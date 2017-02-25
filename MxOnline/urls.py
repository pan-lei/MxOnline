# -*- coding:utf-8 -*-
"""MxOnline URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.views.static import serve

import xadmin

from users.views import LoginView, RegisterView, ActiveUserView, ForgetPwdView, ResetView, ModifyPwdView, \
    LogOutView, IndexView
from MxOnline.settings import MEDIA_ROOT, STATIC_ROOT


urlpatterns = [
    # 管理后台
    url(r'^xadmin/', xadmin.site.urls),
    # 首页
    url(r'^$', IndexView.as_view(), name="index"),
    # 登陆界面
    url(r'^login/$', LoginView.as_view(), name="login"),
    # 退出功能
    url(r'^logout/$', LogOutView.as_view(), name="logout"),
    # 注册界面
    url(r'^register/$', RegisterView.as_view(), name="register"),
    # 验证码界面
    url(r'^captcha/', include('captcha.urls')),
    # 激活链接
    url(r'^active/(?P<active_code>.*)/$', ActiveUserView.as_view(), name="user_active"),
    # 忘记密码页面
    url(r'^forget/$', ForgetPwdView.as_view(), name="forget_pwd"),
    # 重置密码链接
    url(r'^reset/(?P<reset_code>.*)/$', ResetView.as_view(), name="reset_pwd"),
    # 重置密码界面
    url(r'^modify/$', ModifyPwdView.as_view(), name="modify_pwd"),
    # 配置上传文件的访问处理函数
    url(r'^media/(?P<path>.*)$', serve, {"document_root": MEDIA_ROOT}),
    # 配置static文件的处理路径
    url(r'^static/(?P<path>.*)$', serve, {"document_root": STATIC_ROOT}),

    # 课程机构url配置,包括机构首页，机构课程页等页面
    url(r'^org/', include('organization.urls', namespace="org")),
    # 课程url配置，包括课程列表，课程详情等页面
    url(r'^course/', include('courses.urls', namespace="course")),
    # 用户url配置，包括用户个人中心
    url(r'^users/', include('users.urls', namespace="users")),
]

# 404页面处理
handler404 = 'operation.views.page_not_found'
# 500页面处理
handler500 = 'operation.views.page_error'
