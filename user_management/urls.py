from django.urls import include, path
from .views import CreateUserView

urlpatterns = [
    path('users/create/',CreateUserView.as_view(), name='create-user'),
]