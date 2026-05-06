from django.urls import path
from .views import (
    RegisterView, LoginView, UserProfileView,
    UploadDocumentsView, VerifyUserView, UserListView
)

urlpatterns = [
    path('register', RegisterView.as_view(), name='register'),
    path('login', LoginView.as_view(), name='login'),
    path('profile', UserProfileView.as_view(), name='profile'),
    path('upload-documents', UploadDocumentsView.as_view(), name='upload_documents'),
    path('verify/<int:user_id>', VerifyUserView.as_view(), name='verify_user'),
    path('list', UserListView.as_view(), name='user_list'),
]