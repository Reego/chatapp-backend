"""app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User

import json

from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from bleach import clean
from django import forms

class RegistrationForm(forms.ModelForm):
    username = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super(RegistrationForm, self).clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

    class Meta:
        model = User

@csrf_protect
def signup(request):
    obj = json.loads(request.body)
    form = RegistrationForm(obj)
    if form.is_valid():
        user = form.save(False)
        user.set_password(user.password)
        user.save()
        user = authenticate(username=user.username, password=obj['password'])
        login(request, user)
        return JsonResponse({'username': obj['username']})
    return JsonResponse({'username': '' })
    # return JsonResponse({'username': })

@csrf_protect
def form_login(request):
    obj = json.loads(request.body)
    user = authenticate(username=obj['username'], password=obj['password'])
    if user is not None:
        login(request, user)
        return JsonResponse({'username': obj['username']})
    return JsonResponse({'username': '' })


@csrf_protect
def ping_login(request):
    obj = json.loads(request.body)
    if request.user.is_authenticated:
        return JsonResponse({'username': request.user.username })
    return JsonResponse({'username': '' })

@csrf_protect
def logout(request):
    if request.user.is_authenticated:
        logout(request)
    return HttpResponse()

@ensure_csrf_cookie
def csrf(request):
    return HttpResponse()

urlpatterns = [
    path('admin/', admin.site.urls),
    #path('chat/', include('apps.chat.urls')),
    path('csrf/', csrf),
    path('auth/signup/', signup),
    path('auth/login', form_login),
    path('auth/logout', logout),
]
