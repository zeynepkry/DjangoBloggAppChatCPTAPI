from django.urls import path
from . import views
from .views import robots_txt
from django.contrib.sitemaps.views import sitemap
from .sitemaps import BlogSitemap

sitemaps = {
    'blogs': BlogSitemap,
}
urlpatterns = [
    path("", views.blogs, name="home"),  # This makes /blogs the main page
    path("blogs/", views.blogs, name="blogs"),
    path("category/<int:category_id>/", views.blogs, name="blogs_by_category"),
    path("post/<int:id>/", views.blog_details, name="blog_details"),
    path("create/", views.create_post, name="create_post"),
    path("update/<int:id>/", views.update_post, name="update_post"),
    path("delete/<int:id>/", views.delete_post, name="delete_post"),
    path("chatgpt/", views.chatgpt, name="chatgpt"),
    path("robots.txt", robots_txt, name="robots_txt"),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    
]

