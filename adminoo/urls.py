# -*- coding:utf-8 -*-
"""
----------------------------------------------------------
作者: 武广辉
日期: 2022/4/19 14:43
----------------------------------------------------------
当前项目的名称: SchoolManagementSystem
在文件创建过程中在“新建文件”对话框中指定的新文件的名称: urls.py.py
当前集成开发环境: PyCharm
----------------------------------------------------------
"""
from django.urls import path, re_path
from adminoo import views

app_name = "adminoo"

urlpatterns = [
    path('register/', views.register),  # 注册功能
    path('register_user/', views.register_user),  # 注册功能
    path('login/', views.login),  # 登录功能
    path('logout/', views.logout),  # 注销功能
    path('add_profession/', views.add_profession),  # 添加出版社
    path('profession_list/', views.profession_list, name='profession_list'),  # 出版社列表
    path('profession_list/<int:page>', views.profession_list, name='profession_list'),  # 出版社列表(分页)
    path('update_profession/', views.update_profession, name='update_profession'),  # 修改出版社
    path('delete_profession/', views.delete_profession, name="delete_profession"),

    path('add_report/', views.add_report, name="add_report"),  # 添加上报信息
    path('add_report_userlogin/', views.add_report_userlogin, name="add_report_userlogin"),  # 添加上报信息
    path('add_report_userlogin/<int:card>', views.add_report_userlogin, name="add_report_userlogin"),  # 添加上报信息

    path('report_list/', views.report_list, name='report_list'),  # 上报列表
    path('report_list/<int:page>', views.report_list, name='report_list'),  # 带参数路由的上报列表（分页）

    path('update_report/', views.update_report, name='update_report'),  # 修改上报信息
    path('delete_report/', views.delete_report, name="delete_report"),

    path('add_teacher/', views.add_teacher, name="add_teacher"),  # 添加负责人
    path('teacher_list/', views.teacher_list, name='teacher_list'),  # 负责人列表
    path('teacher_list/<int:page>', views.teacher_list, name='teacher_list'),  # 负责人列表
    path('update_teacher/', views.update_teacher, name='update_teacher'),  # 修改出版社
    path('delete_teacher/', views.delete_teacher, name="delete_teacher"),

    path('add_user/', views.add_user, name="add_user"),  # 添加用户
    path('user_list/', views.user_list, name='user_list'),  # 用户列表
    path('user_list/<int:page>', views.user_list, name='user_list'),  # 带参数路由的用户列表（分页）
    path('update_user/', views.update_user, name='update_user'),  # 修改用户
    path('delete_user/', views.delete_user, name='delete_user'),  # 删除用户

    # path('index/', views.index, name='index'),  # 首页
    path('search/', views.search, name='search'),  # 查询

]