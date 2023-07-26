from django.db import models

class User(models.Model):
    """员工表"""
    name = models.CharField("用户名", max_length=32)
    create_time = models.DateField("入社时间")
    # 性别数组
    gender_choices = ((1, "男"), (0, "女"))
    gender = models.SmallIntegerField("性别", choices=gender_choices)
    banji = models.CharField("班级", max_length=32)
    password = models.CharField("密码", max_length=64)

class Course(models.Model):
    """课程表"""
    name = models.CharField("课程名称", max_length=32)
    teacher_name = models.CharField("讲师", max_length=32)

    # 解决前端select显示问题
    def __str__(self):
        return self.name


class CheckIn(models.Model):
    """签到表"""
    course = models.ForeignKey(verbose_name="课程",to=Course,to_field="id",on_delete=models.CASCADE)
    user = models.ForeignKey(verbose_name="学生",to=User,to_field="id",on_delete=models.CASCADE)
    status_choices = ((1, "已签到"), (0, "未签到"))
    status = models.SmallIntegerField("签到情况",choices=status_choices) 
    time = models.DateField("签到时间")
    


class Admin(models.Model):
    """管理员表"""
    username = models.CharField("用户名",max_length=32)
    password = models.CharField("密码", max_length=64)