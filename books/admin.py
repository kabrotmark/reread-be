from django.contrib import admin
from .models import Book


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'owner', 'date_added']
    list_filter = ['genre', 'publication_year', 'date_added']
    search_fields = ['title', 'author', 'isbn']
    ordering = ['-date_added']
