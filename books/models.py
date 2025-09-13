from django.db import models
from django.contrib.auth.models import User


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    isbn = models.CharField(max_length=13, blank=True, null=True)
    publication_year = models.IntegerField(blank=True, null=True)
    genre = models.CharField(max_length=100, blank=True, null=True)
    pages = models.IntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='books')
    date_added = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_added']

    def __str__(self):
        return f"{self.title} by {self.author}"
