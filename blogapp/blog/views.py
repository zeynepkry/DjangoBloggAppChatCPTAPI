from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from .models import Post, Category
from .utils import get_chatgpt_response, get_chatgpt_summary
from django.core.files.storage import FileSystemStorage
from .forms import BlogPostForm  # Import your form that uses CKEditor
from html import unescape  # Correct import for unescape

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

@user_passes_test(lambda u: u.is_staff)
@login_required
def create_post(req):
    categories = Category.objects.all()
    generated_content = None
    generated_summary = None
    title = None
    category_id = None
    word_count = None
    subtopics = None
    
    if req.method == "POST":
        title = req.POST.get('title')
        word_count = req.POST.get('word_count')
        subtopics = req.POST.get('subtopics')
        category_id = req.POST.get('category')
        new_category_name = req.POST.get('new_category')
        uploaded_image = req.FILES.get('uploaded_image')
        
        if new_category_name:
            category, created = Category.objects.get_or_create(name=new_category_name)
            category_id = category.id
        elif category_id:
            category = Category.objects.get(id=category_id)
        else:
            category = None

        if req.POST.get('action') == 'generate' and title:
            # Generate main content with additional parameters
            prompt = f"Generate a blog post based on the title: '{title}', with a word count of {word_count} words and covering the following subtopics: {subtopics}. Use current articles as references. Include one quote from the article, and insert the link to the article within the content."
            generated_content = unescape(get_chatgpt_response(prompt))  # Unescape content to prevent double encoding
            # Generate summary
            generated_summary = unescape(get_chatgpt_summary(generated_content))
        
        if req.POST.get('action') == 'create' and req.POST.get('content'):
            generated_content = req.POST.get('content')
            generated_summary = req.POST.get('summary')
            if uploaded_image:
                fs = FileSystemStorage()
                filename = fs.save(uploaded_image.name, uploaded_image)
                image_url = fs.url(filename)
            else:
                image_url = req.POST.get('image_url')
            post = Post.objects.create(
                title=title, 
                content=generated_content, 
                excerpt=req.POST.get('excerpt'),
                summary=generated_summary, 
                category=category, 
                image_url=image_url
            )
            return redirect('blog_details', id=post.id)
    
    # Use CKEditor form for content editing
    form = BlogPostForm(initial={
        'title': title,
        'content': generated_content,
        'summary': generated_summary,
        'category': category_id,
    })

    return render(req, 'blog/create_post.html', {
        'categories': categories,
        'form': form,
        'generated_content': generated_content,
        'generated_summary': generated_summary, 
        'title': title,
        'word_count': word_count,
        'subtopics': subtopics,
    })

@user_passes_test(lambda u: u.is_staff)
@login_required
def update_post(req, id):
    post = get_object_or_404(Post, id=id)
    categories = Category.objects.all()

    if req.method == "POST":
        form = BlogPostForm(req.POST, instance=post)
        if form.is_valid():
            form.save()

            # Handle image upload
            uploaded_image = req.FILES.get('image')
            if uploaded_image:
                fs = FileSystemStorage()
                filename = fs.save(uploaded_image.name, uploaded_image)
                post.image_url = fs.url(filename)
                post.save()

            return redirect('blog_details', id=post.id)
    else:
        form = BlogPostForm(instance=post)
    
    return render(req, 'blog/update_post.html', {'form': form, 'categories': categories, 'post': post})

@user_passes_test(lambda u: u.is_staff)
@login_required
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
