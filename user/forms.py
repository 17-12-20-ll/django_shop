import re

from django import forms
from django.contrib.auth.hashers import check_password

from user.models import User


class RegisterForm(forms.Form):
    user_name = forms.CharField(max_length=20, min_length=5, required=True,
                                error_messages={
                                    'required': '用户名必填',
                                    'max_length': '用户名不能超过20字符',
                                    'min_length': '用户名不能少于5字符'
                                })
    pwd = forms.CharField(max_length=20, min_length=8, required=True,
                          error_messages={
                              'required': '密码必填',
                              'max_length': '密码不能超过20字符',
                              'min_length': '密码不能少于8字符'
                          })
    cpwd = forms.CharField(max_length=20, min_length=8, required=True,
                           error_messages={
                               'required': '密码必填',
                               'max_length': '密码不能超过20字符',
                               'min_length': '密码不能少于8字符'
                           })
    email = forms.CharField(required=True, error_messages={'required0': '邮箱必填'})
    allow = forms.BooleanField(required=True, error_messages={'required': '必须同意协议'})

    def clean_user_name(self):
        # 校验注册的账号已存在
        username = self.cleaned_data['user_name']
        user = User.objects.filter(username=username).first()
        if user:
            raise forms.ValidationError('抱歉,该账号已存在,请更换账号注册!')
        return self.cleaned_data['user_name']

    def clean(self):
        # 校验密码是否一致
        pwd = self.cleaned_data.get('pwd')
        cpwd = self.cleaned_data.get('cpwd')
        if pwd != cpwd:
            raise forms.ValidationError({'cpwd': '两次密码不一致'})
        return self.cleaned_data

    def clean_email(self):
        # 校验邮箱格式
        email_regx = '^[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+){0,4}$'
        email = self.cleaned_data['email']
        if not re.match(email_regx, email):
            raise forms.ValidationError('邮箱格式错误')
        return self.cleaned_data['email']


class LoginForm(forms.Form):
    username = forms.CharField(max_length=20, min_length=5, required=True,
                               error_messages={
                                   'required': '用户名必填',
                                   'max_length': '用户名不能超过20字符',
                                   'min_length': '用户名不能少于5字符'
                               })
    pwd = forms.CharField(max_length=20, min_length=8, required=True,
                          error_messages={
                              'required': '密码必填',
                              'max_length': '密码不能超过20字符',
                              'min_length': '密码不能少于8字符'
                          })

    def clean(self):
        # 用户名是否已经注册
        username = self.cleaned_data.get('username')
        user = User.objects.filter(username=username).first()
        if not user:
            raise forms.ValidationError({'username': '该账号没有注册,请先注册'})
        # 校验密码
        password = self.cleaned_data.get('pwd')
        if not check_password(password, user.password):
            raise forms.ValidationError({'pwd': '用户密码错误'})
        return self.cleaned_data


class AddressForm(forms.Form):
    username = forms.CharField(max_length=5, required=True,
                               error_messages={'required': '收件人必填', 'max_length': '收件人姓名不能超过5个字符'})
    address = forms.CharField(required=True, error_messages={'required': '收件地址必填'})
    postcode = forms.CharField(required=True, error_messages={'required': '邮编必填'})
    mobile = forms.CharField(required=True, error_messages={'required': '手机号必填'})

    def clean(self):
        # 校验手机号,校验邮箱
        pass
