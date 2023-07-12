from django.urls import include, path
from .views import CreateUserView, LoginView

urlpatterns = [
    path('users/create/',CreateUserView.as_view(), name='create-user'),
    path('users/login/', LoginView.as_view(), name='login-user'),
]