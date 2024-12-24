from django.contrib import admin
from django.conf import settings
import os
from django.urls import path
from django.shortcuts import redirect
from django.core.cache import cache  # Cache for storing the interval
from django.http import HttpResponseRedirect
from .models import Post, CSVProgress, Category
import subprocess  # To run Celery commands
from blogapp.celery import app as celery_app

CELERY_PID_FILE = os.path.join(settings.BASE_DIR, "celery_pids.txt")

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'is_published', 'is_archived')
    list_display_links = ('title',)
    list_filter = ('created_at', 'is_published', 'is_archived')
    search_fields = ('title', 'content')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {
            'fields': ('title', 'content', 'excerpt')
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('is_published', 'is_archived', 'created_at'),
        }),
    )

    actions = ['archive_posts', 'restore_posts']

    def archive_posts(self, request, queryset):
        queryset.update(is_archived=True)
        self.message_user(request, "Selected posts have been archived.")
    archive_posts.short_description = "Archive selected posts"

    def restore_posts(self, request, queryset):
        queryset.update(is_archived=False)
        self.message_user(request, "Selected posts have been restored from the archive.")
    restore_posts.short_description = "Restore selected posts from archive"

    change_list_template = "blog/change_list.html"

    # Custom start, stop Celery, and set interval actions
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('start_worker_and_beat/', self.admin_site.admin_view(self.start_celery_worker_and_beat), name='blog_post_start_worker_and_beat'),
            path('stop_worker_and_beat/', self.admin_site.admin_view(self.stop_celery_worker_and_beat), name='blog_post_stop_worker_and_beat'),
            path('set_interval/', self.admin_site.admin_view(self.set_interval), name='blog_post_set_interval'),
        ]
        return custom_urls + urls

    def start_celery_worker_and_beat(self, request):
        worker_process = subprocess.Popen(["/home/ubuntu/djangoAI/myenv/bin/celery", "-A", "blogapp", "worker", "-l", "info"])
        beat_process = subprocess.Popen(["/home/ubuntu/djangoAI/myenv/bin/celery", "-A", "blogapp", "beat", "-l", "info"])
        
        with open(CELERY_PID_FILE, "w") as f:
            f.write(f"{worker_process.pid}\n{beat_process.pid}\n")
        
        self.message_user(request, "Celery Worker and Beat started.")
        return redirect("..")

    def stop_celery_worker_and_beat(self, request):
        try:
            with open(CELERY_PID_FILE, "r") as f:
                pids = f.readlines()
            
            for pid in pids:
                os.kill(int(pid.strip()), 9)
            
            os.remove(CELERY_PID_FILE)
            self.message_user(request, "Celery Worker and Beat stopped.")
        except FileNotFoundError:
            self.message_user(request, "No running Celery processes found.")
        except Exception as e:
            self.message_user(request, f"Error stopping Celery processes: {str(e)}")
        
        return redirect("..")

    def set_interval(self, request):
        if request.method == 'POST':
            interval_hours = int(request.POST.get('interval_hours', 1))

            # Update Celery Beat schedule dynamically
            celery_app.conf.beat_schedule = {
                'generate_blog_posts_from_reddit_excel': {
                    'task': 'blogapp.tasks.generate_blog_posts_from_reddit_excel',
                    'schedule': interval_hours * 3600,  # Convert hours to seconds
                },
            }
            celery_app.conf.timezone = 'UTC'

            # Store the interval in cache for persistence
            cache.set('celery_interval_hours', interval_hours)

            self.message_user(request, f"Interval set to {interval_hours} hours.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        

admin.site.register(Post, PostAdmin)
admin.site.register(CSVProgress)
admin.site.register(Category)


# from django.contrib import admin
# from django.urls import path
# from django.shortcuts import redirect, get_object_or_404
# from .models import Post, CSVProgress, Category

# class PostAdmin(admin.ModelAdmin):
#     list_display = ('title', 'created_at', 'is_published', 'is_archived')  # Display is_archived status
#     list_display_links = ('title',)
#     list_filter = ('created_at', 'is_published', 'is_archived')  # Filter by archive status
#     search_fields = ('title', 'content')
#     date_hierarchy = 'created_at'
#     readonly_fields = ('created_at',)
#     fieldsets = (
#         (None, {
#             'fields': ('title', 'content', 'excerpt')
#         }),
#         ('Advanced options', {
#             'classes': ('collapse',),
#             'fields': ('is_published', 'is_archived', 'created_at'),  # Add is_archived field
#         }),
#     )

#     # Custom archive and restore actions
#     actions = ['archive_posts', 'restore_posts']

#     def archive_posts(self, request, queryset):
#         queryset.update(is_archived=True)  # Set is_archived to True for selected posts
#         self.message_user(request, "Selected posts have been archived.")
#     archive_posts.short_description = "Archive selected posts"

#     def restore_posts(self, request, queryset):
#         queryset.update(is_archived=False)  # Set is_archived to False to restore posts
#         self.message_user(request, "Selected posts have been restored from the archive.")
#     restore_posts.short_description = "Restore selected posts from archive"

#     # Override the get_urls method to redirect the Add button
#     def get_urls(self):
#         urls = super().get_urls()
#         custom_urls = [
#             path('add/', self.custom_add_view),
#         ]
#         return custom_urls + urls

#     # Custom view to handle the redirection for Add
#     def custom_add_view(self, request):
#         return redirect('create_post')

#     # Override the change_view to redirect the Change button to the custom update_post view
#     def change_view(self, request, object_id, form_url='', extra_context=None):
#         post = get_object_or_404(Post, pk=object_id)
#         return redirect('update_post', id=post.id)

# # Register the Post model with the customized PostAdmin
# admin.site.register(Post, PostAdmin)
# admin.site.register(CSVProgress)
# admin.site.register(Category)

