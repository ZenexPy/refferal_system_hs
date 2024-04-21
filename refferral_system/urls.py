from django.urls import path
from . import views

urlpatterns = [
    path('verify-phone/', views.PhoneVerificationView.as_view(), name='verify-phone'),
    path('verify-code/', views.CodeVerificationView.as_view(), name='verify-code'),
]
