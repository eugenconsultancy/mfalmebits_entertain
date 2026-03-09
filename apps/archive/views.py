from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.utils import timezone
from taggit.models import Tag
from .models import ArchiveEntry, Theme, ArchiveDownload
from utils.seo import SEOMetaGenerator, SEOAnalyzer
from utils.schema import get_article_schema, get_breadcrumb_schema

class ArchiveIndexView(ListView):
    """Main archive listing page"""
    model = ArchiveEntry
    template_name = 'archive/index.html'
    context_object_name = 'entries'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = ArchiveEntry.objects.filter(is_active=True)
        
        # Search
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) |
                Q(content__icontains=q) |
                Q(excerpt__icontains=q) |
                Q(author__icontains=q) |
                Q(tags__name__icontains=q)
            ).distinct()
        
        # Theme filter
        theme = self.request.GET.get('theme')
        if theme:
            queryset = queryset.filter(theme__slug=theme)
        
        # Tag filter
        tag = self.request.GET.get('tag')
        if tag:
            queryset = queryset.filter(tags__slug=tag)
        
        # Date filter
        year = self.request.GET.get('year')
        month = self.request.GET.get('month')
        if year:
            queryset = queryset.filter(published_date__year=year)
            if month:
                queryset = queryset.filter(published_date__month=month)
        
        # Sorting
        sort = self.request.GET.get('sort', '-published_date')
        valid_sorts = ['-published_date', 'published_date', 'title', '-views_count']
        if sort in valid_sorts:
            queryset = queryset.order_by(sort)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get all themes with counts
        context['themes'] = Theme.objects.filter(
            is_active=True,
            archiveentry__is_active=True
        ).annotate(
            entry_count=Count('archiveentry')
        ).filter(entry_count__gt=0)
        
        # Get popular tags
        context['popular_tags'] = Tag.objects.filter(
            archiveentry__is_active=True
        ).annotate(
            entry_count=Count('taggit_taggeditem_items')
        ).order_by('-entry_count')[:20]
        
        # Get archive years for filtering
        context['years'] = ArchiveEntry.objects.filter(
            is_active=True
        ).dates('published_date', 'year', order='DESC')
        
        # Current filters
        context['current_filters'] = {
            'q': self.request.GET.get('q', ''),
            'theme': self.request.GET.get('theme', ''),
            'tag': self.request.GET.get('tag', ''),
            'year': self.request.GET.get('year', ''),
            'month': self.request.GET.get('month', ''),
            'sort': self.request.GET.get('sort', '-published_date'),
        }
        
        # Featured entries
        context['featured_entries'] = ArchiveEntry.objects.filter(
            is_active=True,
            is_featured=True
        )[:6]
        
        # SEO Metadata
        context['seo_title'] = "Knowledge Archive - MfalmeBits"
        context['seo_description'] = "Explore our comprehensive archive of African knowledge, history, culture, and future thinking resources."
        context['seo_keywords'] = "African archive, knowledge base, African history, cultural studies"
        
        return context

class ThemeView(ListView):
    """List entries by theme"""
    model = ArchiveEntry
    template_name = 'archive/theme.html'
    context_object_name = 'entries'
    paginate_by = 12
    
    def get_theme(self):
        return get_object_or_404(Theme, slug=self.kwargs['theme'], is_active=True)
    
    def get_queryset(self):
        return ArchiveEntry.objects.filter(
            theme=self.get_theme(),
            is_active=True
        ).order_by('-published_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        theme = self.get_theme()
        context['theme'] = theme
        
        # SEO Metadata
        context['seo_title'] = SEOMetaGenerator.generate_title(theme)
        context['seo_description'] = SEOMetaGenerator.generate_description(theme)
        context['seo_keywords'] = f"{theme.name}, African knowledge, {theme.name} in Africa"
        
        # Schema
        context['breadcrumb_schema'] = get_breadcrumb_schema([
            {'name': 'Home', 'url': '/'},
            {'name': 'Archive', 'url': '/archive/'},
            {'name': theme.name, 'url': ''},
        ], self.request)
        
        return context

class TagView(ListView):
    """List entries by tag"""
    model = ArchiveEntry
    template_name = 'archive/tag.html'
    context_object_name = 'entries'
    paginate_by = 12
    
    def get_tag(self):
        return get_object_or_404(Tag, slug=self.kwargs['tag'])
    
    def get_queryset(self):
        return ArchiveEntry.objects.filter(
            tags__slug=self.kwargs['tag'],
            is_active=True
        ).order_by('-published_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tag = self.get_tag()
        context['tag'] = tag
        
        # SEO Metadata
        context['seo_title'] = f"Entries tagged with '{tag.name}' - MfalmeBits Archive"
        context['seo_description'] = f"Explore all knowledge entries tagged with {tag.name} in the MfalmeBits archive."
        
        return context

class ArchiveDetailView(DetailView):
    """Individual archive entry detail page"""
    model = ArchiveEntry
    template_name = 'archive/detail.html'
    context_object_name = 'entry'
    slug_url_kwarg = 'entry_slug'
    
    def get_object(self):
        return get_object_or_404(
            ArchiveEntry,
            slug=self.kwargs['entry_slug'],
            theme__slug=self.kwargs['theme'],
            is_active=True
        )
    
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        self.object.increment_views()
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        entry = self.object
        
        # Related entries (by tags or theme)
        related = ArchiveEntry.objects.filter(
            Q(theme=entry.theme) | Q(tags__in=entry.tags.all())
        ).exclude(
            id=entry.id
        ).filter(
            is_active=True
        ).distinct()[:5]
        
        context['related_entries'] = related
        
        # SEO Metadata
        context['seo_title'] = SEOMetaGenerator.generate_title(entry)
        context['seo_description'] = SEOMetaGenerator.generate_description(entry)
        context['seo_keywords'] = SEOMetaGenerator.generate_keywords(entry)
        context['canonical_url'] = entry.get_canonical_url()
        
        # Open Graph
        if entry.featured_image:
            context['og_image'] = self.request.build_absolute_uri(entry.featured_image.url)
        
        # Schema
        context['article_schema'] = get_article_schema(entry, self.request)
        context['breadcrumb_schema'] = get_breadcrumb_schema([
            {'name': 'Home', 'url': '/'},
            {'name': 'Archive', 'url': '/archive/'},
            {'name': entry.theme.name, 'url': entry.theme.get_absolute_url()},
            {'name': entry.title, 'url': ''},
        ], self.request)
        
        # SEO Analysis (for authors/admins)
        if self.request.user.is_staff:
            context['seo_analysis'] = {
                'title': SEOAnalyzer.analyze_title(entry.title),
                'description': SEOAnalyzer.analyze_description(entry.excerpt or entry.content),
                'headings': SEOAnalyzer.analyze_headings(entry.content),
                'readability': SEOAnalyzer.calculate_readability(entry.content),
            }
        
        return context
    
    def post(self, request, *args, **kwargs):
        """Handle document downloads"""
        entry = self.get_object()
        
        if entry.document:
            # Log download
            ArchiveDownload.objects.create(
                entry=entry,
                user=request.user if request.user.is_authenticated else None,
                ip_address=request.META.get('REMOTE_ADDR')
            )
            
            # Increment download count
            entry.download_count += 1
            entry.save(update_fields=['download_count'])
            
            # Return file response
            from django.http import FileResponse
            response = FileResponse(entry.document.open('rb'))
            response['Content-Disposition'] = f'attachment; filename="{entry.document.name}"'
            return response
        
        return self.get(request, *args, **kwargs)
