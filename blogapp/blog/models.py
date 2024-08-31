from django.db import models
from django.utils import timezone
from ckeditor.fields import RichTextField

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

    def __str__(self):
        return self.title
