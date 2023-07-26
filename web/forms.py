from django.shortcuts import render, redirect, HttpResponse
from web import models
from django import forms
from django.core.validators import RegexValidator, ValidationError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import re, hashlib
from django.conf import settings


class BootStrapModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if field.widget.attrs:
                field.widget.attrs["class"] = "form-control"
                field.widget.attrs["placeholder"] = field.label
            else:
                field.widget.attrs = {
                    "class": "form-control",
                    "placeholder": field.label,
                }


class AdminModelForm(BootStrapModelForm):
    class Meta:
        model = models.Admin
        fields = "__all__"
        widgets = {"password": forms.PasswordInput(render_value=True)}

    def md5(self, pwd):
        salt = settings.SECRET_KEY.encode("utf-8")
        obj = hashlib.md5(salt)
        obj.update(pwd.encode("utf-8"))
        return obj.hexdigest()

    def clean_password(self):
        password = self.cleaned_data.get("password")
        return self.md5(password)


class UserLoginModelForm(BootStrapModelForm):
    class Meta:
        model = models.User
        fields = ["name", "password"]
        widgets = {"password": forms.PasswordInput(render_value=True)}

    def md5(self, pwd):
        salt = settings.SECRET_KEY.encode("utf-8")
        obj = hashlib.md5(salt)
        obj.update(pwd.encode("utf-8"))
        return obj.hexdigest()

    def clean_password(self):
        password = self.cleaned_data.get("password")
        return self.md5(password)


class UserModelForm(BootStrapModelForm):
    confirm_pwd = forms.CharField(
        label="确认密码", widget=forms.PasswordInput(render_value=True)
    )

    class Meta:
        model = models.User
        fields = "__all__"
        widgets = {"password": forms.PasswordInput(render_value=True)}

    def md5(self, pwd):
        salt = settings.SECRET_KEY.encode("utf-8")
        obj = hashlib.md5(salt)
        obj.update(pwd.encode("utf-8"))
        return obj.hexdigest()

    def clean_password(self):
        password = self.cleaned_data.get("password")
        return self.md5(password)

    def clean_confirm_pwd(self):
        password = self.cleaned_data.get("password")
        confirm_pwd = self.cleaned_data.get("confirm_pwd")
        if password != self.md5(confirm_pwd):
            raise ValidationError("密码不一致")
        return confirm_pwd
    
    def clean_name(self):
        name = self.cleaned_data.get("name")
        if models.User.objects.filter(name=name).exists():
            raise ValidationError("用户名已经存在")
        return name


class UserEditModelForm(BootStrapModelForm):
    class Meta:
        model = models.User
        fields = ["name", "create_time", "gender", "banji"]
    def clean_name(self):
        name = self.cleaned_data.get("name")
        if models.User.objects.filter(name=name).exists():
            raise ValidationError("用户名已经存在")
        return name


class UserResetModelForm(BootStrapModelForm):
    confirm_pwd = forms.CharField(
        label="确认密码", widget=forms.PasswordInput(render_value=True)
    )

    class Meta:
        model = models.Admin
        fields = ["password"]
        widgets = {"password": forms.PasswordInput(render_value=True)}

    def md5(self, pwd):
        salt = settings.SECRET_KEY.encode("utf-8")
        obj = hashlib.md5(salt)
        obj.update(pwd.encode("utf-8"))
        return obj.hexdigest()

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if self.md5(password) == self.instance.password:
            raise ValidationError("密码与原密码一致")
        return self.md5(password)

    def clean_confirm_pwd(self):
        password = self.cleaned_data.get("password")
        confirm_pwd = self.cleaned_data.get("confirm_pwd")
        if password != self.md5(confirm_pwd):
            raise ValidationError("密码不一致")
        return confirm_pwd


class CourseModelForm(BootStrapModelForm):
    class Meta:
        model = models.Course
        fields = "__all__"


class CheckInModelForm(BootStrapModelForm):
    class Meta:
        model = models.CheckIn
        fields = ["course"]
