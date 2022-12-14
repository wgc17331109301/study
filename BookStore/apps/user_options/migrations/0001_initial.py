# Generated by Django 3.2.10 on 2022-03-29 12:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='user_leave_message',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('add_time', models.DateTimeField(auto_created=True, auto_now=True, verbose_name='添加时间')),
                ('message_type', models.IntegerField(choices=[(1, '留言'), (2, '投诉'), (3, '询问'), (4, '售后'), (5, '求购')], default=1, verbose_name='留言类型')),
                ('subject', models.CharField(default='', max_length=32, verbose_name='主题')),
                ('message', models.CharField(default='', max_length=1024, verbose_name='留言内容')),
                ('file', models.FileField(null=True, upload_to='message/images/', verbose_name='上传文件')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='用户')),
            ],
            options={
                'verbose_name': '用户留言',
                'verbose_name_plural': '用户留言',
                'db_table': 'user_leave_message',
            },
        ),
        migrations.CreateModel(
            name='user_address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('add_time', models.DateTimeField(auto_created=True, auto_now=True, verbose_name='添加时间')),
                ('province', models.CharField(max_length=16, verbose_name='省份')),
                ('city', models.CharField(max_length=16, verbose_name='城市')),
                ('district', models.CharField(max_length=16, verbose_name='区域')),
                ('address', models.CharField(max_length=64, verbose_name='详细地址')),
                ('signer_name', models.CharField(default='', max_length=20, verbose_name='签收人')),
                ('signer_mobile', models.CharField(default='', max_length=11, verbose_name='手机号')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='用户')),
            ],
            options={
                'verbose_name': '收货地址',
                'verbose_name_plural': '收货地址',
                'db_table': 'user_address',
            },
        ),
    ]
