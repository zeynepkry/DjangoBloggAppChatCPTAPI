from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("index/", views.index, name="index"),
    path("blogs/", views.blogs, name="blogs"),
    path("category/<int:category_id>/", views.blogs, name="blogs_by_category"),
    path("post/<int:id>/", views.blog_details, name="blog_details"),
    path("create/", views.create_post, name="create_post"),
    path("update/<int:id>/", views.update_post, name="update_post"),
    path("delete/<int:id>/", views.delete_post, name="delete_post"),
    path("chatgpt/", views.chatgpt, name="chatgpt"),
]
