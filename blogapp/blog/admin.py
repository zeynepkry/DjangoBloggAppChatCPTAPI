from django.contrib import admin
from .models import Post

class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'is_published')
    list_display_links = ('title',)
    list_filter = ('created_at', 'is_published')
    search_fields = ('title', 'content')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)

    fieldsets = (
        (None, {
            'fields': ('title', 'content', 'excerpt')
        }),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('is_published', 'created_at'),
        }),
    )

admin.site.register(Post, PostAdmin)
