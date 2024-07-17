from django.shortcuts import render, redirect, get_object_or_404
from .models import Post, Category
from .utils import get_chatgpt_response

def index(req):
    categories = Category.objects.all()
    posts = Post.objects.all()
    response = None
    if req.method == 'POST':
        prompt = req.POST.get('prompt')
        if prompt:
            response = get_chatgpt_response(prompt)
    return render(req, 'blog/index.html', {'posts': posts, 'categories': categories, 'response': response})
def blogs(req, category_id=None):
    categories = Category.objects.all()
    if category_id:
        posts = Post.objects.filter(category_id=category_id)
    else:
        posts = Post.objects.all()
    return render(req, 'blog/blogs.html', {'posts': posts, 'categories': categories})

def blog_details(req, id):
    post = get_object_or_404(Post, id=id)
    return render(req, 'blog/details.html', {'post': post})

def create_post(req):
    categories = Category.objects.all()
    if req.method == "POST":
        title = req.POST.get('title')
        content = req.POST.get('content')
        category_id = req.POST.get('category')
        if category_id:
            category = Category.objects.get(id=category_id)
        else:
            category = None
        post = Post.objects.create(title=title, content=content, category=category)
        return redirect('blog_details', id=post.id)
    return render(req, 'blog/create_post.html', {'categories': categories})

def update_post(req, id):
    post = get_object_or_404(Post, id=id)
    categories = Category.objects.all()
    if req.method == "POST":
        post.title = req.POST.get('title')
        post.content = req.POST.get('content')
        category_id = req.POST.get('category')
        if category_id:
            post.category = Category.objects.get(id=category_id)
        post.save()
        return redirect('blog_details', id=post.id)
    return render(req, 'blog/update_post.html', {'post': post, 'categories': categories})

def delete_post(req, id):
    post = get_object_or_404(Post, id=id)
    if req.method == "POST":
        post.delete()
        return redirect('blogs')
    return render(req, 'blog/confirm_delete.html', {'post': post})

def chatgpt(req):
    response = None
    if req.method == 'POST':
        prompt = req.POST.get('prompt')
        if prompt:
            response = get_chatgpt_response(prompt)
    return render(req, 'blog/chatgpt.html', {'response': response})
