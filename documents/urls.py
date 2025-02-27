from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('upload/', views.upload_document, name='upload_document'),  # Changed the name here
    path('delete/<int:pk>/', views.delete_document, name='delete'),
]