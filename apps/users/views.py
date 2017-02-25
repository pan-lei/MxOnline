# -*- encoding: utf-8 -*-
import json
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic.base import View
from django.contrib.auth.hashers import make_password
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger

from .models import UserProfile, EmailVerifyRecord, Banner
from .forms import LoginForm, RegisterForm, ForgetForm, ModifyPwdForm, UpLoadImageForm, UserInfoForm
from utils.email_send import send_register_email
from utils.mixin_utils import LoginRequiredMixin
from operation.models import UserCourse, UserFavorite, UserMessage
from courses.models import Course
from organization.models import CourseOrg, Teacher


# 自定义的逻辑，用以处理用户可以使用 用户名+密码登录  或者  邮箱+密码登录
class CustomBackend(ModelBackend):
    def authenticate(self, username=None, password=None, **kwargs):
        try:
            # import Q  来实现 或 运算
            user = UserProfile.objects.get(Q(username=username) | Q(email=username))
            if user.check_password(password):
                return user
        except Exception as e:
            return None
# get用以处理连接请求
# post用以处理用户提交数据
# 以类的形式来处理逻辑，可以更多的增加函数，python推荐这种方式
# 只需要在类中定义函数，django会根据前台的请求类型（get还是post）自动调用函数


# 用户登陆逻辑的实现
class LoginView(View):
    def get(self, request):
        return render(request, "login.html", {})

    def post(self, request):
        # 进行表单提交数据的逻辑判断
        # 先创建一个from的实例化对象，传进一个request.POST的dict类型参数
        # 它会根据这个参数读取表单的数据
        login_form = LoginForm(request.POST)
        # 判断是否满足提前设定好的条件，还没有进入数据库查询
        if login_form.is_valid():
            # 获取前端的数据
            user_name = request.POST.get("username", "")
            pass_word = request.POST.get("password", "")
            # 将用户名和密码进行验证，如果验证通过，会返回一个user对象，如果失败会返回一个空值
            user = authenticate(username=user_name, password=pass_word)
            if user is not None:
                # 只有激活的用户才可以等录
                if user.is_active:
                    login(request, user)
                    from django.core.urlresolvers import reverse
                    return HttpResponseRedirect(reverse("index"))
                else:
                    return render(request, "login.html", {"msg": "账号未激活！"})
            else:
                return render(request, "login.html", {"msg": "用户名或密码错误！"})
        # 不满足约定条件，直接提示错误
        else:
            return render(request, "login.html", {"login_form": login_form})


class LogOutView(View):
    """
    用户退出
    """
    def get(self, request):
        logout(request)
        from django.core.urlresolvers import reverse
        return HttpResponseRedirect(reverse("index"))


# 用户注册逻辑的实现
class RegisterView(View):
    def get(self, request):
        register_form = RegisterForm()
        return render(request, "register.html", {'register_form': register_form})

    def post(self, request):
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            # 获取前端的数据
            user_name = request.POST.get("email", "")
            # 根据获取到的邮箱，去数据库中查询，看是否已经注册，若已经注册则提示用户已存在
            if UserProfile.objects.filter(email=user_name):
                return render(request, "register.html", {"register_form": register_form, "msg": "用户已存在"})
            pass_word = request.POST.get("password", "")
            user_profile = UserProfile()
            user_profile.username = user_name
            user_profile.email = user_name
            # 表明用户还没有激活
            user_profile.is_active = False
            # 密码前台传递过来的是明文，需要加密
            # 加密的话，需要引入其他的包
            user_profile.password = make_password(pass_word)
            # 数据库中保存
            user_profile.save()

            # 发送欢迎消息
            message = UserMessage()
            message.user = user_profile.id
            message.message = "欢迎注册慕学在线网"
            message.save()

            # 发送激活链接
            status = send_register_email(user_name, "register")
            if status:
                return render(request, "login.html")
        else:
            return render(request, "register.html", {"register_form": register_form})


# 用户点击邮箱链接激活逻辑处理
class ActiveUserView(View):
    # active_code 与urls.py中的参数保持一致
    def get(self, request, active_code):
        all_records = EmailVerifyRecord.objects.filter(code=active_code)
        if all_records:
            for record in all_records:
                email = record.email
                user = UserProfile.objects.get(email=email)
                user.is_active = True
                user.save()
        else:
            return render(request, "active_fail.html")
        return render(request, "login.html")


# 用户忘记密码逻辑处理
class ForgetPwdView(View):
    def get(self, request):
        forget_form = ForgetForm()
        return render(request, "forgetpwd.html", {"forget_form": forget_form})

    def post(self, request):
        forget_form = ForgetForm(request.POST)
        if forget_form.is_valid():
            email = request.POST.get("email")
            status = send_register_email(email, "forget")
            if status:
                return render(request, "send_success.html")
        else:
            return render(request, "forgetpwd.html", {"forget_form": forget_form})


# 用户密码重置请求逻辑处理
class ResetView(View):
    # rset_code 与urls.py中的参数保持一致
    def get(self, request, reset_code):
        all_records = EmailVerifyRecord.objects.filter(code=reset_code)
        if all_records:
            for record in all_records:
                email = record.email
                return render(request, "password_reset.html", {"email": email})
        else:
            return render(request, "active_fail.html")


# 用户密码重置具体逻辑处理
class ModifyPwdView(View):
    def post(self, request):
        modify_form = ModifyPwdForm(request.POST)
        if modify_form.is_valid():
            pwd1 = request.POST.get("password1", "")
            pwd2 = request.POST.get("password2", "")
            email = request.POST.get("email")
            if pwd1 != pwd2:
                return render(request, "password_reset.html", {"email": email, "msg": "密码不一致"})
            user = UserProfile.objects.get(email=email)
            user.password = make_password(pwd2)
            user.save()
            return render(request, "login.html")
        else:
            email = request.POST.get("email")
            return render(request, "password_reset.html", {"email": email, "modify_form":modify_form})


class UserInfoView(LoginRequiredMixin, View):
    '''
    用户个人信息
    '''
    def get(self, request):
        current_page = "info"
        return render(request, "usercenter-info.html", {
            "current_page": current_page
        })

    def post(self, request):
        user_info_form = UserInfoForm(request.POST, instance=request.user)
        if user_info_form.is_valid():
            user_info_form.save()
            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            return HttpResponse(json.dumps(user_info_form.errors), content_type='application/json')


class UploadImageView(LoginRequiredMixin, View):
    '''
    用户修改头像
    '''
    def post(self, request):
        # 这里传递的request.FILES是存储文件的地方，取出request内的文件
        image_form = UpLoadImageForm(request.POST, request.FILES, instance=UserProfile)
        if image_form.is_valid():
            # 利用ModelForm有Model的特性，可以直接保存
            image_form.save()
            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            return HttpResponse('{"status":"fail"}', content_type='application/json')


class UpdatePwdView(View):
    '''
    个人中心修改密码
    '''
    def post(self, request):
        modify_form = ModifyPwdForm(request.POST)
        if modify_form.is_valid():
            pwd1 = request.POST.get("password1", "")
            pwd2 = request.POST.get("password2", "")
            if pwd1 != pwd2:
                return HttpResponse('{"status":"fail", "msg":"密码不一致"}', content_type='application/json')
            user = request.user
            user.password = make_password(pwd2)
            user.save()
            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            return HttpResponse(json.dumps(modify_form.errors), content_type='application/json')


class SendMailCodeView(LoginRequiredMixin, View):
    '''
    发送邮箱验证码
    '''
    def get(self, request):
        email = request.GET.get('email', "")
        if UserProfile.objects.filter(email=email):
            return HttpResponse('{"email":"邮箱已经存在"}', content_type='application/json')

        status = send_register_email(email, "update_email")
        if status:
            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            return HttpResponse('{"status":"fail", "msg":"发送失败，请稍后重试！"}', content_type='application/json')


class UpdateEmailView(LoginRequiredMixin, View):
    '''
    修改个人邮箱
    '''
    def post(self, request):
        email = request.POST.get('email', "")
        code = request.POST.get('code', "")
        records = EmailVerifyRecord.objects.filter(email=email, code=code, send_type="update_email")
        if records:
            user = request.user
            user.email = email
            user.save()
            return HttpResponse('{"status":"success"}', content_type='application/json')
        else:
            return HttpResponse('{"email":"验证码出错"}', content_type='application/json')


class MyCourseView(LoginRequiredMixin, View):
    """
    我的课程
    """
    def get(self, request):
        current_page = "course"
        user_courses = UserCourse.objects.filter(user=request.user)
        return render(request, "usercenter-mycourse.html", {
            "user_courses": user_courses,
            "current_page": current_page,
        })


class MyFavCourseView(LoginRequiredMixin, View):
    """
    我的收藏之课程
    """
    def get(self, request):
        current_page = "fav"
        # 取出收藏中的课程，注意取出的是对应课程的id
        fav_courses = UserFavorite.objects.filter(user=request.user, fav_type=1)
        # 根据id取数据
        user_fav_courses = []
        for fav_course in fav_courses:
            course_id = fav_course.fav_id
            course = Course.objects.get(id=course_id)
            user_fav_courses.append(course)
        return render(request, "usercenter-fav-course.html", {
            "user_fav_courses": user_fav_courses,
            "current_page": current_page,
        })


class MyFavOrgView(LoginRequiredMixin, View):
    """
    我的收藏之机构
    """
    def get(self, request):
        current_page = "fav"
        orgs_list = []
        # 取出收藏中的课程，注意取出的是对应课程的id
        fav_orgs = UserFavorite.objects.filter(user=request.user, fav_type=2)
        # 根据id取数据
        for fav_org in fav_orgs:
            org_id = fav_org.fav_id
            org = CourseOrg.objects.get(id=org_id)
            orgs_list.append(org)
        return render(request, "usercenter-fav-org.html", {
            "user_fav_orgs": orgs_list,
            "current_page": current_page,
        })


class MyFavTeacherView(LoginRequiredMixin, View):
    """
    我的收藏之教师
    """
    def get(self, request):
        current_page = "fav"
        teacher_list = []
        # 取出收藏中的课程，注意取出的是对应课程的id
        fav_teachers = UserFavorite.objects.filter(user=request.user, fav_type=3)
        # 根据id取数据
        for fav_teacher in fav_teachers:
            teacher_id = fav_teacher.fav_id
            org = Teacher.objects.get(id=teacher_id)
            teacher_list.append(org)
        return render(request, "usercenter-fav-teacher.html", {
            "teacher_list": teacher_list,
            "current_page": current_page,
        })


class MyMessageView(LoginRequiredMixin, View):
    """
    我的消息
    """
    def get(self, request):
        current_page = "message"
        all_messages = UserMessage.objects.filter(Q(user=request.user.id) | Q(user=0)).order_by("-add_time")
        # 清空未读消息
        all_unread_messages = UserMessage.objects.filter(Q(user=request.user.id) | Q(user=0), has_read=False)
        for unread_message in all_unread_messages:
            unread_message.has_read = True
            unread_message.save()

        try:
            # 分页
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        # 分页的数据
        p = Paginator(all_messages, 5, request=request)
        # 这个变量就是这一页里面的内容
        messages = p.page(page)
        return render(request, "usercenter-message.html", {
            "messages": messages,
            "current_page": current_page,
        })


class IndexView(View):
    def get(self, request):
        all_banners = Banner.objects.all().order_by("index")
        courses = Course.objects.filter(is_banner=False).order_by("-fav_nums")[:6]
        banner_courses = Course.objects.filter(is_banner=True)[:3]
        orgs = CourseOrg.objects.all().order_by("-fav_nums")[:15]
        return render(request, "index.html", {
            "all_banners": all_banners,
            "courses": courses,
            "banner_courses": banner_courses,
            "orgs": orgs,
        })
