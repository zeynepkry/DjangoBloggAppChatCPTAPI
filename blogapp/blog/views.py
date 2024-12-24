
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from .models import Post, Category
from .utils import get_chatgpt_response, get_chatgpt_summary
from django.core.files.storage import FileSystemStorage
from .forms import BlogPostForm  # Import your form that uses CKEditor
from html import unescape  # Correct import for unescape
from django.core.paginator import Paginator
from django.http import HttpResponse
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
    
    # Filter posts by category or fetch all posts
    if category_id:
        posts_list = Post.objects.filter(category_id=category_id, is_archived=False).order_by('-created_at')
    else:
        posts_list = Post.objects.filter(is_archived=False).order_by('-created_at')  # Order by newest first
    
    # Add pagination
    paginator = Paginator(posts_list, 10)  # Show 10 posts per page
    page_number = req.GET.get('page')  # Get current page number from query parameters
    posts = paginator.get_page(page_number)  # Fetch posts for the current page
    
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
    generated_content = "Your Content goes Here"
    generated_summary = None
    
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
            prompt = f"""
            Write a detailed, well-organized educational blog article based on the following title: {title} with a word count of {word_count} and covering the following subtopics: {subtopics}. 
            The article should flow naturally, using well-structured paragraphs and a conversational yet professional tone.

            Start with a compelling introduction that grabs the reader's attention and introduces the importance of the topic. Avoid labeling sections like "Introduction" or "Main Section."
            Throughout the article, ensure smooth transitions between paragraphs and sections. 

            For each subtopic, provide clear and informative explanations, using real-life examples or case studies when applicable. Each section should have a natural, unlabelled heading.
            Include a section offering practical tips or actionable advice that readers can easily implement. Ensure these tips are relevant to the main topic.

            Conclude with a strong summary that reinforces the key points discussed and provides final thoughts, encouraging readers to apply what they've learned or explore further.
            Avoid using explicit labels such as 'Conclusion' or 'Main Point 1.'

            Keep the tone informative and approachable, avoiding jargon. If technical terms are necessary, briefly explain them.

            Structure the article to ensure readability with well-formed paragraphs and double spacing between paragraphs. Do not include the title within the body of the article, and avoid using numbered lists or bullet points for section headers.Use HTML paragraph tags <p> to separate each paragraph, ensuring there is a visible gap between them.Ensure the article reads like a fluid, human-written piece, focusing on a natural and engaging style.
            """

            generated_content = unescape(get_chatgpt_response(prompt))  # Unescape content to prevent double encoding
            # Generate summary
            generated_summary = unescape(get_chatgpt_summary(generated_content))




        if req.POST.get('action') == 'create' and req.POST.get('content'):
            #get the created content when clicked on the button
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
        # Pass POST data and FILES (for image upload) to the form, and bind it to the post instance
        form = BlogPostForm(req.POST, req.FILES, instance=post)
        
        if form.is_valid():
            # Save the post, which includes updating all form fields (title, content, summary, etc.)
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
        # Instantiate the form with the existing post data
        form = BlogPostForm(instance=post)

    return render(req, 'blog/update_post.html', {
        'form': form,
        'categories': categories,
        'post': post
    })

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

def robots_txt(request):
    content = (
        "User-agent: *\n"
        "Allow: /\n"
        "Sitemap: http://datascienceai.net/sitemap.xml\n"
    )
    return HttpResponse(content, content_type="text/plain")

'''


from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from .models import Post, Category
from .utils import get_chatgpt_response, get_chatgpt_summary
from django.core.files.storage import FileSystemStorage
from .forms import BlogPostForm
from html import unescape
import logging

# Set up logging
logger = logging.getLogger(__name__)

def index(req):
    categories = Category.objects.all()
    posts = Post.objects.all()
    response = None
    if req.method == 'POST':
        prompt = req.POST.get('prompt')
        if prompt:
            try:
                response = get_chatgpt_response(prompt)
            except Exception as e:
                logger.error(f"Error fetching ChatGPT response: {e}")
                response = "Error fetching response. Please try again later."
    return render(req, 'blog/index.html', {'posts': posts, 'categories': categories, 'response': response})

def blogs(req, category_id=None):
    categories = Category.objects.all()
    posts = Post.objects.filter(category_id=category_id) if category_id else Post.objects.all()
    return render(req, 'blog/blogs.html', {'posts': posts, 'categories': categories})

def blog_details(req, id):
    post = get_object_or_404(Post, id=id)
    return render(req, 'blog/details.html', {'post': post})

@user_passes_test(lambda u: u.is_staff)
@login_required
def create_post(req):
    categories = Category.objects.all()
    generated_content = generated_summary = title = category = None
    word_count = subtopics = image_url = None
    is_published = False

    if req.method == "POST":
        title = req.POST.get('title')
        word_count = req.POST.get('word_count')
        subtopics = req.POST.get('subtopics')
        category_id = req.POST.get('category')
        new_category_name = req.POST.get('new_category')
        uploaded_image = req.FILES.get('uploaded_image')

        # Handle category creation or selection
        if new_category_name:
            category, created = Category.objects.get_or_create(name=new_category_name)
        elif category_id:
            category = Category.objects.get(id=category_id)

        # Generate content and summary using ChatGPT
        if req.POST.get('action') == 'generate' and title:
            try:
                prompt = (f"Generate a blog post based on the title: '{title}', "
                          f"with a word count of {word_count} words and covering the following subtopics: {subtopics}. "
                          "Use current articles as references. Include one quote from the article, and insert the link to the article within the content.")
                generated_content = unescape(get_chatgpt_response(prompt))
                generated_summary = unescape(get_chatgpt_summary(generated_content))
            except Exception as e:
                logger.error(f"Error generating content or summary: {e}")
                generated_content = "Error generating content."
                generated_summary = "Error generating summary."

        # Create a new post
        if req.POST.get('action') == 'create' and req.POST.get('content'):
            try:
                generated_content = req.POST.get('content')
                generated_summary = req.POST.get('summary')
                
                # Handle image upload
                if uploaded_image:
                    fs = FileSystemStorage()
                    filename = fs.save(uploaded_image.name, uploaded_image)
                    image_url = fs.url(filename)
                else:
                    image_url = req.POST.get('image_url')
                
                # Save the post
                post = Post.objects.create(
                    title=title,
                    content=generated_content,
                    excerpt=req.POST.get('excerpt'),
                    summary=generated_summary,
                    category=category,
                    image_url=image_url,
                    is_published = True
                )
                return redirect('blog_details', id=post.id)
                
            except Exception as e:
                logger.error(f"Error creating post: {e}")
                return render(req, 'blog/create_post.html', {
                    'categories': categories,
                    'form': BlogPostForm(),
                    'error': "An error occurred while creating the post. Please try again."
                })
                

    # Pre-fill form with initial data if necessary
    form = BlogPostForm(initial={
        'title': title,
        'content': generated_content,
        'summary': generated_summary,
        'category': category.id if category else None,
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
            try:
                form.save()

                # Handle image upload
                uploaded_image = req.FILES.get('image')
                if uploaded_image:
                    fs = FileSystemStorage()
                    filename = fs.save(uploaded_image.name, uploaded_image)
                    post.image_url = fs.url(filename)
                    post.save()

                return redirect('blog_details', id=post.id)
            except Exception as e:
                logger.error(f"Error updating post: {e}")
    
    else:
        form = BlogPostForm(instance=post)

    return render(req, 'blog/update_post.html', {'form': form, 'categories': categories, 'post': post})

@user_passes_test(lambda u: u.is_staff)
@login_required
def delete_post(req, id):
    post = get_object_or_404(Post, id=id)
    if req.method == "POST":
        try:
            post.delete()
            return redirect('blogs')
        except Exception as e:
            logger.error(f"Error deleting post: {e}")
    return render(req, 'blog/confirm_delete.html', {'post': post})

def chatgpt(req):
    response = None
    if req.method == 'POST':
        prompt = req.POST.get('prompt')
        if prompt:
            try:
                response = get_chatgpt_response(prompt)
            except Exception as e:
                logger.error(f"Error fetching ChatGPT response: {e}")
                response = "Error fetching response."
    return render(req, 'blog/chatgpt.html', {'response': response})



'''