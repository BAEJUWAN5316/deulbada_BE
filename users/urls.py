# users/urls.py

from django.urls import path
from .views import FarmerSignupView

urlpatterns = [
    path('farmer-signup/', FarmerSignupView.as_view(), name='farmer-signup'),
]
