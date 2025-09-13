from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Book
from .serializers import BookSerializer


class BookListCreateView(generics.ListCreateAPIView):
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Book.objects.filter(owner=self.request.user)


class BookRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Book.objects.filter(owner=self.request.user)
