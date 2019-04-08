"""django_yanzhengma URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.conf.urls import url

from app01.views import pcgetcaptcha
from app01.views import pcvalidate
from app01.views import pcajax_validate
# from app01.views import mobileajax_validate
from app01.views import home

urlpatterns = [
    url(r'^pc-geetest/register', pcgetcaptcha, name='pcgetcaptcha'),
    # url(r'^mobile-geetest/register', pcgetcaptcha, name='mobilegetcaptcha'),
    url(r'^pc-geetest/validate$', pcvalidate, name='pcvalidate'),
    url(r'^pc-geetest/ajax_validate', pcajax_validate, name='pcajax_validate'),
    # url(r'^mobile-geetest/ajax_validate',mobileajax_validate, name='mobileajax_validate'),
    url(r'/*', home, name='home'),
]
