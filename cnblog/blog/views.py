import json
import os

from bs4 import BeautifulSoup
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F
from django.http import JsonResponse
from django.shortcuts import render, HttpResponse, redirect

from blog import models
from blog.Myforms import UserForm
from blog.models import UserInfo
from blog.utils.validCode import get_valid_code
from cnblog import settings


# Create your views here.


def login(request):
    if request.method == "POST":

        response = {"user": None, "msg": None}
        user = request.POST.get("user")
        pwd = request.POST.get("pwd")
        valid_code = request.POST.get("valid_code")

        valid_code_str = request.session.get("valid_code_str")
        if valid_code.upper() == valid_code_str.upper():
            # 用户认证
            user = auth.authenticate(username=user, password=pwd)
            if user:
                auth.login(request, user)  # request.user== 当前登录对象
                response["user"] = user.username
            else:
                response["msg"] = "用户名或者密码错误!"

        else:
            response["msg"] = "验证码错误!"
        return JsonResponse(response)
    return render(request, "login.html")


def get_valid_code_img(request):
    data = get_valid_code(request)
    return HttpResponse(data)


def register(request):
    if request.is_ajax():
        form = UserForm(request.POST)
        response = {"user": None, "msg": None}
        if form.is_valid():
            response["user"] = form.cleaned_data.get("user")
            # 入库
            user = form.cleaned_data.get("user")
            pwd = form.cleaned_data.get("pwd")
            email = form.cleaned_data.get("email")
            # 头像文件获取
            avator_obj = request.FILES.get("avator")
            extra = {}
            if avator_obj:
                extra["avatar"] = avator_obj
            UserInfo.objects.create_user(username=user, password=pwd, email=email, **extra)

        else:
            response["msg"] = form.errors

        return JsonResponse(response)
    form = UserForm()
    return render(request, "register.html", {"form": form})


def logout(request):
    auth.logout(request)
    return redirect("/login/")


def index(request):
    """
    系统首页
    :param request:
    :return:
    """
    article_list = models.Article.objects.all()
    return render(request, "index.html", {"article_list": article_list})


def home_site(request, username, **kwargs):
    """
    个人站点
    :param request:
    :param username:
    :return:
    """
    user = UserInfo.objects.filter(username=username).first()
    # 判断用户是否存在!
    if not user:
        return render(request, "not_found.html")

    # 查询当前站点对象

    blog = user.blog
    article_list = models.Article.objects.filter(user=user)

    if kwargs:
        condition = kwargs.get("condition")
        param = kwargs.get("param")  # 2012-12

        if condition == "category":
            article_list = article_list.filter(category__title=param)
        elif condition == "tag":
            article_list = article_list.filter(tags__title=param)
        else:
            year, month = param.split("/")
            article_list = article_list.filter(create_time__year=year, create_time__month=month)

    return render(request, "home_site.html",
                  {"username": username, "blog": blog, "article_list": article_list})


def article_detail(request, username, article_id):
    """
    文章详情页
    :param request:
    :param username:
    :param article_id:
    :return:
    """
    user = UserInfo.objects.filter(username=username).first()
    blog = user.blog

    article_obj = models.Article.objects.filter(pk=article_id).first()

    # 评论列表
    comment_list = models.Comment.objects.filter(article_id=article_id)

    return render(request, "article_detail.html", locals())


def digg(request):
    print(request.POST)
    article_id = request.POST.get("article_id")
    is_up = json.loads(request.POST.get("is_up"))

    user_id = request.user.pk

    obj = models.ArticleUpDown.objects.filter(user_id=user_id, article_id=article_id).first()
    response = {"state": True}
    if not obj:
        ard = models.ArticleUpDown.objects.create(user_id=user_id, article_id=article_id, is_up=is_up)
        queryset = models.Article.objects.filter(pk=article_id)
        if is_up:
            queryset.update(up_count=F("up_count") + 1)
        else:
            queryset.update(down_count=F("down_count") + 1)
    else:
        response["state"] = False
        response["handled"] = obj.is_up
    return JsonResponse(response)


def comment(request):
    print(request.POST)
    article_id = request.POST.get("article_id")
    pid = request.POST.get("pid")
    content = request.POST.get("content")
    user_id = request.user.pk

    # 事务操作
    with transaction.atomic():
        comment_obj = models.Comment.objects.create(user_id=user_id, article_id=article_id, content=content,
                                                    parent_comment_id=pid)
        models.Article.objects.filter(pk=article_id).update(comment_count=F("comment_count") + 1)

    response = {}
    response["create_time"] = comment_obj.create_time.strftime("%Y-%m-%d %X")
    response["username"] = request.user.username
    response["content"] = content

    return JsonResponse(response)


def get_comment_tree(request):
    article_id = request.GET.get("article_id")
    response = list(models.Comment.objects.filter(article_id=article_id).order_by("pk").values("pk", "content",
                                                                                               "parent_comment_id"))
    return JsonResponse(response, safe=False)


@login_required
def add_article(request):
    """
    后台管理的添加书籍视图函数
    :param request:
    :return:
    """
    if request.method == "POST":
        title = request.POST.get("title")
        content = request.POST.get("content")
        # 防止xss攻击,过滤script标签
        soup = BeautifulSoup(content, "html.parser")
        for tag in soup.find_all():

            print(tag.name)
            if tag.name == "script":
                tag.decompose()
        # 构建摘要数据,获取标签字符串的文本前150个符号

        desc = soup.text[0:150] + "..."

        models.Article.objects.create(title=title, desc=desc, content=str(soup), user=request.user)
        return redirect("/cn_backend/")

    return render(request, "backend/add_article.html")


def upload(request):
    """
    编辑器上传文件接受视图函数
    :param request:
    :return:
    """

    print(request.FILES)
    img_obj = request.FILES.get("upload_img")  # 文件对象
    print(img_obj.name)

    path = os.path.join(settings.MEDIA_ROOT, "add_article_img", img_obj.name)  # 指定文件上传的路径

    with open(path, "wb") as f:
        for line in img_obj:
            f.write(line)
    # 把上传的图像返回给编辑器
    response = {
        "error": 0,
        "url": "/media/add_article_img/%s" % img_obj.name  # 编辑器可以识别的路径，直接浏览器可以访问的路径
    }
    import json  # 编辑器需要json数据
    return HttpResponse(json.dumps(response))


@login_required
def cn_backend(request):
    """
    后台管理的首页
    :param request:
    :return:
    """
    article_list = models.Article.objects.filter(user=request.user)

    return render(request, "backend/backend.html", locals())
