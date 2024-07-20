from allauth.account.utils import send_email_confirmation
from django.contrib.auth import logout, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.http import request, HttpResponseNotFound
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, View

from .forms import CustomUserCreationForm, ProfileForm, UserForm
from .models import Profile



class ProfileView(View):
    template_name = 'profile.html'
    # form_class = UserProfileForm(instance=request.user)

    def get(self, request,username=None, *args, **kwargs):
        if username:
            # profile = get_object_or_404(User, username=username).profile
            try:
                profile = User.objects.get(username=username).profile
            except User.DoesNotExist:
                return HttpResponseNotFound(render(request, '404.html'))
        else:
            if request.user.is_authenticated:
                profile = request.user.profile
            else:
                return redirect('account_login')
        return render(request, self.template_name, {'profile': profile})

@method_decorator(login_required, name='dispatch')
class Profile_edit_View(View):
    template_name = 'profile_edit.html'

    def get(self, request, *args, **kwargs):
        profile_form = ProfileForm(instance=request.user.profile)
        onboarding = False
        if request.path == reverse('profile-onboarding'):
            onboarding = True

        return render(request, self.template_name, {'form': profile_form, 'onboarding': onboarding})

    def post(self, request, *args, **kwargs):
        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if  profile_form.is_valid():
            profile_form.save()
            return redirect('profile')
        return render(request, self.template_name, {'form': profile_form})



@login_required
def profile_email_verify(request):
    send_email_confirmation(request, request.user)
    return redirect('profile-settings')

@login_required
def profile_settings_view(request):
    return render(request, 'profile_settings.html')

