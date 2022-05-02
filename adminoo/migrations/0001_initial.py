# Generated by Django 3.2.12 on 2022-04-21 11:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Adminoo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, verbose_name='用户名')),
                ('nickname', models.CharField(max_length=32, verbose_name='昵称')),
                ('password', models.CharField(max_length=32, verbose_name='密码')),
            ],
        ),
        migrations.CreateModel(
            name='College',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=32, null=True, verbose_name='学院名称')),
            ],
        ),
        migrations.CreateModel(
            name='Profession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, verbose_name='专业名称')),
                ('teacher', models.CharField(max_length=128, verbose_name='专业负责人')),
                ('college', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='adminoo.college', verbose_name='学院名称')),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, verbose_name='用户名')),
                ('nickname', models.CharField(max_length=32, verbose_name='用户昵称')),
                ('sex', models.CharField(default='男', max_length=32, verbose_name='性别')),
                ('card', models.CharField(blank=True, max_length=32, null=True, verbose_name='学生学号')),
                ('password', models.CharField(max_length=32, verbose_name='密码')),
                ('phone', models.CharField(max_length=11, verbose_name='电话号码')),
                ('time', models.DateTimeField(auto_now=True, verbose_name='时间')),
                ('profession', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='adminoo.profession', verbose_name='专业')),
            ],
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('teacher_name', models.CharField(max_length=32, verbose_name='负责人姓名')),
                ('teacher_card', models.CharField(blank=True, max_length=32, null=True, verbose_name='负责人工号')),
                ('teacher_phone', models.CharField(blank=True, max_length=11, null=True, verbose_name='电话号码')),
                ('profession', models.ManyToManyField(related_name='teacher_profession', to='adminoo.Profession', verbose_name='专业')),
            ],
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, verbose_name='上报用户名')),
                ('report_num', models.CharField(blank=True, max_length=128, null=True, verbose_name='健康上报编码')),
                ('report_address', models.CharField(max_length=128, verbose_name='上报地址')),
                ('report_age', models.CharField(max_length=128, verbose_name='上报年龄')),
                ('report_phone', models.CharField(max_length=11, verbose_name='电话号码')),
                ('report_temperature', models.CharField(max_length=128, verbose_name='体温')),
                ('report_description', models.TextField(verbose_name='身体状况')),
                ('report_time', models.DateTimeField(auto_now=True, verbose_name='上报时间')),
                ('profession', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='adminoo.profession', verbose_name='专业名称')),
            ],
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('img_address', models.ImageField(upload_to='', verbose_name='图片路径')),
                ('img_label', models.CharField(max_length=128, verbose_name='上报健康码')),
                ('reports', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='adminoo.report', verbose_name='上报')),
            ],
        ),
    ]
