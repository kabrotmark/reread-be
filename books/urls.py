from django.urls import path
from .views import BookListCreateView, BookRetrieveUpdateDestroyView
from .auth_views import login_view, logout_view, register_view, user_info_view

urlpatterns = [
    path('', BookListCreateView.as_view(), name='book-list-create'),
    path('<int:pk>/', BookRetrieveUpdateDestroyView.as_view(), name='book-detail'),
]

auth_urlpatterns = [
    path('login/', login_view, name='api-login'),
    path('logout/', logout_view, name='api-logout'),
    path('register/', register_view, name='api-register'),
    path('user/', user_info_view, name='api-user-info'),
]