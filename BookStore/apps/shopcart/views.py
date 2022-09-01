from alipay import AliPay, AliPayConfig
from django.shortcuts import render, redirect
from rest_framework.response import Response
from rest_framework.views import APIView
from datetime import datetime
from BookStore.settings import ALIPAY_APPID, app_private_key_string, alipay_public_key_string
from shopcart.models import shop_cart, order_info, order_goods
from rest_framework.permissions import IsAuthenticated
from shopcart.serializers import shop_cart_serializer, shop_cart_detail_serializer
from shopcart.serializers import order_goods_serializer, order_create_serializer
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.viewsets import ModelViewSet


# 商品购物车的视图
class shop_cart_view(ModelViewSet):
    queryset = shop_cart.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [JSONWebTokenAuthentication]
    serializer_class = shop_cart_serializer

    # 商品的pk值
    lookup_field = 'goods_id'

    # 指定获取当前用户的购物车信息
    def get_queryset(self):
        return shop_cart.objects.filter(user=self.request.user)

    # 基于商品购物车是否存在来使用不同的序列化器
    def get_serializer_class(self):
        # list用于获取商品购物车信息，调用商品购物车详情的序列化器 （主要是用于查询）
        if self.action == 'list':
            return shop_cart_detail_serializer

        # 否则就是商品购物车信息不存在，调用创建商品购物车的序列化器 （主要是用于创建或修改）
        else:
            return shop_cart_serializer


# 清空购物车的视图
class shop_cart_clear_view(APIView):
    def post(self, request):
        user = request.user
        shop_cart.objects.filter(user=user).delete()
        return Response(status=204)


# 商品订单的视图
class order_view(ModelViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JSONWebTokenAuthentication]
    serializer_class = None

    # 获取当前用户的订单信息
    def get_queryset(self):
        return order_info.objects.filter(user=self.request.user)

    # 订单序列化器的判定
    def get_serializer_class(self):
        # 如果订单存在，调用订单的序列化器
        if self.action == 'retrieve':
            return order_goods_serializer

        # 如果订单不存在，调用订单创建的序列化器
        return order_create_serializer

    # 创建订单，支付完成之后，删除已购买的商品数据
    def perform_create(self, serializer):
        # 获取订单模型
        order = serializer.save()
        # 获取当前用户购物车中的数据信息
        user_shopping_cart = shop_cart.objects.filter(user=self.request.user)

        # 遍历用户购物车中的数据
        for shopping_cart in user_shopping_cart:
            user_order = order_goods()              # 商品订单
            user_order.goods = shopping_cart.goods  # 把购物车中的商品传给订单商品
            user_order.goods_num = shopping_cart.nums   # 把购物车中的商品数量传给订单商品数量

            # 刚刚报错的地方，没有添加这行代码
            user_order.order = order   # 把模型对象中的数据存储到订单中

            # 在购买支付之后，修改商品的销量和库存量
            # 库存数量 = 库存数量 - 购物车中的商品数量
            shopping_cart.goods.goods_num -= shopping_cart.nums
            # 商品销量 = 商品销量 + 购物车中的商品数量
            shopping_cart.goods.sold_num += shopping_cart.nums
            shopping_cart.goods.save()      # 保存修改后的结果

            user_order.save()                   # 保存商品订单信息
            shopping_cart.delete()              # 删除购物车信息

        return order


# 支付后修改订单状态的视图
class alipay_return_view(APIView):

    # 通过支付后的返回结果，验证是否支付成功
    def get(self, request):
        processed_dict = {}

        # 从alipay_url中循环遍历键值对
        for key, value in request.GET.items():
            processed_dict[key] = value

        # 取出密钥，在做交易号验证的时候使用，如果没有就为None
        sign = processed_dict.pop("sign", None)

        alipay = AliPay(
            appid=ALIPAY_APPID,
            app_private_key_string=app_private_key_string,
            alipay_public_key_string=alipay_public_key_string,
            sign_type='RSA2',
            config=AliPayConfig(timeout=15),
        )

        # 验证订单是否支付成功，传入的是订单信息processed_dict和密钥sign
        verify_result = alipay.verify(processed_dict, sign)

        # 判断是否支付成功
        if verify_result:
            order_sn = processed_dict.get('out_trade_no', None)     # 获取订单编号
            trade_on = processed_dict.get('trade_on', None)         # 获取交易号

            # 取出订单对象
            existed_order = order_info.objects.filter(order_sn=order_sn).first()

            # 通过订单对象修改订单数据
            existed_order.trade_on = trade_on           # 修改交易号
            existed_order.pay_status = 'TRADE_SUCCESS'  # 修改支付状态
            existed_order.pay_time = datetime.now()     # 修改支付时间
            existed_order.save()                        # 保存修改结果
            response = redirect('http://192.168.136.148')
            return response
        else:
            # 如果超时支付失败，修改订单状态
            order_sn = processed_dict.get('out_trade_no', None)  # 获取订单编号
            trade_on = processed_dict.get('trade_on', None)  # 获取交易号

            # 取出订单对象
            existed_order = order_info.objects.filter(order_sn=order_sn).first()

            # 通过订单对象修改订单数据
            existed_order.trade_on = trade_on  # 修改交易号
            existed_order.pay_status = 'TRADE_CLOSED'  # 修改支付状态
            existed_order.pay_time = datetime.now()  # 修改支付时间
            existed_order.save()  # 保存修改结果
            response = redirect('http://192.168.136.148')
            return response
