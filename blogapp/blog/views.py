from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Post

def index(req):
    posts = Post.objects.all()
    return render(req, 'blog/index.html', {'posts': posts})

def blogs(req):
    posts = Post.objects.all()
    return render(req, 'blog/blogs.html', {'posts': posts})

def blog_details(req, id):
    post = get_object_or_404(Post, id=id)
    return render(req, 'blog/details.html', {'post': post})

def create_post(req):
    if req.method == "POST":
        title = req.POST.get('title')
        content = req.POST.get('content')
        post = Post.objects.create(title=title, content=content)
        return redirect('blog_details', id=post.id)
    return render(req, 'blog/create_post.html')

def update_post(req, id):
    post = get_object_or_404(Post, id=id)
    if req.method == "POST":
        post.title = req.POST.get('title')
        post.content = req.POST.get('content')
        post.save()
        return redirect('blog_details', id=post.id)
    return render(req, 'blog/update_post.html', {'post': post})

def delete_post(req, id):
    post = get_object_or_404(Post, id=id)
    if req.method == "POST":
        post.delete()
        return redirect('blogs')
    return render(req, 'blog/confirm_delete.html', {'post': post})
