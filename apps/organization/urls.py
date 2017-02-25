# _*_ coding: utf-8 _*_
from django.conf.urls import url

from .views import OrgView, AddUserAskView, OrgHomeView, OrgCourseView, OrgDescView, \
    OrgTeacherView, AddFavView, TeacherListView, TeacherDetailView

urlpatterns = [
    # 课程机构列表页
    url(r'^list/$', OrgView.as_view(), name="org_list"),
    # 用户咨询课程
    url(r'^add_ask/$', AddUserAskView.as_view(), name="add_ask"),
    # 课程机构详情页首页
    url(r'^home/(?P<org_id>\d+)/$', OrgHomeView.as_view(), name="org_home"),
    # 课程机构课程页
    url(r'^course/(?P<org_id>\d+)/$', OrgCourseView.as_view(), name="org_course"),
    # 机构介绍列表
    url(r'^desc/(?P<org_id>\d+)/$', OrgDescView.as_view(), name="org_desc"),
    # 机构讲师页面，只是该机构的所有讲师
    url(r'^teachers/(?P<org_id>\d+)/$', OrgTeacherView.as_view(), name="org_teachers"),
    # 添加收藏机构
    url(r'^fav/$', AddFavView.as_view(), name="add_fav"),
    # 所有讲师列表页
    url(r'^teacher/list/$', TeacherListView.as_view(), name="teacher_list"),
    # 所有讲师列表页
    url(r'^teacher/detail/(?P<teacher_id>\d+)/$', TeacherDetailView.as_view(), name="teacher_detail"),
]
