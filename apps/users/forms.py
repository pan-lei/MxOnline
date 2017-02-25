# _*_ coding: utf-8 _*_
# 这个文件是用来实现对表单提交数据的检查的
# 检查长度是否满足要求，是否必填项为空等
# 若不创建这个文件，就需要在views.py中进行逻辑判断
# 会不优雅，很混乱
# 也就是说django将python的优雅，简洁做的很好。将各功能进行合理的分割
from django import forms
from captcha.fields import CaptchaField

from.models import UserProfile

__author__ = 'Perry'
__date__ = '2017/2/15 11:06'


# 这个类负责登录的验证
# 继承了forms.Form 里的一些方法
# 在views.py中被引入调用
class LoginForm(forms.Form):
    # required=True 表示不允许为空，即为必填项，若为空就报错
    # 还有max_length 等判断
    # 注意该处的名称一定要与前台的名称相对应
    username = forms.CharField(required=True)
    password = forms.CharField(required=True, min_length=5)


# 注册表单验证码的配置
class RegisterForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.CharField(required=True, min_length=5)
    captcha = CaptchaField(error_messages={"invalid": u"验证码错误"})


# 忘记密码的表单的配置
class ForgetForm(forms.Form):
    email = forms.EmailField(required=True)
    captcha = CaptchaField(error_messages={"invalid": u"验证码错误"})


# 重置密码的表单的配置
class ModifyPwdForm(forms.Form):
    password1 = forms.CharField(required=True, min_length=5)
    password2 = forms.CharField(required=True, min_length=5)


# 用户修改头像的form验证
class UpLoadImageForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['image']


# 用户修改信息的form验证
class UserInfoForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['nick_name', 'birday', 'gender', 'address', 'mobile']
