from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'excerpt', 'summary']




class BlogPostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'category', 'summary', 'excerpt', 'image_url']
        # The CKEditor widget is automatically applied to the 'content' field