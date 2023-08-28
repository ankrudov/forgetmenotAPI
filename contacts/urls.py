from django.urls import path
from .views import CreateContactView

urlpatterns = [
    path('contacts/create/',CreateContactView.as_view(),name='create-contact'),
]
