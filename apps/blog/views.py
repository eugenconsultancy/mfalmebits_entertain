from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import FormView, CreateView
from django.shortcuts import get_object_or_404, redirect
from django.db.models import Q, Count
from django.http import JsonResponse, Http404
from django.contrib import messages
from django.core.paginator import Paginator
from django.utils import timezone
from django.urls import reverse
from taggit.models import Tag
from .models import Post, Category, Comment, Series, Author, NewsletterSubscription
from .forms import CommentForm, NewsletterForm, SearchForm
from utils.seo import SEOMetaGenerator, SEOAnalyzer
from utils.schema import get_article_schema, get_breadcrumb_schema
import logging

logger = logging.getLogger(__name__)

class BlogIndexView(ListView):
    """Main blog listing page"""
    model = Post
    template_name = 'blog/index.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Post.objects.filter(
            status='published',
            is_active=True
        ).select_related('author', 'category')
        
        # Search
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) |
                Q(content__icontains=q) |
                Q(excerpt__icontains=q) |
                Q(tags__name__icontains=q)
            ).distinct()
        
        # Category filter
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)
        
        # Tag filter
        tag = self.request.GET.get('tag')
        if tag:
            queryset = queryset.filter(tags__slug=tag)
        
        # Author filter
        author = self.request.GET.get('author')
        if author:
            queryset = queryset.filter(author__username=author)
        
        # Date filters
        year = self.request.GET.get('year')
        month = self.request.GET.get('month')
        if year:
            queryset = queryset.filter(published_date__year=year)
            if month:
                queryset = queryset.filter(published_date__month=month)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get featured posts
        context['featured_posts'] = Post.objects.filter(
            status='published',
            is_active=True,
            is_featured=True
        )[:3]
        
        # Get categories with counts
        context['categories'] = Category.objects.filter(
            is_active=True,
            post__status='published'
        ).annotate(
            post_count=Count('post')
        ).filter(post_count__gt=0)
        
        # Get popular tags
        context['popular_tags'] = Tag.objects.filter(
            post__status='published'
        ).annotate(
            post_count=Count('taggit_taggeditem_items')
        ).order_by('-post_count')[:20]
        
        # Get archive years
        context['years'] = Post.objects.filter(
            status='published'
        ).dates('published_date', 'year', order='DESC')
        
        # Get popular posts
        context['popular_posts'] = Post.objects.filter(
            status='published',
            is_active=True
        ).order_by('-views_count')[:5]
        
        # Current filters
        context['current_filters'] = {
            'q': self.request.GET.get('q', ''),
            'category': self.request.GET.get('category', ''),
            'tag': self.request.GET.get('tag', ''),
            'author': self.request.GET.get('author', ''),
            'year': self.request.GET.get('year', ''),
            'month': self.request.GET.get('month', ''),
        }
        
        # Search form
        context['search_form'] = SearchForm(initial={'q': context['current_filters']['q']})
        
        # Newsletter form
        context['newsletter_form'] = NewsletterForm()
        
        # SEO Metadata
        context['seo_title'] = "Blog - MfalmeBits"
        context['seo_description'] = "Latest news, updates, and insights from MfalmeBits about African knowledge, culture, and digital innovation."
        context['seo_keywords'] = "African blog, news, updates, African knowledge, insights"
        
        return context


class PostDetailView(DetailView):
    """Individual blog post detail page"""
    model = Post
    template_name = 'blog/detail.html'
    context_object_name = 'post'
    
    def get_queryset(self):
        return Post.objects.filter(
            status='published',
            is_active=True
        ).select_related('author', 'category')
    
    def get_object(self):
        post = super().get_object()
        
        # Check if post is published
        if post.status != 'published' and not self.request.user.is_staff:
            raise Http404("Post not found")
        
        return post
    
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        self.object.increment_views()
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object
        
        # Get approved comments
        context['comments'] = post.comments.filter(
            is_approved=True,
            parent__isnull=True
        ).select_related('parent')
        
        # Comment form
        context['comment_form'] = CommentForm()
        
        # Related posts (by tags or category)
        related = Post.objects.filter(
            Q(category=post.category) | Q(tags__in=post.tags.all())
        ).exclude(
            id=post.id
        ).filter(
            status='published',
            is_active=True
        ).distinct()[:3]
        
        context['related_posts'] = related
        
        # Previous/Next posts
        context['previous_post'] = post.get_previous_post()
        context['next_post'] = post.get_next_post()
        
        # SEO Metadata
        context['seo_title'] = SEOMetaGenerator.generate_title(post)
        context['seo_description'] = SEOMetaGenerator.generate_description(post)
        context['seo_keywords'] = SEOMetaGenerator.generate_keywords(post)
        context['canonical_url'] = post.get_canonical_url()
        
        # Open Graph
        if post.featured_image:
            context['og_image'] = self.request.build_absolute_uri(post.featured_image.url)
        
        # Schema
        context['article_schema'] = get_article_schema(post, self.request)
        context['breadcrumb_schema'] = get_breadcrumb_schema([
            {'name': 'Home', 'url': '/'},
            {'name': 'Blog', 'url': '/blog/'},
            {'name': post.category.name, 'url': post.category.get_absolute_url()},
            {'name': post.title, 'url': ''},
        ], self.request)
        
        return context


class CategoryView(ListView):
    """Posts by category"""
    model = Post
    template_name = 'blog/category.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_category(self):
        return get_object_or_404(Category, slug=self.kwargs['slug'], is_active=True)
    
    def get_queryset(self):
        return Post.objects.filter(
            category=self.get_category(),
            status='published',
            is_active=True
        ).order_by('-published_date')
    
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
            {'name': 'Blog', 'url': '/blog/'},
            {'name': category.name, 'url': ''},
        ], self.request)
        
        return context


class TagView(ListView):
    """Posts by tag"""
    model = Post
    template_name = 'blog/tag.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_tag(self):
        return get_object_or_404(Tag, slug=self.kwargs['slug'])
    
    def get_queryset(self):
        return Post.objects.filter(
            tags__slug=self.kwargs['slug'],
            status='published',
            is_active=True
        ).order_by('-published_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tag = self.get_tag()
        context['tag'] = tag
        
        # SEO Metadata
        context['seo_title'] = f"Posts tagged with '{tag.name}' - MfalmeBits Blog"
        context['seo_description'] = f"Read all blog posts tagged with {tag.name} on MfalmeBits"
        
        return context


class AuthorView(ListView):
    """Posts by author"""
    model = Post
    template_name = 'blog/author.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_author(self):
        return get_object_or_404(Author, user__username=self.kwargs['username'])
    
    def get_queryset(self):
        return Post.objects.filter(
            author=self.get_author().user,
            status='published',
            is_active=True
        ).order_by('-published_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        author = self.get_author()
        context['author'] = author
        
        # SEO Metadata
        context['seo_title'] = f"Posts by {author.user.get_full_name()} - MfalmeBits Blog"
        context['seo_description'] = f"Read all blog posts by {author.user.get_full_name()} on MfalmeBits"
        
        return context


class SeriesView(ListView):
    """Posts in a series"""
    model = Post
    template_name = 'blog/series.html'
    context_object_name = 'posts'
    
    def get_series(self):
        return get_object_or_404(Series, slug=self.kwargs['slug'], is_active=True)
    
    def get_queryset(self):
        series = self.get_series()
        return series.posts.filter(
            status='published',
            is_active=True
        ).order_by('published_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['series'] = self.get_series()
        return context


class CommentCreateView(CreateView):
    """Handle comment submissions"""
    model = Comment
    form_class = CommentForm
    
    def form_valid(self, form):
        # Get the post
        post = get_object_or_404(Post, slug=self.kwargs['slug'])
        
        # Save comment
        comment = form.save(commit=False)
        comment.post = post
        
        # Handle parent comment
        parent_id = self.request.POST.get('parent')
        if parent_id:
            try:
                parent = Comment.objects.get(id=parent_id, post=post)
                comment.parent = parent
            except Comment.DoesNotExist:
                pass
        
        # Capture metadata
        comment.ip_address = self.request.META.get('REMOTE_ADDR')
        comment.user_agent = self.request.META.get('HTTP_USER_AGENT', '')[:200]
        
        # Auto-approve if setting allows
        from .models import BlogSettings
        settings = BlogSettings.objects.first()
        if settings and not settings.moderate_comments:
            comment.is_approved = True
        
        comment.save()
        
        # Send notification
        if settings and settings.notify_on_comments:
            self.send_notification(comment)
        
        messages.success(self.request, 'Your comment has been submitted and is awaiting moderation.')
        
        return redirect(post.get_absolute_url() + '#comments')
    
    def form_invalid(self, form):
        messages.error(self.request, 'There was an error with your comment. Please check the form.')
        return redirect(self.request.META.get('HTTP_REFERER', '/'))
    
    def send_notification(self, comment):
        """Send email notification about new comment"""
        try:
            from django.core.mail import send_mail
            from django.conf import settings
            
            subject = f'New Comment on {comment.post.title}'
            message = f"""
            New comment on "{comment.post.title}"
            
            Name: {comment.name}
            Email: {comment.email}
            
            Comment:
            {comment.content}
            
            Approve or moderate: {self.request.build_absolute_uri('/admin/blog/comment/')}
            """
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.COMMENT_NOTIFICATION_EMAIL or settings.DEFAULT_FROM_EMAIL],
                fail_silently=True,
            )
        except Exception as e:
            logger.error(f"Failed to send comment notification: {e}")


class NewsletterSubscribeView(FormView):
    """Handle newsletter subscriptions"""
    form_class = NewsletterForm
    
    def form_valid(self, form):
        email = form.cleaned_data['email']
        first_name = form.cleaned_data.get('first_name', '')
        
        # Create or update subscription
        sub, created = NewsletterSubscription.objects.get_or_create(
            email=email,
            defaults={
                'first_name': first_name,
                'ip_address': self.request.META.get('REMOTE_ADDR'),
                'source': 'blog'
            }
        )
        
        if not created and not sub.is_active:
            sub.is_active = True
            sub.first_name = first_name or sub.first_name
            sub.save()
        
        if created:
            message = 'Thank you for subscribing to our newsletter!'
        else:
            message = 'You are already subscribed to our newsletter.'
        
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': message})
        
        messages.success(self.request, message)
        return redirect(self.request.META.get('HTTP_REFERER', '/'))
    
    def form_invalid(self, form):
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)
        
        messages.error(self.request, 'Please enter a valid email address.')
        return redirect(self.request.META.get('HTTP_REFERER', '/'))


class NewsletterUnsubscribeView(TemplateView):
    """Handle newsletter unsubscriptions"""
    template_name = 'blog/unsubscribe.html'
    
    def get(self, request, *args, **kwargs):
        email = request.GET.get('email')
        token = request.GET.get('token')
        
        # Simple token verification (in production, use proper token)
        if email and token:
            try:
                sub = NewsletterSubscription.objects.get(email=email, is_active=True)
                sub.is_active = False
                sub.unsubscribed_at = timezone.now()
                sub.save()
                
                messages.success(request, 'You have been unsubscribed successfully.')
            except NewsletterSubscription.DoesNotExist:
                messages.error(request, 'Subscription not found.')
        
        return super().get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['seo_title'] = "Unsubscribe from Newsletter - MfalmeBits"
        return context


class ArchiveView(ListView):
    """Archive view by year/month"""
    model = Post
    template_name = 'blog/archive.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        year = self.kwargs.get('year')
        month = self.kwargs.get('month')
        
        queryset = Post.objects.filter(
            status='published',
            is_active=True
        )
        
        if year:
            queryset = queryset.filter(published_date__year=year)
        if month:
            queryset = queryset.filter(published_date__month=month)
        
        return queryset.order_by('-published_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        context['archive_year'] = self.kwargs.get('year')
        context['archive_month'] = self.kwargs.get('month')
        
        # Get month name
        if context['archive_month']:
            import calendar
            context['month_name'] = calendar.month_name[int(context['archive_month'])]
        
        # SEO Metadata
        if context['archive_year']:
            if context['archive_month']:
                context['seo_title'] = f"Blog Archive: {context['month_name']} {context['archive_year']}"
            else:
                context['seo_title'] = f"Blog Archive: {context['archive_year']}"
        
        return context
