import random
from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework_jwt.settings import api_settings

from celery_tasks.sms.tasks import send_sms_code
from users.models import verify_code, user_token, user_favorite
from django_redis import get_redis_connection
from users.serializers import verify_code_serializer, user_register_serializer, login_serializer, \
    user_favorite_serializer, user_favorite_detail_serializer


# 短信验证码的视图
class verify_code_view(APIView):

    # 定义一个生成随机验证码的函数
    def get_verify_code(self):
        number = '0123456789'   # 随机数生成的种子
        random_code = ''
        for i in range(4):
            random_code += random.choice(number)    # 循环四次生成四位数的随机验证码
        return random_code

    # 验证码校验视图
    def post(self, request, *args, **kwargs):
        # 获取前端传递的手机号和生成的验证码
        data = request.data
        mobile = data.get('mobile')     # 确定发给哪个用户
        code = self.get_verify_code()   # 确定发送什么内容

        # 校验手机号码格式
        serializer = verify_code_serializer(data=data)
        serializer.is_valid(raise_exception=True)

        # 使用云通讯来发送短信验证码，如果发送成功返回0，如果发送失败返回-1
        # result = CCP().send_template_sms(mobile, [code, 5], 1)
        # result = 0      # 测试，默认云通讯发送成功

        # 使用异步任务来发送短信验证码
        send_sms_code.delay(mobile, code)

        # 判定云通讯短信是否发送成功
        # if result != 0:
        #     return Response({"mobile": "验证码发送失败"}, status=status.HTTP_400_BAD_REQUEST)
        # else:

        verify_code.objects.create(mobile=mobile, code=code)    # 创建验证码对象
        redis_conn = get_redis_connection('verify_codes')       # 实例化一个redis连接对象
        redis_pipeline = redis_conn.pipeline()   # 实例化redis管道对象
        redis_pipeline.setex('sms_%s' % mobile, 300, code)      # 设置存储的键值对数据
        redis_pipeline.execute()            # 提交保存
        return Response({"mobile": "验证码发送成功"}, status=status.HTTP_201_CREATED)


# 用户注册视图
class register_view(APIView):
    def post(self, request):
        serializer = user_register_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # serializer.save()

        # 获取注册所生成的用户
        user = serializer.save()

        # 生成jwt信息
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        # 创建token并存储到数据库中
        user_token.objects.create(user=user, token=token)

        # 将生成的jwt返回给前端
        dic = serializer.validated_data
        dic['token'] = token    # 往字典中添加token数据
        headers = {'Authorization': 'Bearer %s' % token}

        # return Response({'message': '注册成功'}, status=status.HTTP_201_CREATED)
        return Response(dic, headers=headers, status=status.HTTP_201_CREATED)

    # 定义get方法，用于前端获取用户的信息展示出来
    def get(self, request):
        user = request.user

        serializer = login_serializer(user)
        data = serializer.data
        data['mobile'] = user.username
        return Response(data)


# 用户收藏的视图
class user_favorite_view(ModelViewSet):
    queryset = user_favorite.objects.all()
    serializer_class = user_favorite_serializer
    authentication_classes = [JSONWebTokenAuthentication]

    # 在 ModelViewSet 中涉及到pk值的操作
    lookup_field = 'goods_id'

    # 通过当前用户从所有用户收藏数据表中获取当前用户的收藏信息
    def get_queryset(self):
        return user_favorite.objects.filter(user=self.request.user)

    # 根据action动作来判断不同序列化器的调用
    def get_serializer_class(self):
        # list对应的是get请求，用于查询，调用已收藏的序列化器
        if self.action == 'list':
            return user_favorite_detail_serializer

        # create对应的是post请求，用于创建，调用未收藏的序列化器
        if self.action == 'create':
            return user_favorite_serializer

        return user_favorite_serializer
