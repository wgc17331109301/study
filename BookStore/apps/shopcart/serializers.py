import time
from random import Random
from django.db import transaction
from alipay import AliPay, AliPayConfig
from goods.models import goods
from BookStore.settings import ALIPAY_APPID, app_private_key_string, alipay_public_key_string, ALIPAY_URL
from shopcart.models import shop_cart, order_goods, order_info
from rest_framework import serializers
from goods.serializers import goods_serializer


# 购物车已添加的序列化器
class shop_cart_detail_serializer(serializers.ModelSerializer):
    goods = goods_serializer()

    class Meta:
        model = shop_cart
        fields = '__all__'


# 购物车未添加的序列化器
class shop_cart_serializer(serializers.Serializer):
    # 模型对应的字段
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    goods = serializers.PrimaryKeyRelatedField(required=True, queryset=goods.objects.all())
    nums = serializers.IntegerField(required=True, label='数量', min_value=1,
                                    error_messages={
                                        "min_value": "商品数量不能小于1",
                                        "required": "请选择购买数量"
                                    })

    # 重写create方法, 增加购物车中的商品信息
    def create(self, validated_data):
        user = self.context["request"].user
        nums = validated_data["nums"]
        goods = validated_data["goods"]

        # 查询当前用户的购物车数据
        exits = shop_cart.objects.filter(user=user, goods=goods)

        # 当购物车信息存在，在原有商品数量的基础上增加商品数量的值
        if exits:
            ins = exits.first()
            ins.nums += nums
            ins.save()
        # 购物车信息不存在，创建一个购物车信息
        else:
            ins = shop_cart.objects.create(**validated_data)

        return ins

    # 重写 update 方法, 修改购物车中商品的数量
    def update(self, instance, validated_data):
        # 修改商品数量
        instance.nums = validated_data["nums"]
        instance.save()
        return instance


# 订单已存在，且订单中只有一个商品
class order_goods_one_serializer(serializers.ModelSerializer):
    goods = goods_serializer(many=False)

    class Meta:
        model = order_goods
        fields = '__all__'


# 订单已存在，但订单中有多个商品
class order_goods_serializer(serializers.ModelSerializer):
    goods = order_goods_one_serializer(many=True)

    class Meta:
        model = order_info
        fields = '__all__'


# 订单不存在，需要创建一个订单信息
class order_create_serializer(serializers.ModelSerializer):
    # 字段信息
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    pay_status = serializers.CharField(label='订单状态', read_only=True)
    order_sn = serializers.CharField(label='订单编号', read_only=True)
    create_time = serializers.DateTimeField(label='创建时间', read_only=True)

    # 支付宝交易号字段【新增】
    trade_on = serializers.CharField(label='交易号', read_only=True)
    # 支付宝的请求接口【新增】
    alipay_url = serializers.SerializerMethodField(read_only=True)

    # 获取支付宝支付的路由【新增】
    def get_alipay_url(self, obj):
        # 实例
        alipay = AliPay(
            appid=ALIPAY_APPID,
            app_private_key_string=app_private_key_string,
            alipay_public_key_string=alipay_public_key_string,
            sign_type='RSA2',       # 指定加密方式，一般为RSA或RSA2
            config=AliPayConfig(timeout=15),  # 等待时间15秒
        )

        # 订单信息
        order_string = alipay.api_alipay_trade_wap_pay(
            out_trade_no=obj.order_sn,      # 订单编号
            total_amount=obj.order_mount,   # 订单金额
            subject='二手书商城订单:%s' % obj.order_sn,    # 订单主题
            return_url='http://192.168.136.148:8000/alipay/return/',  # 支付后返回的页面
            ontify_url='http://example.com/notify',      # 可选
        )

        alipay_url = ALIPAY_URL + '?' + order_string
        return alipay_url

    # 创建订单编号，规则是 创建时间+用户ID+随机数字
    def create_order_sn(self):
        random_ins = Random()
        order_sn = "{time_str}{user_id}{ran_str}".format(
            time_str=time.strftime("%Y%m%d%H%M%S"),
            user_id=self.context['request'].user.id,
            ran_str=random_ins.randint(10, 99)
        )
        return order_sn

    def validate(self, attrs):
        # 判定商品库存的数量
        user = self.context['request'].user
        user_shop_cart = user.shop_cart_set.all()

        # 开启事务
        with transaction.atomic():
            # 设置回档点
            save_id = transaction.savepoint()
            # 遍历购物车信息
            for shopping_cart in user_shop_cart:

                while True:
                    origin_nums = shopping_cart.goods.goods_num     # 原有的库存数量
                    new_nums = origin_nums - shopping_cart.nums     # 新的库存数量

                    if shopping_cart.nums > origin_nums:
                        transaction.savepoint_rollback(save_id)     # 事务回滚
                        raise serializers.ValidationError('商品库存不足')

                    # 如果库存足够，就修改原有的库存数量
                    res = goods.objects.filter(goods_num=origin_nums).update(goods_num=new_nums)

                    if res == 0:
                        continue
                    break

            # 提交事务
            transaction.savepoint_commit(save_id)

            # # 如果购物车中的商品数量大于商品的库存量
            # if shopping_cart.nums > shopping_cart.goods.goods_num:
            #     raise serializers.ValidationError('商品库存不足')

        attrs['order_sn'] = self.create_order_sn()
        return attrs

    class Meta:
        model = order_info
        fields = '__all__'
