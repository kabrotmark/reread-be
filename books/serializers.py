from rest_framework import serializers
from .models import Book


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'isbn', 'publication_year', 'genre', 'pages', 'description', 'date_added', 'date_modified']
        read_only_fields = ['id', 'date_added', 'date_modified']

    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)
    
    def validate_title(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Title cannot be empty")
        return value.strip()
    
    def validate_author(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("Author cannot be empty")
        return value.strip()