# _*_ coding: utf-8 _*_
from django.conf.urls import url

from .views import UserInfoView, UploadImageView, UpdatePwdView, SendMailCodeView, \
    UpdateEmailView, MyCourseView, MyFavOrgView, MyFavCourseView, MyFavTeacherView, MyMessageView

urlpatterns = [
    # 用户信息
    url(r'^info/$', UserInfoView.as_view(), name="user_info"),
    # 修改头像
    url(r'^image/upload/$', UploadImageView.as_view(), name="image_upload"),
    # 用户个人中心修改密码
    url(r'^update/pwd/$', UpdatePwdView.as_view(), name="update_pwd"),
    # 发送邮箱验证码
    url(r'^sendemail_code/$', SendMailCodeView.as_view(), name="sendemail_code"),
    # 修改邮箱
    url(r'^update_email/$', UpdateEmailView.as_view(), name="update_email"),
    # 我的课程
    url(r'^mycourse/$', MyCourseView.as_view(), name="mycourse"),
    # 我的收藏之课程
    url(r'^myfav/course/$', MyFavCourseView.as_view(), name="myfav_course"),
    # 我的收藏之机构
    url(r'^myfav/org/$', MyFavOrgView.as_view(), name="myfav_org"),
    # 我的收藏之教师
    url(r'^myfav/teacher/$', MyFavTeacherView.as_view(), name="myfav_teacher"),
    # 我的消息
    url(r'^mymessage/$', MyMessageView.as_view(), name="my_message"),
]
