from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("index/", views.index, name ="index"),
    path("blogs/", views.blogs, name="blogs"),
    path("blogs/<int:id>/", views.blog_details, name="blog_details"),
]
