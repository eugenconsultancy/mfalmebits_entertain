from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import FormView
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Count, Avg
from django.http import JsonResponse, FileResponse, Http404
from django.contrib import messages
from django.urls import reverse
from django.conf import settings
from decimal import Decimal
import stripe
import hashlib
import hmac
import json

from .models import DigitalProduct, ProductCategory, Purchase, Review, Wishlist
from utils.seo import SEOMetaGenerator, SEOAnalyzer
from utils.schema import get_product_schema, get_breadcrumb_schema

class LibraryIndexView(ListView):
    """Main library listing page"""
    model = DigitalProduct
    template_name = 'library/index.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = DigitalProduct.objects.filter(is_active=True)
        
        # Search
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) |
                Q(description__icontains=q) |
                Q(short_description__icontains=q) |
                Q(author__icontains=q) |
                Q(tags__name__icontains=q)
            ).distinct()
        
        # Category filter
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)
        
        # Format filter
        format = self.request.GET.get('format')
        if format:
            queryset = queryset.filter(format=format)
        
        # Price range
        min_price = self.request.GET.get('min_price')
        max_price = self.request.GET.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # Free products
        if self.request.GET.get('free'):
            queryset = queryset.filter(is_free=True)
        
        # On sale
        if self.request.GET.get('sale'):
            queryset = queryset.filter(sale_price__isnull=False, sale_price__lt=models.F('price'))
        
        # Sorting
        sort = self.request.GET.get('sort', '-created_at')
        valid_sorts = ['-created_at', 'created_at', 'title', '-price', 'price', '-purchase_count', '-views_count']
        if sort in valid_sorts:
            queryset = queryset.order_by(sort)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get categories with counts
        context['categories'] = ProductCategory.objects.filter(
            is_active=True,
            digitalproduct__is_active=True
        ).annotate(
            product_count=Count('digitalproduct')
        ).filter(product_count__gt=0)
        
        # Get available formats
        context['formats'] = DigitalProduct.objects.filter(
            is_active=True
        ).values_list('format', flat=True).distinct()
        
        # Featured products
        context['featured_products'] = DigitalProduct.objects.filter(
            is_active=True,
            is_featured=True
        )[:6]
        
        # Current filters
        context['current_filters'] = {
            'q': self.request.GET.get('q', ''),
            'category': self.request.GET.get('category', ''),
            'format': self.request.GET.get('format', ''),
            'min_price': self.request.GET.get('min_price', ''),
            'max_price': self.request.GET.get('max_price', ''),
            'sort': self.request.GET.get('sort', '-created_at'),
        }
        
        # SEO Metadata
        context['seo_title'] = "Digital Library - MfalmeBits"
        context['seo_description'] = "Explore our digital library of eBooks, audiobooks, curriculum kits, and educational resources on African knowledge and culture."
        context['seo_keywords'] = "digital library, eBooks, African books, educational resources, curriculum"
        
        return context

class CategoryView(ListView):
    """Products by category"""
    model = DigitalProduct
    template_name = 'library/category.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_category(self):
        return get_object_or_404(ProductCategory, slug=self.kwargs['slug'], is_active=True)
    
    def get_queryset(self):
        return DigitalProduct.objects.filter(
            category=self.get_category(),
            is_active=True
        ).order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.get_category()
        context['category'] = category
        
        # SEO Metadata
        context['seo_title'] = SEOMetaGenerator.generate_title(category)
        context['seo_description'] = SEOMetaGenerator.generate_description(category)
        
        # Schema
        context['breadcrumb_schema'] = get_breadcrumb_schema([
            {'name': 'Home', 'url': '/'},
            {'name': 'Library', 'url': '/library/'},
            {'name': category.name, 'url': ''},
        ], self.request)
        
        return context

class ProductDetailView(DetailView):
    """Individual product detail page"""
    model = DigitalProduct
    template_name = 'library/detail.html'
    context_object_name = 'product'
    slug_url_kwarg = 'product_slug'
    
    def get_object(self):
        return get_object_or_404(
            DigitalProduct,
            slug=self.kwargs['product_slug'],
            category__slug=self.kwargs['category'],
            is_active=True
        )
    
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        self.object.increment_views()
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.object
        
        # Related products
        context['related_products'] = DigitalProduct.objects.filter(
            Q(category=product.category) | Q(tags__in=product.tags.all())
        ).exclude(
            id=product.id
        ).filter(
            is_active=True
        ).distinct()[:4]
        
        # Reviews
        context['reviews'] = product.reviews.filter(is_approved=True)
        context['average_rating'] = product.reviews.filter(
            is_approved=True
        ).aggregate(Avg('rating'))['rating__avg'] or 0
        
        # Check if user has purchased
        if self.request.user.is_authenticated:
            context['has_purchased'] = Purchase.objects.filter(
                user=self.request.user,
                product=product,
                status='completed'
            ).exists()
            context['in_wishlist'] = Wishlist.objects.filter(
                user=self.request.user,
                product=product
            ).exists()
        
        # SEO Metadata
        context['seo_title'] = SEOMetaGenerator.generate_title(product)
        context['seo_description'] = SEOMetaGenerator.generate_description(product)
        context['seo_keywords'] = SEOMetaGenerator.generate_keywords(product)
        
        # Open Graph
        if product.cover_image:
            context['og_image'] = self.request.build_absolute_uri(product.cover_image.url)
        
        # Schema
        context['product_schema'] = get_product_schema(product, self.request)
        context['breadcrumb_schema'] = get_breadcrumb_schema([
            {'name': 'Home', 'url': '/'},
            {'name': 'Library', 'url': '/library/'},
            {'name': product.category.name, 'url': product.category.get_absolute_url()},
            {'name': product.title, 'url': ''},
        ], self.request)
        
        # Stripe configuration
        context['stripe_public_key'] = settings.STRIPE_PUBLIC_KEY
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle AJAX requests for adding to cart/wishlist"""
        product = self.get_object()
        action = request.POST.get('action')
        
        if action == 'add_to_wishlist' and request.user.is_authenticated:
            wishlist, created = Wishlist.objects.get_or_create(
                user=request.user,
                product=product
            )
            return JsonResponse({'success': True, 'in_wishlist': True})
        
        elif action == 'remove_from_wishlist' and request.user.is_authenticated:
            Wishlist.objects.filter(user=request.user, product=product).delete()
            return JsonResponse({'success': True, 'in_wishlist': False})
        
        return JsonResponse({'success': False, 'error': 'Invalid action'})

class CheckoutView(LoginRequiredMixin, TemplateView):
    """Checkout page"""
    template_name = 'library/checkout.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get cart from session
        cart = self.request.session.get('cart', {})
        product_ids = [int(pid) for pid in cart.keys()]
        
        products = DigitalProduct.objects.filter(id__in=product_ids, is_active=True)
        total = sum(product.get_current_price() * cart[str(product.id)] for product in products)
        
        context['products'] = products
        context['cart'] = cart
        context['total'] = total
        context['stripe_public_key'] = settings.STRIPE_PUBLIC_KEY
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Process payment"""
        try:
            # Get cart total
            cart = request.session.get('cart', {})
            product_ids = [int(pid) for pid in cart.keys()]
            products = DigitalProduct.objects.filter(id__in=product_ids, is_active=True)
            total = sum(product.get_current_price() * cart[str(product.id)] for product in products)
            
            # Create Stripe payment intent
            stripe.api_key = settings.STRIPE_SECRET_KEY
            intent = stripe.PaymentIntent.create(
                amount=int(total * 100),  # Convert to cents
                currency='usd',
                metadata={
                    'user_id': request.user.id,
                    'products': ','.join(str(p.id) for p in products)
                }
            )
            
            return JsonResponse({
                'clientSecret': intent.client_secret
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

class PaymentSuccessView(LoginRequiredMixin, TemplateView):
    """Payment success page"""
    template_name = 'library/success.html'
    
    def get(self, request, *args, **kwargs):
        payment_intent_id = request.GET.get('payment_intent')
        
        if payment_intent_id:
            # Verify payment with Stripe
            stripe.api_key = settings.STRIPE_SECRET_KEY
            try:
                intent = stripe.PaymentIntent.retrieve(payment_intent_id)
                
                if intent.status == 'succeeded':
                    # Create purchase records
                    cart = request.session.get('cart', {})
                    product_ids = [int(pid) for pid in cart.keys()]
                    products = DigitalProduct.objects.filter(id__in=product_ids)
                    
                    for product in products:
                        Purchase.objects.create(
                            user=request.user,
                            product=product,
                            transaction_id=payment_intent_id,
                            amount=product.get_current_price(),
                            status='completed',
                            payment_method='stripe'
                        )
                        product.purchase_count += 1
                        product.save(update_fields=['purchase_count'])
                    
                    # Clear cart
                    request.session['cart'] = {}
                    
                    messages.success(request, 'Payment successful! Your downloads are now available.')
                    
            except Exception as e:
                messages.error(request, f'Error verifying payment: {str(e)}')
        
        return super().get(request, *args, **kwargs)

class DownloadView(LoginRequiredMixin, DetailView):
    """Handle product downloads"""
    model = DigitalProduct
    
    def get(self, request, *args, **kwargs):
        product = self.get_object()
        
        # Check if user has purchased
        purchase = Purchase.objects.filter(
            user=request.user,
            product=product,
            status='completed'
        ).first()
        
        if not purchase:
            raise Http404("You haven't purchased this product")
        
        # Check download limit
        if not purchase.can_download():
            messages.error(request, 'Download limit reached')
            return redirect('library:detail', category=product.category.slug, product_slug=product.slug)
        
        # Get requested file
        file_id = request.GET.get('file')
        if file_id and product.files.exists():
            file_obj = product.files.filter(id=file_id).first()
            if file_obj:
                # Update download count
                purchase.download_count += 1
                purchase.last_download = timezone.now()
                purchase.save(update_fields=['download_count', 'last_download'])
                
                # Return file
                response = FileResponse(file_obj.file.open('rb'))
                response['Content-Disposition'] = f'attachment; filename="{file_obj.file.name}"'
                return response
        
        # Return main file
        if product.files.exists():
            file_obj = product.files.first()
        else:
            raise Http404("No files available for download")
        
        # Update download count
        purchase.download_count += 1
        purchase.last_download = timezone.now()
        purchase.save(update_fields=['download_count', 'last_download'])
        
        response = FileResponse(file_obj.file.open('rb'))
        response['Content-Disposition'] = f'attachment; filename="{file_obj.file.name}"'
        return response

class AddReviewView(LoginRequiredMixin, FormView):
    """Add product review"""
    
    def post(self, request, *args, **kwargs):
        product = get_object_or_404(DigitalProduct, slug=kwargs['product_slug'])
        
        # Check if user has purchased
        has_purchased = Purchase.objects.filter(
            user=request.user,
            product=product,
            status='completed'
        ).exists()
        
        # Create or update review
        review, created = Review.objects.update_or_create(
            product=product,
            user=request.user,
            defaults={
                'rating': request.POST.get('rating'),
                'title': request.POST.get('title', ''),
                'comment': request.POST.get('comment'),
                'verified_purchase': has_purchased
            }
        )
        
        messages.success(request, 'Review submitted successfully!')
        return redirect('library:detail', category=product.category.slug, product_slug=product.slug)
