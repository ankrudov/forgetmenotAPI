from django.urls import include, path
from .views import CreateUserView, LoginView, UpdateUserView, UpdatePasswordView

urlpatterns = [
    path('users/create/',CreateUserView.as_view(), name='create-user'),
    path('users/login/', LoginView.as_view(), name='login-user'),
    path('users/update-user/<int:pk>/',UpdateUserView.as_view(),name='update-user'),
    path('users/update-password/',UpdatePasswordView.as_view(), name='update-password'),
]