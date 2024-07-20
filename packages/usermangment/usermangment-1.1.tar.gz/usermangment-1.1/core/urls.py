
from django.conf.urls.static import static
from django.conf import settings
from django.urls import path

from . import views

from .views import (

    ProfileView, Profile_edit_View, profile_email_verify, profile_settings_view,
    # EditProfileView,
    # ChangePasswordView,
)


urlpatterns = [
    path('', ProfileView.as_view(), name="profile"),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('onboarding/', ProfileView.as_view(), name="profile-onboarding"),
    path('profile/edit/', Profile_edit_View.as_view(), name='edit_profile'),
    path('emailverify/', profile_email_verify, name="profile-email-verify"),
    path('settings/', profile_settings_view, name="profile-settings"),
    path('@<username>/', ProfileView.as_view(), name="profile"),

    # path('profile/password/', views.change_password, name='change_password'),

]
