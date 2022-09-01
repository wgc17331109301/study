from django.db import models
from goods.models import goods
from django.contrib.auth.models import AbstractUser


# 继承Django自带的认证模型类，然后补充字段信息
class user_info(AbstractUser):
    # 性别字段参数的可选项
    GENDER_CHOICES = (
        ("man", u"男"),
        ("female", u"女")
    )
    # 补充的字段
    name = models.CharField(max_length=30, null=True, blank=True, verbose_name='姓名')
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES, default="man", verbose_name='性别')
    mobile = models.CharField(max_length=11, null=True, blank=True, verbose_name='手机号')
    email = models.EmailField(max_length=100, null=True, blank=True, verbose_name='邮箱')
    birthday = models.DateField(null=True, blank=True, verbose_name='生日')

    class Meta:
        verbose_name = '用户信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.username


# 短信验证码的模型类
class verify_code(models.Model):
    # 字段信息
    code = models.CharField(max_length=10, verbose_name='验证码')
    mobile = models.CharField(max_length=11, verbose_name='手机号')
    add_time = models.DateTimeField(auto_now=True, verbose_name='添加时间')

    class Meta:
        verbose_name = '短信验证码'
        verbose_name_plural = verbose_name
        ordering = ['-add_time']

    def __str__(self):
        return self.code


# 创建token模型
class user_token(models.Model):
    # 字段信息
    user = models.OneToOneField(user_info, on_delete=models.CASCADE, verbose_name='用户')
    token = models.CharField(max_length=255, verbose_name='用户令牌')

    class Meta:
        db_table = 'user_token'
        verbose_name = '用户令牌'
        verbose_name_plural = verbose_name


# 用户收藏的模型
class user_favorite(models.Model):
    # 字段
    user = models.ForeignKey(user_info, on_delete=models.CASCADE, verbose_name='用户')
    goods = models.ForeignKey(goods, on_delete=models.CASCADE, verbose_name='商品')
    add_time = models.DateTimeField(auto_now_add=True, verbose_name='添加时间')

    class Meta:
        verbose_name = '用户收藏'
        verbose_name_plural = verbose_name
        # 多个字段作为联合唯一索引，可以从user和goods两个对象来查询收藏表的数据
        unique_together = ('user', 'goods')

    def __str__(self):
        return self.user.username

