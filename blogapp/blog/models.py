from django.db import models
from django.utils import timezone
from ckeditor.fields import RichTextField
from django.urls import reverse  # Import reverse for get_absolute_url

class BlogPost(models.Model):
    title = models.CharField(max_length=500)
    content = RichTextField()  # This field will use CKEditor

class Category(models.Model):
    name = models.CharField(max_length=225)

    def __str__(self):
        return self.name

class Post(models.Model):
    title = models.CharField(max_length=200)
    content = RichTextField()  # This will automatically use CKEditor
    excerpt = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    is_published = models.BooleanField(default=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='posts', null=True, blank=True)
    image_url = models.URLField(max_length=200, null=True, blank=True)
    summary = models.CharField(max_length=512, blank=True, null=True)
    is_archived = models.BooleanField(default=False)  # New field
    created_at = models.DateTimeField(auto_now_add=True)  # Add this if missing
    updated_at = models.DateTimeField(auto_now=True)  # Automatically updates on save

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        # Returns the URL for this post
        return reverse('blog_details', args=[self.id])

class CSVProgress(models.Model):
    last_row = models.IntegerField(default=0)
    all_processed = models.BooleanField(default=False)
    is_running = models.BooleanField(default=False)  # New field to track running state

    class Meta:
        verbose_name = "Reddit Process"
        verbose_name_plural = "Reddit Processes"

    def __str__(self):
        # Customize the display name for each object
        if self.all_processed:
            return f"Processed Lines - Row {self.last_row}"
        else:
            return f"Reddit (Row {self.last_row}, Running: {self.is_running})"
