# _*_ coding: utf-8 _*_
from django.conf.urls import url

from .views import CourseListView, CourseDetailView, \
    CourseInfoView, CourseCommentView, AddCommentView, VideoPlayView

urlpatterns = [
    # 课程列表页
    url(r'^list/$', CourseListView.as_view(), name='course_list'),
    # 课程详情页
    url(r'^detail/(?P<course_id>\d+)/$', CourseDetailView.as_view(), name='course_detail'),
    # 课程章节信息页
    url(r'^info/(?P<course_id>\d+)/$', CourseInfoView.as_view(), name='course_lesson'),
    # 课程评论页
    url(r'^comment/(?P<course_id>\d+)/$', CourseCommentView.as_view(), name='course_comment'),
    # 添加课程评论
    url(r'^add_comment/$', AddCommentView.as_view(), name='add_comment'),
    # 视频播放
    url(r'^video/(?P<video_id>\d+)/$', VideoPlayView.as_view(), name='video_play'),
]
