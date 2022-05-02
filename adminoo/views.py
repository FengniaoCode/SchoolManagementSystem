from django.shortcuts import render

# Create your views here.
import hashlib
import time

from django.core.paginator import Paginator
from django.db.models import Q, Count
from faker import Faker
from django.db import connection
from django.shortcuts import render, redirect, HttpResponse

# Create your views here.
from adminoo import models


def pwd_encrypt(password):
    md5 = hashlib.md5()  # 获取md5对象
    md5.update(password.encode())  # 进行更新注意需要使用 字符串的二进制格式
    result = md5.hexdigest()  # 获取加密后的内容
    return result


# 注册视图函数
def register(request):
    if request.method == 'POST':
        # 1. 获取表单提交过来的内容
        username = request.POST.get('register_username')
        nickname = request.POST.get('register_nickname')
        password = request.POST.get('register_password')
        # 2.对密码进行加密
        password = pwd_encrypt(password)
        # 3. 保存到数据库
        models.User.objects.create(name=username, nickname=nickname, password=password)
        # 4. 重定向到登录界面
        return redirect('/adminoo/login')
    #
    return render(request, 'register_new.html')


def register_user(request):
    """注册用户"""
    if request.method == "GET":
        # 查询所有的
        profession_obj_list = models.Profession.objects.all()
        # 将页面转跳到用户添加页面，并把数据传给前端
        return render(request, "register_user.html", locals())

    else:
        # 获取表单提交过来的用户信息
        name = request.POST.get("register_username")
        nickname = request.POST.get("register_nickname")
        sex = request.POST.get("sex")
        card = request.POST.get("card")
        phone = request.POST.get("phone")
        time = request.POST.get("time")
        profession_id = request.POST.get("profession_id")
        profession_obj = models.Profession.objects.get(id=profession_id)  # 专业对象
        password = request.POST.get("register_password")
        # 对密码进行加密
        password = pwd_encrypt(password)
        # 将用户信息保存数据库中
        user_obj = models.User.objects.create(
            name=name,
            nickname=nickname,
            sex=sex,
            card=card,
            password=password,
            phone=phone,
            time=time,
            profession=profession_obj,
        )

        return redirect("/adminoo/login")
    return render(request, 'register_user.html')


def login(request):
    error_msg = ''
    if request.method == 'POST':
        # 1.获取表单提交过来的内容
        username = request.POST.get('login_username')
        pwd = request.POST.get('login_password')
        # 2. 对输入的密码进行加密
        pwd = pwd_encrypt(pwd)
        if username=="1":
            ret = models.Adminoo.objects.filter(name=username, password=pwd)
            if ret:
                # 有此用户 -->> 跳转到首页
                # 登录成功后，将用户名和昵称保存到session 中，
                request.session['username'] = username
                adminoo_obj = ret.last()  # 获取adminoo对象
                nickname = adminoo_obj.nickname
                request.session['nickname'] = nickname
                # 将用户的id 保存到session中
                request.session['id'] = adminoo_obj.id
                return render(request, 'profession_add.html')
            else:
                # 没有此用户-->> 用户名或者密码错误
                error_msg = '用户名或者密码错误请重新输入'
        else:
            # 3.数据库查询
            # select * from adminoo where name=username and password =pwd
            ret = models.User.objects.filter(name=username, password=pwd)
        # print(ret) # 如果用户不存在 返回空 QuerySet对象,转换成False
            if ret:
                # 有此用户 -->> 跳转到首页
                # 登录成功后，将用户名和昵称保存到session 中，
                request.session['username'] = username
                adminoo_obj = ret.last()  # 获取adminoo对象
                nickname = adminoo_obj.nickname
                request.session['nickname'] = nickname
                # 将用户的id 保存到session中
                request.session['id'] = adminoo_obj.id
                profession = models.Profession.objects.all()
                return render(request, 'base_user.html', {"profession": profession, "ret": ret})
                # return render(request, 'base_user.html', {'ret': ret})
                # return redirect('/adminoo/add_report_userlogin/', {"ret": ret})
            else:
                # 没有此用户-->> 用户名或者密码错误
                error_msg = '用户名或者密码错误请重新输入'
    return render(request, 'login_new.html', {'error_msg': error_msg})


# 登出
def logout(request):
    # 1. 将session中的用户名、昵称删除
    request.session.flush()
    # 2. 重定向到 登录界面
    return redirect('/adminoo/login/')


# 装饰器
def adminoo_decorator(func):
    def inner(request, *args, **kwargs):
        username = request.session.get('username')
        nickname = request.session.get('nickname')
        if username and nickname:
            """用户登录过"""
            return func(request, *args, **kwargs)
        else:
            """用户没有登录，重定向到登录页面"""
            return redirect('/adminoo/login/')

    return inner


# 专业操作
def add_profession(request):
    if request.method == "GET":
        # 获取内容
        # 从数据库中获取全部学院对象（有N条数据），然后返回到前端，通过for循环一一展示。
        college_list = models.College.objects.all()

        # 下面可以用这个：return redirect('/adminoo/profession_list/')
        # return redirect('adminoo:profession_list')
        return render(request, "profession_add.html", locals())
    elif request.method == "POST":
        profession_name = request.POST.get("profession_name")
        # profession_teacher = request.POST.get("profession_teacher")
        college_id = request.POST.get("college")  # 专业id
        college_obj = models.College.objects.get(id=college_id)  # 学院对象
        # 保存到数据库中
        models.Profession.objects.create(name=profession_name, college=college_obj, )
        return redirect('/adminoo/profession_list')


# @adminoo_decorator
def profession_list(request, page=1):
    """专业列表"""
    # 我们要把专业的数据库中的数据全部取出，传给前端进行显示
    # ----->方法init(列表,int)：返回分页对象，参数为列表数据，每面数据的条数
    #       属性count：返回对象总数
    #       属性num_pages：返回页面总数
    #       属性page_range：返回页码列表，从1开始，例如[1, 2, 3, 4]
    #       方法page(m)：返回Page对象，表示第m页的数据，下标以1开始
    if request.method == "GET":
        profession_obj_list = models.Profession.objects.all()  # 获取专业所有数据
        paginator = Paginator(profession_obj_list, 5)  # 对数据库中获取的数据进行分页，每页显示10条数据
        total_page_num = paginator.num_pages  # num_pages:总页码
        current_page_num = page if page else request.GET.get("page", 1)  # 当前页，默认显示第一页
        profession_page_objs = paginator.page(current_page_num)  # 获取当页面的数据对象，用于传到前端进行显示
        page_range = paginator.page_range  # 确定页面范围，以便进行模板渲染使用页码
        # 当前页
        # 由于每个页面只让显示10页，我们要判断，总页码是否大10页，如果总页码小于10页就直接显示。下面我们主要完成总页码大于10页的情况，我们要分情况处理。
        if total_page_num > 10:  # 当总页码大于10时
            if current_page_num < 9:  # 当前页小于10时
                page_range = range(1, 11)
            elif current_page_num + 8 > total_page_num:  # 当前页是倒数第8页时页码的范围
                page_range = range(current_page_num - 2, total_page_num + 1)
            else:
                page_range = range(current_page_num - 2, current_page_num + 8)  # 当前页大于8且小于倒数第8页时页码的范围
        else:  # 当页码小于10时
            page_range = page_range
        # Django笔记10：用local()代替视图函数中render的字典参数：https://blog.csdn.net/gaifuxi9518/article/details/88632972
        return render(request, "profession_list.html", locals())  # local()是Python中的一个内置函数，它可以将函数中的局部变量以字典的形式返回。
        # 等同于：return render(request,'profession_list.html', {'profession_page_objs': profession_page_objs})


def update_profession(request):
    """修改专业"""
    if request.method == "GET":
        profession_id = request.GET.get("id")
        # 2.从数据库中获取要修改的专业对象
        profession_obj = models.Profession.objects.get(id=profession_id)
        # profession = models.Profession.objects.get(id=profession_id)
        college_list = models.College.objects.all()
        return render(request, "profession_update.html", locals())
    else:
        # 1.获取report_list.html页面传过来的id
        profession_id = request.POST.get("id")
        # 2.从数据库中获取要修改的健康报告对象
        names = request.POST.get("name")
        # 3. 获取所有的专业数据,传到前端用来选择专业。
        college = request.POST.get("college")
        college_obj = models.College.objects.get(id=college)  # 专业对象
        # 将表单提交过来的数据保存到数据库
        profession_obj = models.Profession.objects.filter(id=profession_id).update(name=names, college=college_obj)
    return redirect('/adminoo/profession_list/')


def delete_profession(request):
    """删除专业"""
    # 获取profession_list.html页面传过来的id
    profession_id = request.GET.get('id')
    # 根据id，从数据库中获取专业对象
    profession = models.Profession.objects.get(id=profession_id)
    # 从数据库中删除该专业对象，并重定向到专业列表
    profession.delete()
    return redirect("/adminoo/profession_list/")


# @adminoo_decorator
def add_report(request):
    """添加健康报告"""
    if request.method == "GET":
        # TODO:添加性别，可以模仿上个项目的user_add
        # 从数据库中获取全部专业对象（有N条数据），然后返回到前端，通过for循环一一展示。
        profession_list = models.Profession.objects.all()
        # 将页面转调到添加健康报告的页面
        return render(request, "report_add.html", locals())
    elif request.method == "POST":
        f = Faker(locale="zh_CN")  # 初始化Faker对象
        report_num = f.msisdn()  # 健康报告编码
        # 获取report_add.html表单提交过来的数据
        report_name = request.POST.get("name")  # 上报人的姓名
        report_time = request.POST.get("report_time")  # 上报时间
        # teacher = request.POST.get("teacher")
        report_age = request.POST.get("report_age")
        card = request.POST.get("card")
        # report_price = request.POST.get("report_price")
        report_address = request.POST.get("report_address")
        report_phone = request.POST.get("report_phone")
        report_description = request.POST.get("report_description")
        report_temperature = request.POST.get("report_temperature")
        # comment_nums = request.POST.get("comment_nums")
        profession_id = request.POST.get("profession")  # 专业id
        profession_obj = models.Profession.objects.get(id=profession_id)  # 专业对象
        # 将表单获取到的数据保存到数据库中
        report_obj = models.Report.objects.create(
            report_num=report_num,
            name=report_name,
            # teacher=teacher,
            report_age=report_age,
            card=card,
            # report_price=report_price,
            report_address=report_address,
            report_phone=report_phone,
            report_description=report_description,
            report_temperature=report_temperature,
            # comment_nums=comment_nums,
            profession=profession_obj,
            report_time=report_time,
        )
        # 保存图片
        # 注意上传字段使用 FILES.getlist() 来获取 多张图片
        userfiles = request.FILES.getlist('report_image')  # 健康报告缩略图
        # 循环遍历读取每一张图片保存到images下  -->>枚举 （0,'<InMemoryUploadedFile: 3.jpg (image/jpeg)>'）
        for index, image_obj in enumerate(userfiles):
            image_type = image_obj.name.rsplit('.', 1)[
                1]  # 取出健康报告格式（jpg、png等）,[1]:表示从后面分割1个出来（jpg、png等），如果是2，那么就是分割两部分出来
            path = 'adminoo/static/images/reports/{}_{}.{}'.format(report_num, index, image_type)  # 图片路径、图片名称
            ## 保存图片
            # wb:以二进制格式打开一个文件只用于写入。如果该文件已存在则将其覆盖。如果该文件不存在，创建新文件。
            with open(path, mode='wb') as f:
                for content in image_obj.chunks():
                    f.write(content)  # 将字符串写入文件

            # 2.保存图片路径到数据库,下次使用时直接从数据库里取路径和名称就行
            obj_image = models.Image()
            path1 = 'images/reports/{}_{}.{}'.format(report_num, index, image_type)
            obj_image.img_address = path1
            obj_image.img_label = image_obj.name  # 图片原名称
            obj_image.reports = report_obj  # 设置图片和报告的关系
            obj_image.save()
            # 3.重定向到报告列表
        return redirect('/adminoo/report_list/')


def add_report_userlogin(request):
    """添加健康报告"""
    if request.method == "GET":
        # TODO:添加性别，可以模仿上个项目的user_add
        # 从数据库中获取全部专业对象（有N条数据），然后返回到前端，通过for循环一一展示。
        profession_list = models.Profession.objects.all()
        # 将页面转调到添加健康报告的页面
        return render(request, "base_user.html", locals())
    elif request.method == "POST":
        f = Faker(locale="zh_CN")  # 初始化Faker对象
        report_num = f.msisdn()  # 健康报告编码
        # 获取report_add.html表单提交过来的数据
        report_name = request.POST.get("name")  # 上报人的姓名
        report_time = request.POST.get("report_time")  # 上报时间
        # teacher = request.POST.get("teacher")
        report_age = request.POST.get("report_age")
        card = request.POST.get("card")
        # report_price = request.POST.get("report_price")
        report_address = request.POST.get("report_address")
        report_phone = request.POST.get("report_phone")
        report_description = request.POST.get("report_description")
        report_temperature = request.POST.get("report_temperature")
        ret = models.Report.objects.filter(card=card)
        # comment_nums = request.POST.get("comment_nums")
        profession_id = request.POST.get("profession")  # 专业id
        profession_obj = models.Profession.objects.get(id=profession_id)  # 专业对象
        # 将表单获取到的数据保存到数据库中
        report_obj = models.Report.objects.create(
            report_num=report_num,
            name=report_name,
            card=card,
            # teacher=teacher,
            report_age=report_age,
            # report_price=report_price,
            report_address=report_address,
            report_phone=report_phone,
            report_description=report_description,
            report_temperature=report_temperature,
            # comment_nums=comment_nums,
            profession=profession_obj,
            report_time=report_time,
        )
        # 保存图片
        # 注意上传字段使用 FILES.getlist() 来获取 多张图片
        userfiles = request.FILES.getlist('report_image')  # 健康报告缩略图
        # 循环遍历读取每一张图片保存到images下  -->>枚举 （0,'<InMemoryUploadedFile: 3.jpg (image/jpeg)>'）
        for index, image_obj in enumerate(userfiles):
            image_type = image_obj.name.rsplit('.', 1)[
                1]  # 取出健康报告格式（jpg、png等）,[1]:表示从后面分割1个出来（jpg、png等），如果是2，那么就是分割两部分出来
            path = 'adminoo/static/images/reports/{}_{}.{}'.format(report_num, index, image_type)  # 图片路径、图片名称
            ## 保存图片
            # wb:以二进制格式打开一个文件只用于写入。如果该文件已存在则将其覆盖。如果该文件不存在，创建新文件。
            with open(path, mode='wb') as f:
                for content in image_obj.chunks():
                    f.write(content)  # 将字符串写入文件

            # 2.保存图片路径到数据库,下次使用时直接从数据库里取路径和名称就行
            obj_image = models.Image()
            path1 = 'images/reports/{}_{}.{}'.format(report_num, index, image_type)
            obj_image.img_address = path1
            obj_image.img_label = image_obj.name  # 图片原名称
            obj_image.reports = report_obj  # 设置图片和报告的关系
            obj_image.save()
            # 3.重定向到报告列表
        return render(request, 'base_user.html', {'ret': ret})


def report_list(request, page=1):
    """健康报告列表"""
    if request.method == "GET":
        # 我们要把健康报告的数据库中的数据全部取出，传给前端进行显示
        report_obj_list = models.Report.objects.all()
        paginator = Paginator(report_obj_list, 5)  # 实例化分页对象，每页显示8条数据
        total_page_num = paginator.num_pages  # 总页码
        current_page_num = page  # 当前页，默认显示第一页
        report_page_objs = paginator.page(current_page_num)  # 获取当页面的数据对象，用于响应前端请求进行渲染显示
        page_range = paginator.page_range  # 确定页面范围，以便进行模板渲染使用页码
        # 当前页
        if total_page_num > 10:  # 当总页码大于10时
            if current_page_num < 9:  # 当前页小于10时
                page_range = range(1, 11)
            elif current_page_num + 8 > total_page_num:  # 当前页码是倒数第8页时
                page_range = range(current_page_num - 2, total_page_num + 1)
            else:
                page_range = range(current_page_num - 2, current_page_num + 8)

        return render(request, "report_list.html", locals())


def update_report(request):
    """修改健康报告"""
    if request.method == "GET":
        # 1.获取report_list.html页面传过来的id
        report_id = request.GET.get("id")
        # 2.从数据库中获取要修改的健康报告对象
        report_obj = models.Report.objects.get(id=report_id)
        # 3. 获取所有的专业数据,传到前端用来选择专业。
        profession_list = models.Profession.objects.all()
        return render(request, "report_update.html", locals())

    else:
        # TODO:缺少修改图片选项
        # 获取report_update.html表单提交过来的数据
        report_id = request.POST.get("id")
        report_name = request.POST.get("name")
        report_age = request.POST.get("report_age")
        report_address = request.POST.get("report_address")
        report_phone = request.POST.get("report_phone")
        # report_inventory = request.POST.get("report_inventory")
        report_temperature = request.POST.get("report_temperature")
        report_time = request.POST.get("report_time")
        report_description = request.POST.get("report_description")
        # report_sales = request.POST.get("report_sales")
        # comment_nums = request.POST.get("comment_nums")
        profession_id = request.POST.get("profession")  # 专业id
        profession_obj = models.Profession.objects.get(id=profession_id)  # 专业对象
        # 将表单提交过来的数据保存到数据库
        report_obj = models.Report.objects.filter(id=report_id).update(
            name=report_name,
            report_age=report_age,
            report_address=report_address,
            report_phone=report_phone,
            # report_inventory=report_inventory,
            report_temperature=report_temperature,
            report_description=report_description,
            report_time=report_time,
            # report_sales=report_sales,
            # comment_nums=comment_nums,
            profession=profession_obj,
        )
        # 重定向到健康报告列表页面
        return redirect("/adminoo/report_list")


def delete_report(request):
    #  1. 获取report_list.html传来的id
    report_id = request.GET.get("id")
    # 2. 根据id，从数据库中获取专业对象并且删除
    models.Report.objects.get(id=report_id).delete()
    # 3.  删除数据后返回到专业列表页面。
    return redirect("/adminoo/report_list/")


def add_teacher(request):
    """添加负责人"""
    if request.method == "GET":
        # 1. 获取所有专业，返回到前端然后循环显示专业
        profession_obj_list = models.Profession.objects.all()
        # 2. 返回作者添加页面
        return render(request, "teacher_add.html", locals())

    elif request.method == "POST":
        teacher_name = request.POST.get("teacher_name")
        profession_id = request.POST.get("profession_id")
        teacher_phone = request.POST.get("teacher_phone")
        teacher_card = request.POST.get("teacher_card")
        # 将作者添加到数据库
        teacher_obj = models.Teacher.objects.create(teacher_name=teacher_name, teacher_phone=teacher_phone,
                                                    teacher_card=teacher_card)
        teacher_obj.profession.set(profession_id)  # 设置作者和图书的关系，进行关联
        return redirect("/adminoo/teacher_list")


def teacher_list(request, page=1):
    # 第一种方法：
    # teacher_obj_list = models.Author.objects.all()
    # bk = Paginator(teacher_obj_list, 5)
    # num = bk.num_pages
    # page = bk.page(page)

    # 第二种方法
    # 我们要把负责人的数据库中的数据全部取出，传给前端进行显示
    teacher_obj_list = models.Teacher.objects.all()
    res_lst = []  # 字典，用来存放图书和作者信息,传值给前端
    for teacher_obj in teacher_obj_list:
        profession_obj_list = teacher_obj.profession.all()  # 获取每个作者的所有图书，添加到字典里面
        print(profession_obj_list)
        res_dic = {
            "teacher_obj": teacher_obj,  # 负责人对象
            "profession_obj_list": profession_obj_list,  # 每个作者的图书列表
        }
        res_lst.append(res_dic)
        ####### 分页 #######
    paginator = Paginator(res_lst, 5)  # 实例化分页对象，每页显示5条数据
    total_page_num = paginator.num_pages  # 总页码
    current_page_num = page  # 当前页，默认显示第一页
    teacher_page_objs = paginator.page(current_page_num)  # 获取当页面的数据对象，用于响应前端请求进行渲染显示
    page_range = paginator.page_range  # 确定页面范围，以便进行模板渲染使用页码
    # 页码范围
    if total_page_num > 10:  # 当总页码大于10时
        if current_page_num < 9:  # 当前页小于10时
            page_range = range(1, 11)
        elif current_page_num + 8 > total_page_num:  # 当前页码是倒数第8页时
            page_range = range(current_page_num - 2, total_page_num + 1)
        else:
            page_range = range(current_page_num - 2, current_page_num + 8)

    return render(request, "teacher_list.html", locals())


def update_teacher(request):
    """"""
    if request.method == "GET":
        teacher_id = request.GET.get("id")
        teacher_obj = models.Teacher.objects.get(id=teacher_id)
        # 查询所有图书
        profession_obj_list = models.Profession.objects.all()
        return render(request, "teacher_update.html", locals())

    else:
        # 保存修改的数据
        teacher_id = request.POST.get("id")
        teacher_name = request.POST.get("teacher_name")
        teacher_card = request.POST.get("teacher_card")
        teacher_phone = request.POST.get("teacher_phone")
        profession_id = request.POST.get("profession")
        # 根据id，查找对象并修改
        teacher_obj = models.Teacher.objects.filter(id=teacher_id).first()
        # print(teacher_obj)
        teacher_obj.teacher_name = teacher_name
        teacher_obj.teacher_card = teacher_card
        teacher_obj.teacher_phone = teacher_phone
        teacher_obj.profession.set(profession_id)
        teacher_obj.save()
        # 重定向到作者列表
        return redirect("/adminoo/teacher_list")


def delete_teacher(request):
    teacher_id = request.GET.get("id")
    teacher = models.Teacher.objects.get(id=teacher_id)
    teacher.delete()
    return redirect("adminoo:teacher_list")


def add_user(request):
    """添加学生"""
    if request.method == "GET":
        # 查询所有的
        profession_obj_list = models.Profession.objects.all()
        # 将页面转跳到用户添加页面，并把数据传给前端
        return render(request, "user_add.html", locals())

    else:
        # 获取表单提交过来的用户信息
        name = request.POST.get("name")
        nickname = request.POST.get("nickname")
        sex = request.POST.get("sex")
        card = request.POST.get("card")
        phone = request.POST.get("phone")
        time = request.POST.get("time")
        profession_id = request.POST.get("profession_id")
        profession_obj = models.Profession.objects.get(id=profession_id)  # 专业对象
        password = request.POST.get("password")
        # 对密码进行加密
        password = pwd_encrypt(password)
        # 将用户信息保存数据库中
        user_obj = models.User.objects.create(
            name=name,
            nickname=nickname,
            sex=sex,
            card=card,
            password=password,
            phone=phone,
            time=time,
            profession=profession_obj,
        )

        return redirect("/adminoo/user_list")


def user_list(request, page=1):
    """学生列表"""
    # data_dict = {}  # 设一个空字典
    # value = request.GET.get("res1", "")
    # if value:  # 用户通过url传入关键字，只有输入了关键字不为空了，才往字典里写入这个值
    #     # data_dict = {"username__contains": value}
    #     data_dict['username__contains'] = value
    # # 根据关键字，去数据库获取
    # queryset = models.Admin.objects.filter(**data_dict)
    user_obj_list = models.User.objects.all()
    paginator = Paginator(user_obj_list, 5)  # 实例化分页对象，每页显示10条数据
    total_page_num = paginator.num_pages  # 总页码
    current_page_num = page  # 当前页，默认显示第一页
    user_page_objs = paginator.page(current_page_num)  # 获取当页面的数据对象，用于响应前端请求进行渲染显示
    page_range = paginator.page_range  # 确定页面范围，以便进行模板渲染使用页码
    # 当前页
    if total_page_num > 10:  # 当总页码大于10时
        if current_page_num < 9:  # 当前页小于10时
            page_range = range(1, 11)
        elif current_page_num + 8 > total_page_num:  # 当前页码是倒数第8页时
            page_range = range(current_page_num - 2, total_page_num + 1)
        else:
            page_range = range(current_page_num - 2, current_page_num + 8)

    return render(request, "user_list.html", locals())


def update_user(request):
    """修改学生"""
    if request.method == "GET":
        user_id = request.GET.get("id")
        user_obj = models.User.objects.get(id=user_id)
        profession_obj_list = models.Profession.objects.all()
        return render(request, "user_update.html", locals())
    else:
        user_id = request.POST.get("id")
        # user_name = request.POST.get("name")
        # card = request.POST.get("card")
        phone = request.POST.get("phone")
        nick_name = request.POST.get("nickname")
        sex = request.POST.get("sex")
        password = request.POST.get("password")
        profession_id = request.POST.get("profession_id")
        profession_obj = models.Profession.objects.get(id=profession_id)  # 专业对象
        # .对密码进行加密
        password = pwd_encrypt(password)
        # 根据id，查找对象并修改
        # user_obj = models.User.objects.filter(id=user_id).first()
        # user_obj.password = password
        # user_obj.nick_name = nick_name
        # user_obj.phone = phone
        # user_obj.save()
        # user_obj.profession.set(profession_id)  # 设置用户与时间的关系
        # 更新数据库的另一个方法
        user_obj = models.User.objects.filter(id=user_id).update(
            # name=user_name,
            password=password,
            nickname=nick_name,
            sex=sex,
            phone=phone,
            # card=card,
            profession=profession_obj,
        )

        return redirect("/adminoo/user_list")


def delete_user(request):
    """删除学生"""
    user_id = request.GET.get("id")
    models.User.objects.get(id=user_id).delete()
    return redirect("adminoo:user_list")


def search(request):
    """查询"""
    # 从前端中获取用户输入的关键字
    search_keywords = request.POST.get("search_keywords", "")
    # print(search_keywords)
    # 如果前端有数据传来则执行查询语句，如果为空则返回"你输入的信息错误,请重新出入"
    if search_keywords:
        # Q对象是Django对model查询中所使用的关键字参数进行封装后的一个对象。
        # Q对象可以通过 &（与）、 |（或）、 ~（非）运算来组合生成不同的Q对象，便于在查询操作中灵活地运用
        # icontains是表示模糊匹配, 主要还有个 contains，两者区别是是否区分大小写。
        # college_obj_list = models.College.objects.filter(
        #     Q(college_name__icontains=search_keywords)
        #     # Q(profession__icontains=search_keywords)
        # )
        # 健康报告查询
        report_obj_list = models.Report.objects.filter(
            Q(name__icontains=search_keywords) |
            Q(report_num__icontains=search_keywords)
            # Q(profession__icontains=search_keywords)
        )
        # 专业查询
        profession_obj_list = models.Profession.objects.filter(
            Q(name__icontains=search_keywords)
            # Q(teacher__icontains=search_keywords)
        )
        # 专业查询
        teacher_obj_list = models.Teacher.objects.filter(
            Q(teacher_name__icontains=search_keywords) |
            Q(teacher_card__icontains=search_keywords)
            # Q(teacher__icontains=search_keywords)
        )
        # 用户查询
        users_obj_list = models.User.objects.filter(
            Q(name__icontains=search_keywords) |
            Q(card__icontains=search_keywords)
            # Q(profession__icontains=search_keywords)
        )
        # 判断查询结果，用来控制前端页面绘制
        if len(report_obj_list) != 0:  # 如果能查询到（不为空：有结果），前端显示报告查询结果
            report_search_result = True  # 方便前端使用if或for语言，来控制搜索查询页面
        elif len(teacher_obj_list) != 0:  # 如果能查到，前端显示学院查询结果
            teacher_search_result = True
        elif len(profession_obj_list) != 0:  # 如果能查到，前端显示专业查询结果
            profession_search_result = True
        elif len(users_obj_list) != 0:
            user_search_result = True  # 如果能查到，前端显示用户信息
        else:
            error_msg = "没有查询到结果，请重新输入"
    else:
        error_msg = "你输入的信息错误,请重新出入"
    return render(request, "search_result.html", locals())
