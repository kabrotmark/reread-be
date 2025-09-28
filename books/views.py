from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.core.files.storage import default_storage
import anthropic
import os
import csv
import base64
from datetime import datetime
from dotenv import load_dotenv
from .models import Book
from .serializers import BookSerializer


@method_decorator(csrf_exempt, name='dispatch')
class BookListCreateView(generics.ListCreateAPIView):
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Book.objects.filter(owner=self.request.user)


@method_decorator(csrf_exempt, name='dispatch')
class BookRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Book.objects.filter(owner=self.request.user)


def load_prompt_template():
    prompt_file_path = os.path.join(settings.BASE_DIR, 'prompt_config.txt')
    try:
        with open(prompt_file_path, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return "Tell me about the book: {title} by {author}"


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remind_me_view(request, book_id):
    try:
        book = get_object_or_404(Book, id=book_id, owner=request.user)
        # Load .env file
        load_dotenv()

        ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
        if not ANTHROPIC_API_KEY:
            return Response({
                'error': 'Claude API key not configured'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        prompt_template = load_prompt_template()
        prompt = prompt_template.format(title=book.title, author=book.author)
        
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=300,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        claude_response = response.content[0].text
        
        return Response({
            'book': {
                'id': book.id,
                'title': book.title,
                'author': book.author
            },
            'reminder': claude_response
        })
        
    except Book.DoesNotExist:
        return Response({
            'error': 'Book not found or does not belong to user'
        }, status=status.HTTP_404_NOT_FOUND)
        
    except Exception as e:
        return Response({
            'error': f'Failed to generate reminder: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def analyze_bookshelf_photo(request):
    try:
        # Use the sample image
        sample_path = "uploads/bookshelf_photos/sample.png"
        
        # Check if sample file exists
        if not default_storage.exists(sample_path):
            return Response({
                'error': 'Sample image not found at uploads/bookshelf_photos/sample.png'
            }, status=status.HTTP_404_NOT_FOUND)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = "sample.png"
        
        # Read and encode image for Claude
        with default_storage.open(sample_path, 'rb') as f:
            image_data = f.read()
            image_base64 = base64.b64encode(image_data).decode('utf-8')
        
        # Load environment variables
        load_dotenv()
        ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
        
        if not ANTHROPIC_API_KEY:
            return Response({
                'error': 'Claude API key not configured'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # Analyze image with Claude Vision
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1000,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": image_base64
                            }
                        },
                        {
                            "type": "text",
                            "text": '''Please analyze this bookshelf photo and identify all visible books. For each book you can clearly identify, provide:
1. Title (if visible)
2. Author (if visible)
3. A confidence level (high/medium/low) based on how clearly you can read the text

Format your response as a list, with each book on a new line like this:
- Title: [title or "Unknown"], Author: [author or "Unknown"], Confidence: [high/medium/low]

Only include books where you can see text on the spine or cover. Don't guess or make up titles.'''
                        }
                    ]
                }
            ]
        )
        
        claude_response = response.content[0].text
        
        # Parse Claude's response to extract book data
        books_detected = []
        lines = claude_response.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('- ') or line.startswith('* '):
                # Remove bullet point
                line = line[2:].strip()
                
                # Parse the structured response
                parts = line.split(', ')
                title = "Unknown"
                author = "Unknown"
                confidence = "low"
                
                for part in parts:
                    if part.startswith('Title:'):
                        title = part.replace('Title:', '').strip()
                    elif part.startswith('Author:'):
                        author = part.replace('Author:', '').strip()
                    elif part.startswith('Confidence:'):
                        confidence = part.replace('Confidence:', '').strip()
                
                books_detected.append({
                    'title': title,
                    'author': author,
                    'confidence': confidence
                })
        
        # Save to CSV
        csv_filename = f"bookshelf_analysis_{timestamp}.csv"
        csv_path = f"exports/{csv_filename}"
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['title', 'author', 'confidence', 'analysis_date', 'photo_filename']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for book in books_detected:
                writer.writerow({
                    'title': book['title'],
                    'author': book['author'],
                    'confidence': book['confidence'],
                    'analysis_date': datetime.now().isoformat(),
                    'photo_filename': filename
                })
        
        return Response({
            'message': f'Successfully analyzed bookshelf photo',
            'books_detected': len(books_detected),
            'books': books_detected,
            'csv_file': csv_filename,
            'photo_filename': filename,
            'full_analysis': claude_response
        })
        
    except Exception as e:
        return Response({
            'error': f'Failed to analyze bookshelf photo: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
