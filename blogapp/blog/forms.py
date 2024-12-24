from django import forms
from .models import Post
from ckeditor.widgets import CKEditorWidget  # Ensure you have CKEditor installed and imported

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'excerpt', 'summary']


class BlogPostForm(forms.ModelForm):
    # Explicitly set CKEditor for 'content' and 'summary' fields
    content = forms.CharField(widget=CKEditorWidget())
    summary = forms.CharField(widget=forms.Textarea()) 

    class Meta:
        model = Post
        fields = ['title', 'content', 'category', 'summary',]
