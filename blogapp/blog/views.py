from django.http.response import HttpResponse
from django.shortcuts import render
from django.shortcuts import render, get_object_or_404
from .models import Post

# Create your views here.
def index(req):
    posts = Post.objects.all()
    return render(req, 'blog/index.html', {'posts': posts})

def blogs(req):
    posts = Post.objects.all()
    return render(req, 'blog/blogs.html', {'posts': posts})
def blog_details(req, id):
    post = get_object_or_404(Post, id=id)
    return render(req, 'blog/blog_details.html', {'post': post})