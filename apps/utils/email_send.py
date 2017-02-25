# _*_ coding: utf-8 _*_
from random import Random

from django.core.mail import send_mail

from users.models import EmailVerifyRecord
from MxOnline.settings import EMAIL_FROM

__author__ = 'Perry'
__date__ = '2017/2/16 10:22'


# 生成随机字符串，附加到激活链接上
def random_str(randomlength=8):
    str = ''
    chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz0123456789'
    length = len(chars) - 1
    # Random()是一个类，调用它的randint函随机在给定的范围内生成一个数字
    random = Random()
    for i in range(randomlength):
        str += chars[random.randint(0, length)]
    return str


# 发送邮箱激活链接
def send_register_email(email, send_type="register"):
    # 实例化一个邮箱验证的对象，数据库中的表
    email_record = EmailVerifyRecord()
    # 调用上方的函数，生成随机字符串
    if send_type == "update_email":
        code = random_str(4)
    else:
        code = random_str(16)
    # 进行赋值
    email_record.code = code
    email_record.email = email
    email_record.send_type = send_type
    # 先将验证信息保存到数据库中，再发送邮件
    email_record.save()
    # 定义好邮件的内容
    email_title = ""
    email_body = ""

    if send_type == "register":
        email_title = u"慕学在线网注册激活链接"
        email_body = u"请点击下面的激活链接激活你的账号：http://127.0.0.1:8000/active/{0}".format(code)
        # 发送邮件，注意在settings.py中的配置,会返回一个值
        send_status = send_mail(email_title, email_body, EMAIL_FROM, [email])
        return send_status

    elif send_type == "forget":
        email_title = u"慕学在线网密码重置链接"
        email_body = u"请点击下面的链接重置你的账号：http://127.0.0.1:8000/reset/{0}".format(code)
        # 发送邮件，注意在settings.py中的配置,会返回一个值
        send_status = send_mail(email_title, email_body, EMAIL_FROM, [email])
        return send_status

    elif send_type == "update_email":
        email_title = u"慕学在线网邮箱修改验证码"
        email_body = u"您的验证码为：{0}".format(code)
        # 发送邮件，注意在settings.py中的配置,会返回一个值
        send_status = send_mail(email_title, email_body, EMAIL_FROM, [email])
        return send_status
