from django.urls import path

from . import views

app_name = 'accounts'

urlpatterns = [
    # No signup page: accounts are created by an administrator in the Django admin.
    path('profile/', views.ProfileDetailView.as_view(), name='profile'),
    path('profile/edit/', views.ProfileUpdateView.as_view(), name='profile_edit'),
]
