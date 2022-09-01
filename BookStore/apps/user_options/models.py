from django.db import models
from users.models import user_info


# 用户留言的模型类
class user_leave_message(models.Model):
    # 留言类型的选项
    MESSAGE_CHOICES = (
        (1, '留言'),
        (2, '投诉'),
        (3, '询问'),
        (4, '售后'),
        (5, '求购'),
    )

    # 模型字段
    user = models.ForeignKey(user_info, on_delete=models.CASCADE, verbose_name='用户')
    message_type = models.IntegerField(verbose_name='留言类型', choices=MESSAGE_CHOICES, default=1)
    subject = models.CharField(verbose_name='主题', max_length=32, default='')
    message = models.CharField(verbose_name='留言内容', max_length=1024, default='')
    file = models.FileField(verbose_name='上传文件', upload_to='message/images/', null=True)
    add_time = models.DateTimeField(auto_now=True, auto_created=True, verbose_name='添加时间')

    class Meta:
        db_table = 'user_leave_message'
        verbose_name = '用户留言'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.subject


# 用户收货地址的模型
class user_address(models.Model):
    # 设置字段
    user = models.ForeignKey(user_info, on_delete=models.CASCADE, verbose_name='用户')
    province = models.CharField(max_length=16, verbose_name='省份')
    city = models.CharField(max_length=16, verbose_name='城市')
    district = models.CharField(max_length=16, verbose_name='区域')
    address = models.CharField(max_length=64, verbose_name='详细地址')
    signer_name = models.CharField(max_length=20, default='', verbose_name='签收人')
    signer_mobile = models.CharField(max_length=11, default='', verbose_name='手机号')
    add_time = models.DateTimeField(auto_now=True, auto_created=True, verbose_name='添加时间')

    class Meta:
        db_table = 'user_address'
        verbose_name = '收货地址'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.address

