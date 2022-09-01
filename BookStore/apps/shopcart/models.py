from django.db import models
from goods.models import goods
from django.contrib.auth import get_user_model


# 获取用户模型
User = get_user_model()


# 商品购物车的模型
class shop_cart(models.Model):
    # 字段
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    goods = models.ForeignKey(goods, on_delete=models.CASCADE, verbose_name='商品')
    nums = models.IntegerField(default=0, verbose_name='商品数量')
    add_time = models.DateTimeField(auto_now_add=True, verbose_name='添加时间')

    class Meta:
        verbose_name = '购物车'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '%s(%d)'.format(self.goods.name, self.nums)


# 订单的模型
class order_info(models.Model):
    # 支付的状态选项
    ORDER_STATUS = (
        ("TRADE_SUCCESS", "支付成功"),
        ("TRADE_CLOSED", "超时关闭"),
        ("WAIT_BUYER_PAY", "交易创建"),
        ("TRADE_FINISHED", "交易结束"),
        ("paying", "等待支付"),
    )

    # 支付的可选方式
    PAY_TYPE = (
        ("alipay", "支付宝"),
        ("wechat", "微信")
    )

    # 用户的字段信息
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')
    address = models.CharField(max_length=100, default='', verbose_name='收货地址')
    signer_name = models.CharField(max_length=20, default='', verbose_name='签收人')
    singer_mobile = models.CharField(max_length=11, verbose_name='联系电话')
    add_time = models.DateTimeField(auto_now_add=True, verbose_name='添加时间')

    # 订单的字段信息
    order_sn = models.CharField(max_length=30, null=True, blank=True, unique=True, verbose_name='订单号')
    trade_on = models.CharField(max_length=100, unique=True, null=True, blank=True, verbose_name='交易号')
    pay_status = models.CharField(choices=ORDER_STATUS, default='paying', max_length=30, verbose_name='订单状态')
    pay_type = models.CharField(choices=PAY_TYPE, default='alipay', max_length=10, verbose_name='支付方式')
    post_script = models.CharField(max_length=200, verbose_name='订单留言')
    order_mount = models.FloatField(default=0.0, verbose_name='订单金额')
    pay_time = models.DateTimeField(null=True, blank=True, verbose_name='支付时间')

    class Meta:
        verbose_name = '订单信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.order_sn


# 订单内商品的详情
class order_goods(models.Model):
    # 字段信息
    order = models.ForeignKey(order_info, on_delete=models.CASCADE, verbose_name='订单信息')
    goods = models.ForeignKey(goods, on_delete=models.CASCADE, verbose_name='商品')
    goods_num = models.IntegerField(default=0, verbose_name='商品数量')
    add_time = models.DateTimeField(auto_now_add=True, verbose_name='添加时间')

    class Meta:
        verbose_name = '订单商品'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.order.order_sn
