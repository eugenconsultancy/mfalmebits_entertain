from django.views.generic import TemplateView, DetailView, ListView
from django.shortcuts import get_object_or_404
from .models import (
    AboutSection, TeamMember, Timeline, 
    Achievement, Value, Partner, Testimonial, 
    AboutSettings
)
from utils.seo import SEOMetaGenerator
from utils.schema import get_breadcrumb_schema, get_organization_schema

class AboutIndexView(TemplateView):
    """Main about page"""
    template_name = 'about/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get settings
        context['settings'] = AboutSettings.objects.first()
        
        # Get active sections
        context['sections'] = AboutSection.objects.filter(is_active=True)
        
        # Get team members
        context['team_leadership'] = TeamMember.objects.filter(
            is_active=True, is_leadership=True
        )
        context['team_founders'] = TeamMember.objects.filter(
            is_active=True, is_founder=True
        )
        context['team_members'] = TeamMember.objects.filter(
            is_active=True, is_leadership=False, is_founder=False
        )
        
        # Get timeline
        context['timeline'] = Timeline.objects.filter(is_active=True)
        
        # Get achievements
        context['achievements'] = Achievement.objects.filter(is_active=True)
        
        # Get values
        context['values'] = Value.objects.filter(is_active=True)
        
        # Get partners
        context['partners'] = Partner.objects.filter(is_active=True)
        
        # Get testimonials
        context['testimonials'] = Testimonial.objects.filter(is_active=True)
        
        # SEO Metadata
        if context['settings']:
            context['seo_title'] = context['settings'].meta_title or "About Us - MfalmeBits"
            context['seo_description'] = context['settings'].meta_description or "Learn about MfalmeBits, our mission to preserve and share African knowledge, and the team behind it."
            context['seo_keywords'] = context['settings'].meta_keywords or "about us, mission, team, African knowledge, cultural preservation"
        else:
            context['seo_title'] = "About Us - MfalmeBits"
            context['seo_description'] = "Learn about MfalmeBits, our mission to preserve and share African knowledge, and the team behind it."
            context['seo_keywords'] = "about us, mission, team, African knowledge, cultural preservation"
        
        # Schema
        context['breadcrumb_schema'] = get_breadcrumb_schema([
            {'name': 'Home', 'url': '/'},
            {'name': 'About', 'url': ''},
        ], self.request)
        
        context['organization_schema'] = get_organization_schema(self.request)
        
        return context


class TeamDetailView(DetailView):
    """Individual team member detail"""
    model = TeamMember
    template_name = 'about/team_detail.html'
    context_object_name = 'member'
    slug_url_kwarg = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get other team members
        context['other_members'] = TeamMember.objects.filter(
            is_active=True
        ).exclude(id=self.object.id)[:4]
        
        # SEO Metadata
        context['seo_title'] = f"{self.object.name} - {self.object.position} | MfalmeBits Team"
        context['seo_description'] = f"Learn about {self.object.name}, {self.object.position} at MfalmeBits."
        
        return context


class TeamListView(ListView):
    """Team listing page"""
    model = TeamMember
    template_name = 'about/team.html'
    context_object_name = 'team_members'
    
    def get_queryset(self):
        return TeamMember.objects.filter(is_active=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Group team members
        context['founders'] = self.get_queryset().filter(is_founder=True)
        context['leadership'] = self.get_queryset().filter(is_leadership=True, is_founder=False)
        context['members'] = self.get_queryset().filter(is_leadership=False, is_founder=False)
        
        context['seo_title'] = "Our Team - MfalmeBits"
        context['seo_description'] = "Meet the dedicated team behind MfalmeBits working to preserve and share African knowledge."
        
        return context


class TimelineView(ListView):
    """Timeline/history page"""
    model = Timeline
    template_name = 'about/timeline.html'
    context_object_name = 'timeline'
    
    def get_queryset(self):
        return Timeline.objects.filter(is_active=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['seo_title'] = "Our History - MfalmeBits"
        context['seo_description'] = "Explore the journey and history of MfalmeBits from our founding to today."
        return context


class ValuesView(ListView):
    """Core values page"""
    model = Value
    template_name = 'about/values.html'
    context_object_name = 'values'
    
    def get_queryset(self):
        return Value.objects.filter(is_active=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['seo_title'] = "Our Values - MfalmeBits"
        context['seo_description'] = "Discover the core values that guide MfalmeBits in our mission to preserve and share African knowledge."
        return context


class PartnersView(ListView):
    """Partners page"""
    model = Partner
    template_name = 'about/partners.html'
    context_object_name = 'partners'
    
    def get_queryset(self):
        return Partner.objects.filter(is_active=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Group partners by type
        partners_by_type = {}
        for partner in self.get_queryset():
            if partner.partner_type not in partners_by_type:
                partners_by_type[partner.partner_type] = []
            partners_by_type[partner.partner_type].append(partner)
        
        context['partners_by_type'] = partners_by_type
        context['seo_title'] = "Our Partners - MfalmeBits"
        context['seo_description'] = "Meet the organizations and institutions partnering with MfalmeBits to preserve and share African knowledge."
        
        return context
