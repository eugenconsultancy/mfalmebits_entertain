"""
Custom admin dashboard configuration for django-admin-tools.
Compatible with Django 4.2+
"""

from admin_tools.dashboard import Dashboard, AppIndexDashboard
from admin_tools.dashboard.modules import DashboardModule, Group, AppList, RecentActions, LinkList
from django.urls import reverse  # CHANGED: from django.core.urlresolvers to django.urls
from django.utils.translation import gettext_lazy as _  # CHANGED: updated import

# Custom Welcome Module
class WelcomeModule(DashboardModule):
    """
    Welcome module for the admin dashboard.
    """
    title = 'Welcome'
    template = 'admin_tools/dashboard/modules/welcome.html'
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.description = kwargs.get('description', '')
        self.preferences = {}

    def is_empty(self):
        return False

# Custom Quick Actions Module
class QuickActionsModule(DashboardModule):
    """
    Quick actions module for common admin tasks.
    """
    title = 'Quick Actions'
    template = 'admin_tools/dashboard/modules/quick_actions.html'
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.actions = kwargs.get('actions', [])
        self.preferences = {}

    def is_empty(self):
        return not bool(self.actions)

# Custom Statistics Module
class StatisticsModule(DashboardModule):
    """
    Statistics module showing platform metrics.
    """
    title = 'Platform Statistics'
    template = 'admin_tools/dashboard/modules/statistics.html'
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.stats = kwargs.get('stats', [])
        self.preferences = {}

    def is_empty(self):
        return not bool(self.stats)

class CustomIndexDashboard(Dashboard):
    """
    Custom index dashboard for MfalmeBits admin.
    """
    
    def init_with_context(self, context):
        # Welcome module
        self.children.append(WelcomeModule(
            title='Welcome to MfalmeBits Admin',
            description='Manage your African knowledge platform with our enhanced admin interface.',
        ))
        
        # Quick actions module
        self.children.append(QuickActionsModule(
            title='Quick Actions',
            actions=[
                {
                    'title': 'Add Archive Entry',
                    'url': reverse('admin:archive_archiveentry_add'),
                    'icon': 'fa-archive',
                    'color': 'primary',
                },
                {
                    'title': 'Add Blog Post',
                    'url': reverse('admin:blog_post_add'),
                    'icon': 'fa-newspaper',
                    'color': 'success',
                },
                {
                    'title': 'Add Library Product',
                    'url': reverse('admin:library_product_add'),
                    'icon': 'fa-book',
                    'color': 'info',
                },
                {
                    'title': 'Manage Users',
                    'url': reverse('admin:auth_user_changelist'),
                    'icon': 'fa-users',
                    'color': 'warning',
                },
            ]
        ))
        
        # Statistics module
        self.children.append(StatisticsModule(
            title='Platform Statistics',
            stats=[
                {
                    'label': 'Total Users',
                    'value': 'user_count',
                    'icon': 'fa-users',
                    'color': 'info',
                },
                {
                    'label': 'Archive Entries',
                    'value': 'archive_count',
                    'icon': 'fa-archive',
                    'color': 'primary',
                },
                {
                    'label': 'Blog Posts',
                    'value': 'blog_count',
                    'icon': 'fa-newspaper',
                    'color': 'success',
                },
                {
                    'label': 'Library Products',
                    'value': 'library_count',
                    'icon': 'fa-book',
                    'color': 'accent1',
                },
            ]
        ))
        
        # App list grouped by category
        self.children.append(Group(
            title='Content Management',
            display='tabs',
            children=[
                AppList(
                    title='Archive & Library',
                    models=('apps.archive.*', 'apps.library.*'),
                ),
                AppList(
                    title='Blog & News',
                    models=('apps.blog.*', 'apps.newsletter.*'),
                ),
                AppList(
                    title='Pages & Content',
                    models=('apps.home.*', 'apps.about.*', 'apps.contact.*'),
                ),
            ]
        ))
        
        # Recent actions
        self.children.append(RecentActions(
            title='Recent Actions',
            limit=10,
            include_list=('apps.archive.*', 'apps.blog.*', 'apps.library.*', 'apps.accounts.*'),
        ))
        
        # Links module
        self.children.append(LinkList(
            title='Quick Links',
            children=[
                {
                    'title': 'View Site',
                    'url': '/',
                    'external': False,
                    'attrs': {'target': '_blank', 'class': 'text-primary'},
                },
                {
                    'title': 'Documentation',
                    'url': '#',
                    'external': True,
                },
                {
                    'title': 'Support',
                    'url': '#',
                    'external': True,
                },
            ]
        ))

class CustomAppIndexDashboard(AppIndexDashboard):
    """
    Custom app index dashboard for MfalmeBits admin.
    """
    
    def init_with_context(self, context):
        # Get the app's model classes
        app_models = self.get_app_model_classes()
        
        # Add AppList module
        self.children.append(AppList(
            title=self.app_title,
            models=self.models(),
            css_classes=('applist',),
        ))
        
        # Add RecentActions module
        if app_models:
            self.children.append(RecentActions(
                title='Recent Actions',
                include_list=app_models,
                limit=5,
            ))
    
    def get_app_model_classes(self):
        """Get a list of model class strings for this app."""
        from django.apps import apps
        model_classes = []
        app_label = self.app_label
        
        try:
            app_config = apps.get_app_config(app_label)
            for model in app_config.get_models():
                model_classes.append(f"{app_label}.{model.__name__.lower()}")
        except LookupError:
            pass
        
        return model_classes