from django.db import models

# Create your models here.


# 管理员数据模型
class Adminoo(models.Model):
    name = models.CharField(max_length=32, verbose_name="用户名")  # 图书管理员用户名
    nickname = models.CharField(max_length=32, verbose_name="昵称")  # 昵称
    password = models.CharField(max_length=32, verbose_name="密码")  # 密码


# 学院数据模型
class College(models.Model):
    name = models.CharField(max_length=32, verbose_name="学院名称", null=True, blank=True,)


# 专业数据模型
class Profession(models.Model):
    name = models.CharField(max_length=128, verbose_name="专业名称")  # 专业名称
    teacher = models.CharField(max_length=128, verbose_name="专业负责人")  # 专业负责人
    college = models.ForeignKey(to='College', on_delete=models.CASCADE, verbose_name="学院名称")


# 上报信息数据模型
class Report(models.Model):
    name = models.CharField(max_length=128, verbose_name="上报用户名")
    report_num = models.CharField(max_length=128, verbose_name="健康上报编码", null=True, blank=True)
    report_address = models.CharField(max_length=128, verbose_name="上报地址")
    card = models.CharField(max_length=32, null=True, blank=True, verbose_name="学生学号")
    report_age = models.CharField(max_length=128, verbose_name="上报年龄")
    report_phone = models.CharField(max_length=11, verbose_name="电话号码")  # 电话
    report_temperature = models.CharField(max_length=128, verbose_name="体温")
    report_description = models.TextField(verbose_name="身体状况")
    profession = models.ForeignKey(to='Profession', on_delete=models.CASCADE, verbose_name="专业名称")
    report_time = models.DateTimeField(auto_now=True, verbose_name="上报时间")    # 上报时间


class Image(models.Model):
    # 创建点数据表用来存储上传的照片路径和名称
    img_address = models.ImageField(verbose_name="图片路径")  # 图片路径 -->> 会将路径封装成一个对象，需要使用模块Pillow,python 3.6 后 使用 PIL 模块
    img_label = models.CharField(max_length=128, verbose_name="上报健康码")
    reports = models.ForeignKey(to='Report', on_delete=models.CASCADE, verbose_name="上报")  # 图书的图片


# 用户
class User(models.Model):
    name = models.CharField(max_length=32, verbose_name="用户名")
    nickname = models.CharField(max_length=32, verbose_name="用户昵称")
    sex = models.CharField(max_length=32, verbose_name="性别", default='男')
    card = models.CharField(max_length=32, null=True, blank=True, verbose_name="学生学号")
    password = models.CharField(max_length=32, verbose_name="密码")
    phone = models.CharField(max_length=11, verbose_name="电话号码")  # 电话
    time = models.DateTimeField(auto_now=True, verbose_name="时间")    # 每个用户登陆的时间
    profession = models.ForeignKey(to="Profession", on_delete=models.CASCADE, verbose_name="专业")   # 借的书进行绑定


class Teacher(models.Model):
    teacher_name = models.CharField(max_length=32, verbose_name="负责人姓名")
    teacher_card = models.CharField(max_length=32, null=True, blank=True, verbose_name="负责人工号")
    teacher_phone = models.CharField(max_length=11, null=True, blank=True, verbose_name="电话号码")  # 电话
    profession = models.ManyToManyField(to="Profession", verbose_name="专业", related_name='teacher_profession')   # 专业进行绑定

