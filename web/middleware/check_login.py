from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import render, redirect, HttpResponse


class LoginMiddleWare(MiddlewareMixin):
    def process_request(self, request):
        """用户是否登录验证"""
        print(request.session.get("admin"), request.session.get("user"))
        if (
            request.path_info == "/admin/login/"
            or request.path_info == "/user/login/"
            or request.path_info == "/user/register/"
        ):
            return  # return None 相当于继续下一步
        if request.path_info.startswith("/admin/") and not request.session.get("admin"):
            return redirect("/admin/login/")
        if request.path_info.startswith("/user/") and not request.session.get("user"):
            return redirect("/user/login/")
