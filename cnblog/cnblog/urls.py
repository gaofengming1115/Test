"""cnblog URL Configuration

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
from django.urls import path, re_path
from blog import views
from cnblog import settings
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', views.login),
    path('index/', views.index),
    path('logout/', views.logout),
    path('get_valid_code_img/', views.get_valid_code_img),
    path('register/', views.register),
    path('digg/', views.digg),
    # re_path('^$', views.index),
    path('comment/', views.comment),
    path('get_comment_tree/', views.get_comment_tree),
    # 文本编辑器上传图片url
    path('upload/', views.upload),
    # media配置:
    re_path(r"media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),

    # 个人站点的跳转
    re_path('^(?P<username>\w+)/(?P<condition>tag|category|archive)/(?P<param>.*)/$', views.home_site),

    # 个人站点
    re_path("^(?P<username>\w+)$", views.home_site),

    # 文章路由
    re_path('^(?P<username>\w+)/articles/(?P<article_id>\d+)$', views.article_detail),

    # 后台管理url
    re_path("cn_backend/$", views.cn_backend),
    re_path("cn_backend/add_article/$", views.add_article),
]
