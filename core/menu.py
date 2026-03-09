"""
Custom admin menu configuration for django-admin-tools.
Compatible with Django 4.2+
"""

from admin_tools.menu import Menu, Item, AppListMenuItem
from django.urls import reverse  # CHANGED: from django.core.urlresolvers to django.urls
from django.utils.translation import gettext_lazy as _  # CHANGED: updated import

class CustomMenu(Menu):
    """
    Custom menu for MfalmeBits admin interface.
    """
    
    def init_with_context(self, context):
        # Get site name for URL reversing
        site_name = context.get('site_name', 'admin')
        
        # Dashboard item
        self.children.append(Item(
            title='Dashboard',
            url=reverse('admin:index'),
            icon='fa-dashboard',
            css_class='text-primary',
        ))
        
        # Content Management section
        content_menu = Item(
            title='Content',
            icon='fa-file-text',
            css_class='text-success',
        )
        
        content_menu.children.append(AppListMenuItem(
            title='Archive',
            app_label='archive',
            icon='fa-archive',
        ))
        
        content_menu.children.append(AppListMenuItem(
            title='Blog',
            app_label='blog',
            icon='fa-newspaper',
        ))
        
        content_menu.children.append(AppListMenuItem(
            title='Library',
            app_label='library',
            icon='fa-book',
        ))
        
        content_menu.children.append(AppListMenuItem(
            title='Pages',
            app_label='home',
            icon='fa-file',
        ))
        
        self.children.append(content_menu)
        
        # User Management section
        users_menu = Item(
            title='Users',
            icon='fa-users',
            css_class='text-info',
        )
        
        users_menu.children.append(AppListMenuItem(
            title='All Users',
            app_label='auth',
            icon='fa-user',
        ))
        
        users_menu.children.append(AppListMenuItem(
            title='Accounts',
            app_label='accounts',
            icon='fa-id-card',
        ))
        
        users_menu.children.append(AppListMenuItem(
            title='Groups',
            app_label='auth',
            model='group',
            icon='fa-group',
        ))
        
        self.children.append(users_menu)
        
        # Commerce section
        commerce_menu = Item(
            title='Commerce',
            icon='fa-shopping-cart',
            css_class='text-warning',
        )
        
        commerce_menu.children.append(AppListMenuItem(
            title='Orders',
            app_label='payments',
            icon='fa-credit-card',
        ))
        
        commerce_menu.children.append(AppListMenuItem(
            title='Products',
            app_label='library',
            model='product',
            icon='fa-cube',
        ))
        
        self.children.append(commerce_menu)
        
        # System section
        system_menu = Item(
            title='System',
            icon='fa-cog',
            css_class='text-secondary',
        )
        
        system_menu.children.append(AppListMenuItem(
            title='Settings',
            app_label='sites',
            icon='fa-globe',
        ))
        
        system_menu.children.append(AppListMenuItem(
            title='Tasks',
            app_label='django_celery_beat',
            icon='fa-clock-o',
        ))
        
        system_menu.children.append(Item(
            title='Logs',
            url='#',
            icon='fa-history',
        ))
        
        self.children.append(system_menu)
        
        # Quick actions (right side)
        self.children.append(Item(
            title='Add Archive Entry',
            url=reverse('admin:archive_archiveentry_add'),
            icon='fa-plus-circle',
            css_class='text-success float-right',
        ))
        
        self.children.append(Item(
            title='Add Blog Post',
            url=reverse('admin:blog_post_add'),
            icon='fa-plus-circle',
            css_class='text-info float-right',
        ))