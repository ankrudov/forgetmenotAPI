from django.urls import path
from .views import CreateUserView, LoginView, UpdateUserView, DeleteUserView

urlpatterns = [
    path('users/create/',CreateUserView.as_view(), name='create-user'),
    path('users/login/', LoginView.as_view(), name='login-user'),
    path('users/update-user/',UpdateUserView.as_view(),name='update-user'),
    path('users/delete-user/', DeleteUserView.as_view(), name='delete-user'),
]