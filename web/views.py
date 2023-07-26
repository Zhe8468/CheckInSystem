from django.shortcuts import render, redirect, HttpResponse
from web import models
from django import forms
from django.core.validators import RegexValidator, ValidationError
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import re, datetime, os
from openpyxl import Workbook, styles
from web.forms import (
    BootStrapModelForm,
    UserModelForm,
    AdminModelForm,
    UserEditModelForm,
    UserResetModelForm,
    CourseModelForm,
    CheckInModelForm,
    UserLoginModelForm,
)


def download(request):
    wb = Workbook()
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    file_path = os.path.join(os.path.expanduser("~"), "Desktop")
    sheet = wb.active
    sheet.append(["课程名称", "讲师", "学生姓名", "学生班级", "签到时间", "签到状态"])
    checkins = None
    if request.GET.get("q") == "all":
        checkins = models.CheckIn.objects.all()
        file_path = os.path.join(file_path, "学生之家全部签到记录.xlsx")
    else:
        checkins = models.CheckIn.objects.filter(time=today)
        file_path = os.path.join(file_path, "{}学生之家签到记录.xlsx".format(today))
    for checkin in checkins:
        sheet.append(
            [
                "《{}》".format(checkin.course.name),
                checkin.course.teacher_name,
                checkin.user.name,
                checkin.user.banji,
                checkin.time,
                "已签到" if checkin.status == 1 else "未签到",
            ]
        )
    # 第一行加粗
    for cell in sheet["1"]:
        cell.font = styles.Font(bold=True)
    # 保存
    wb.save(file_path)
    return HttpResponse("已经保存到桌面")


def user_login(request):
    if request.method == "GET":
        form = UserLoginModelForm()
        print(form)
        return render(request, "user/user_login.html", {"form": form})
    form = UserLoginModelForm(data=request.POST)
    if form.is_valid():
        user = models.User.objects.filter(
            name=form.cleaned_data["name"],
            password=form.cleaned_data["password"],
        ).first()
        if not user:
            form.add_error("password", "用户名或密码错误")
            return render(request, "user/user_login.html", {"form": form})
        request.session["user"] = {"id": user.id, "username": user.name}
        return redirect("/user/index/")
    else:
        return render(request, "user/user_login.html", {"form": form})


def user_index(request):
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    user_id = request.session.get("user").get("id")
    user = models.User.objects.filter(id=user_id).first()
    checkins = models.CheckIn.objects.filter(user_id=user_id).all()
    checkin_today = models.CheckIn.objects.filter(user_id=user_id, time=today).first()
    print(checkins, checkin_today)
    return render(
        request,
        "user/user_index.html",
        {"user": user, "checkin": checkin_today, "checkins": checkins},
    )


def user_checkin(request):
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    user_id = request.session.get("user").get("id")
    user = models.User.objects.filter(id=user_id).first()
    checkin_today = models.CheckIn.objects.filter(user_id=user_id, time=today).first()
    if not checkin_today:
        return redirect("/user/index/?error={}".format("讲师还没有发布今天的签到，请等待！"))
    elif checkin_today.status == 1:
        return redirect("/user/index/?error={}".format("你今天已经签到过了，请不要重复签到！"))
    # 查询到用户签到数据 更新
    models.CheckIn.objects.filter(user_id=user_id, time=today).update(status=1)
    return redirect("/user/index/?success={}".format("签到成功！"))


def user_add(request):
    if request.method == "GET":
        form = UserModelForm()
        return render(request, "admin/user_add.html", {"form": form})
    form = UserModelForm(data=request.POST)
    if form.is_valid():
        form.save()
        return redirect("/admin/user/")
    else:
        return render(request, "admin/user_add.html", {"form": form})


def user_edit(request, id):
    user = models.User.objects.filter(id=id).first()
    if not user:
        return render(request, "error.html", {"msg": "ID不存在"})
    if request.method == "GET":
        form = UserEditModelForm(instance=user)
        return render(request, "admin/user_edit.html", {"form": form})
    form = UserEditModelForm(data=request.POST, instance=user)
    if form.is_valid():
        form.save()
        return redirect("/admin/user/")
    else:
        return render(request, "admin/user_edit.html", {"form": form})


def user_delete(request, id):
    user = models.User.objects.filter(id=id).first()
    if not user:
        return render(request, "error.html", {"msg": "ID不存在"})
    user.delete()
    return redirect("/admin/user/")


def user_reset(request, id):
    user = models.User.objects.filter(id=id).first()
    if not user:
        return render(request, "error.html", {"msg": "ID不存在"})
    if request.method == "GET":
        form = UserResetModelForm()
        return render(
            request, "admin/user_reset.html", {"form": form, "username": user.name}
        )
    form = UserResetModelForm(data=request.POST, instance=user)
    if form.is_valid():
        form.save()
        return redirect("/admin/user/")
    else:
        return render(
            request, "admin/user_reset.html", {"form": form, "username": user.name}
        )


def user_list(request):
    dict = {}
    q = request.GET.get("q", "")
    if q:
        dict["name__contains"] = q
    users = models.User.objects.filter(**dict).all()
    # 分页器
    paginator = Paginator(users, 10)
    page_number = request.GET.get("page")
    try:
        page_obj = paginator.page(page_number)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    return render(
        request,
        "admin/user_list.html",
        {"users": users, "q": q, "page_obj": page_obj},
    )


def admin_login(request):
    if request.method == "GET":
        form = AdminModelForm()
        return render(request, "admin/admin_login.html", {"form": form})
    form = AdminModelForm(data=request.POST)
    if form.is_valid():
        admin = models.Admin.objects.filter(
            username=form.cleaned_data["username"],
            password=form.cleaned_data["password"],
        ).first()
        if not admin:
            form.add_error("password", "用户名或密码错误")
            return render(request, "admin/admin_login.html", {"form": form})
        request.session["admin"] = {"id": admin.id, "username": admin.username}
        return redirect("/admin/user/")
    else:
        return render(request, "admin/admin_login.html", {"form": form})


def course_list(request):
    courses = models.Course.objects.all()
    return render(request, "admin/course_list.html", {"courses": courses})


def course_add(request):
    if request.method == "GET":
        form = CourseModelForm()
        return render(request, "admin/course_add.html", {"form": form})
    form = CourseModelForm(data=request.POST)
    if form.is_valid():
        form.save()
        return redirect("/admin/course/")
    else:
        return render(request, "admin/course_add.html", {"form": form})


def course_edit(request, id):
    course = models.Course.objects.filter(id=id).first()
    if not course:
        return render(request, "error.html", {"msg": "ID不存在"})
    if request.method == "GET":
        form = CourseModelForm(instance=course)
        return render(request, "admin/course_edit.html", {"form": form})
    form = CourseModelForm(data=request.POST, instance=course)
    if form.is_valid():
        form.save()
        return redirect("/admin/course/")
    else:
        return render(request, "admin/course_edit.html", {"form": form})


def course_delete(request, id):
    course = models.Course.objects.filter(id=id).first()
    if not course:
        return render(request, "error.html", {"msg": "ID不存在"})
    course.delete()
    return redirect("/admin/course/")


def checkin_list(request):
    dict = {}
    q = request.GET.get("q", "")
    user = None
    if q:
        user = models.User.objects.filter(name=q).first()
        if not user:
            return redirect("/admin/checkin/?error={}".format("找不到该用户的签到记录 请输入正确的用户名"))
        dict["user_id"] = user.id
    checkins = models.CheckIn.objects.filter(**dict).order_by("-time")
    # 分页器
    paginator = Paginator(checkins, 10)
    page_number = request.GET.get("page")
    try:
        page_obj = paginator.page(page_number)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    return render(
        request,
        "admin/checkin_list.html",
        {"checkins": checkins, "page_obj": page_obj, "user": user},
    )


def checkin_add(request):
    if request.method == "GET":
        form = CheckInModelForm()
        return render(request, "admin/checkin_add.html", {"form": form})
    # 判断今天是否签到过
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    if models.CheckIn.objects.filter(time=today).exists():
        return render(request, "error.html", {"msg": "你今天已经发布过签到了，请不要重复签到!"})
    form = CheckInModelForm(data=request.POST)
    if form.is_valid():
        users = models.User.objects.all()
        for user in users:
            models.CheckIn.objects.create(
                course_id=form.cleaned_data["course"].id,
                user_id=user.id,
                status=0,
                time=today,
            )
        return redirect("/admin/checkin/")
    else:
        return render(request, "admin/checkin_add.html", {"form": form})


def admin_logout(request):
    request.session["admin"] = {}
    return redirect("/admin/login/")


def user_logout(request):
    request.session["user"] = {}
    return redirect("/user/login/")
