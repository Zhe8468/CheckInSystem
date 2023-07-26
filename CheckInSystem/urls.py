from django.contrib import admin
from django.urls import path
from web import views

urlpatterns = [
    # 管理员
    path('admin/login/', views.admin_login),
    path('admin/user/', views.user_list),
    path('admin/user/add/', views.user_add),
    path('admin/user/edit/<int:id>/', views.user_edit),
    path('admin/user/delete/<int:id>/', views.user_delete),
    path('admin/user/reset/<int:id>/', views.user_reset),
    path('admin/logout/', views.admin_logout),
    # 用户
    path('user/login/',views.user_login),
    path('user/index/',views.user_index),
    path('user/checkin/',views.user_checkin),
    path('user/logout/',views.user_logout),
    path('user/register/',views.user_register),
    # 课程
    path('admin/course/',views.course_list),
    path('admin/course/add/',views.course_add),
    path('admin/course/edit/<int:id>/',views.course_edit),
    path('admin/course/delete/<int:id>/',views.course_delete),
    # 签到
    path('admin/checkin/',views.checkin_list),
    path('admin/checkin/add/',views.checkin_add),
    # 下载签到记录
    path('admin/checkin/download/',views.download)
]

