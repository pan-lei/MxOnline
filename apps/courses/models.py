# -*- encoding:utf-8 -*-
from __future__ import unicode_literals
from datetime import datetime

from django.db import models

from organization.models import CourseOrg, Teacher


# 课程信息
class Course(models.Model):
    # 将课程与机构联系起来
    course_org = models.ForeignKey(CourseOrg, verbose_name=u"课程机构", null=True, blank=True)
    # CharField 必须指定最大长度
    name = models.CharField(max_length=50, verbose_name=u"课程名称")
    desc = models.CharField(max_length=300, verbose_name=u"课程描述")
    is_banner = models.BooleanField(default=False, verbose_name=u"是否轮播")
    # TextField 不必指定最大长度
    detail = models.TextField(verbose_name=u"课程详情")
    degree = models.CharField(choices=(("cj", u"初级"), ("zj", u"中级"), ("gj", u"高级")), max_length=2, verbose_name=u"难度")
    learn_times = models.IntegerField(default=0, verbose_name=u"学习时长（分钟数）")
    students = models.IntegerField(default=0, verbose_name=u"学习人数")
    fav_nums = models.IntegerField(default=0, verbose_name=u"收藏人数")
    image = models.ImageField(upload_to="courses/%Y/%m", verbose_name=u"封面图", max_length=100)
    click_nums = models.IntegerField(default=0, verbose_name=u"点击数")
    category = models.CharField(max_length=20, verbose_name=u"课程类别", null=True, blank=True, default=u"后端开发")
    tag = models.CharField(max_length=10, verbose_name=u"课程标签", default="")
    teacher = models.ForeignKey(Teacher, verbose_name=u"授课讲师", null=True, blank=True)
    you_need_know = models.CharField(max_length=300, verbose_name=u"课程须知", default="")
    knowledge = models.CharField(max_length=300, verbose_name=u"学到什么", default="")
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u"添加时间")

    class Meta:
        verbose_name = u"课程"
        verbose_name_plural = verbose_name

    # 获取课程章节数
    def get_zj_nums(self):
        return self.lesson_set.all().count()

    # 获取课程章节
    def get_lesson(self):
        return self.lesson_set.all()

    # 获取学习本门课程的信息
    def get_learn_users(self):
        return self.usercourse_set.all()[:5]

    def __unicode__(self):
        return self.name


# 章节类
class Lesson(models.Model):
    # 以外键的形式将章节与课程进行关联
    course = models.ForeignKey(Course, verbose_name=u"课程")
    name = models.CharField(max_length=100, verbose_name=u"章节名")
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u"添加时间")

    class Meta:
        verbose_name = u"章节"
        verbose_name_plural = verbose_name

    # 获取章节视频
    def get_video(self):
        return self.video_set.all()

    def __unicode__(self):
        return self.name


# 视频资源类
class Video(models.Model):
    # 以外键的形式将章节与章节进行关联
    lesson = models.ForeignKey(Lesson, verbose_name=u"章节")
    name = models.CharField(max_length=100, verbose_name=u"视频名称")
    url = models.CharField(max_length=200, verbose_name=u"访问链接", default="")
    learn_times = models.IntegerField(default=0, verbose_name=u"学习时长（分钟数）")
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u"添加时间")

    class Meta:
        verbose_name = u"视频"
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return self.name


# 课程资源类，提供给学员下载的课件之类的
class CourseResource(models.Model):
    # 以外键的形式将章节与课程进行关联
    course = models.ForeignKey(Course, verbose_name=u"课程")
    name = models.CharField(max_length=100, verbose_name=u"名称")
    # FileField() 一个文件类型的东西，在后台会直接生成文件上传的按钮
    download = models.FileField(upload_to="course/resource/%Y/%m", verbose_name=u"资源文件", max_length=100)
    add_time = models.DateTimeField(default=datetime.now, verbose_name=u"添加时间")

    class Meta:
        verbose_name = u"课程资源"
        verbose_name_plural = verbose_name

    def __unicode__(self):
        return self.name
