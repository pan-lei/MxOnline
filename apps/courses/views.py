# _*_ coding: utf-8 _*_
from django.shortcuts import render
from django.views.generic import View
from django.http import HttpResponse
from django.db.models import Q
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger

from .models import Course, CourseResource, Video
from operation.models import UserFavorite, CourseComments, UserCourse
from utils.mixin_utils import LoginRequiredMixin


class CourseListView(View):
    '''
    课程列表功能
    '''
    def get(self, request):
        current_page = "open"
        all_courses = Course.objects.all().order_by("-add_time")
        hot_courses = Course.objects.all().order_by("-click_nums")[:3]
        # 课程搜索功能
        search_keywords = request.GET.get('keywords', "")
        if search_keywords:
            all_courses = all_courses.filter(Q(name__icontains=search_keywords)
                                             | Q(desc__icontains=search_keywords)
                                             | Q(detail__icontains=search_keywords))
        # 课程排序
        sort = request.GET.get('sort', "")
        if sort:
            if sort == "hot":
                all_courses = all_courses.order_by("-click_nums")
            elif sort == "students":
                all_courses = all_courses.order_by("-students")

        try:
            # 对课程进行分页，分页的页码
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(all_courses, 6, request=request)
        # 这个变量就是这一页里面的内容,并携带了页数，前一页等信息
        courses = p.page(page)

        return render(request, 'course-list.html', {
            "current_page": current_page,
            "all_courses": courses,
            "sort": sort,
            "hot_courses": hot_courses,
        })


class CourseDetailView(View):
    '''
    课程详情页
    '''
    def get(self, request, course_id):
        course = Course.objects.get(id=int(course_id))

        has_fav_course = False
        has_fav_org = False
        if request.user.is_authenticated():
            if UserFavorite.objects.filter(user=request.user, fav_id=course.id, fav_type=1):
                has_fav_course = True
            if UserFavorite.objects.filter(user=request.user, fav_id=course.course_org.id, fav_type=2):
                has_fav_org = True
        # 课程点击数加一
        course.click_nums += 1
        course.save()
        # 相关课程推荐，根据tag进行推荐
        tag = course.tag
        if tag:
            relate_courses = Course.objects.filter(tag=tag)[:3]
        else:
            # 如果没有的话，传回一个空值是会出错的，但传回一个空list是不会出错的
            relate_courses = []

        return render(request, 'course-detail.html', {
            "course": course,
            "relate_courses": relate_courses,
            "has_fav_course": has_fav_course,
            "has_fav_org": has_fav_org,
        })


class CourseInfoView(LoginRequiredMixin, View):
    '''
    课程章节详情页,点击开始学习后跳转
    '''

    def get(self, request, course_id):
        course = Course.objects.get(id=int(course_id))
        # 查询用户是否已经关联了此课程
        user_course_relate = UserCourse.objects.filter(user=request.user, course=course)
        if not user_course_relate:
            uc = UserCourse(user=request.user, course=course)
            uc.save()
            course.students += 1
            course.save()

        # 取出所有学习这门课程的相关用户
        user_courses = UserCourse.objects.filter(course=course)
        user_ids = [user_course.user.id for user_course in user_courses]
        # 根据相关用户再次在UserCourse表中查询数据
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        # 在all_user_courses中查询出课程id
        all_courses_ids = [all_user_course.course.id for all_user_course in all_user_courses]
        # 根据查找的id在Course中查找数据
        all_courses = Course.objects.filter(course_org_id__in=all_courses_ids).order_by("-students")[:3]
        all_resources = CourseResource.objects.filter(course=course)
        return render(request, "course-video.html", {
            "course": course,
            "all_resources": all_resources,
            "all_courses": all_courses,
        })


class CourseCommentView(LoginRequiredMixin, View):
    '''
    课程评论页
    '''

    def get(self, request, course_id):
        course = Course.objects.get(id=int(course_id))
        # 取出所有学习这门课程的相关用户
        user_courses = UserCourse.objects.filter(course=course)
        user_ids = [user_course.user.id for user_course in user_courses]
        # 根据相关用户再次在UserCourse表中查询数据
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        # 在all_user_courses中查询出课程id
        all_courses_ids = [all_user_course.course.id for all_user_course in all_user_courses]
        # 根据查找的id在Course中查找数据
        all_courses = Course.objects.filter(course_org_id__in=all_courses_ids).order_by("-students")[:3]
        all_resources = CourseResource.objects.filter(course=course)
        all_comments = CourseComments.objects.all().order_by("-add_time")
        return render(request, "course-comment.html", {
            "course": course,
            "all_comments": all_comments,
            "all_resources": all_resources,
            "all_courses": all_courses,
        })


# 添加课程评论
class AddCommentView(View):
    def post(self, request):
        # 如果用户未登录
        if not request.user.is_authenticated():
            return HttpResponse('{"status":"fail", "msg": "用户未登录"}', content_type='application/json')
        course_id =request.POST.get("course_id", 0)
        comment = request.POST.get("comments", "")
        if course_id > 0 and comment:
            course_comment = CourseComments()
            course = Course.objects.get(id=int(course_id))
            course_comment.course = course
            course_comment.comments = comment
            course_comment.user = request.user
            course_comment.save()
            return HttpResponse('{"status":"success", "msg": "添加成功"}', content_type='application/json')
        else:
            return HttpResponse('{"status":"fail", "msg": "添加失败"}', content_type='application/json')


class VideoPlayView(View):
    '''
    视频播放页面
    '''
    def get(self, request, video_id):
        video = Video.objects.get(id=int(video_id))
        course = video.lesson.course
        # 查询用户是否已经关联了此课程
        user_course_relate = UserCourse.objects.filter(user=request.user, course=course)
        if not user_course_relate:
            uc = UserCourse(user=request.user, course=course)
            uc.save()

        # 取出所有学习这门课程的相关用户
        user_courses = UserCourse.objects.filter(course=course)
        user_ids = [user_course.user.id for user_course in user_courses]
        # 根据相关用户再次在UserCourse表中查询数据
        all_user_courses = UserCourse.objects.filter(user_id__in=user_ids)
        # 在all_user_courses中查询出课程id
        all_courses_ids = [all_user_course.course.id for all_user_course in all_user_courses]
        # 根据查找的id在Course中查找数据
        all_courses = Course.objects.filter(course_org_id__in=all_courses_ids).order_by("-students")[:3]
        all_resources = CourseResource.objects.filter(course=course)
        return render(request, "course-play.html", {
            "course": course,
            "all_resources": all_resources,
            "all_courses": all_courses,
            "video": video,
        })
