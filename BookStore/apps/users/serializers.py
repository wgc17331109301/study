import re
import datetime
from goods.serializers import goods_serializer
from rest_framework import serializers
from django_redis import get_redis_connection
from django.contrib.auth import get_user_model
from users.models import user_info, verify_code, user_favorite
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator


# 短信验证码的序列化器
class verify_code_serializer(serializers.Serializer):
    # 手机号字段
    mobile = serializers.CharField(max_length=11)

    # 校验短信验证码模型类的数据
    def validated_mobile(self, mobile):

        # 手机号是否已注册
        if user_info.objects.filter(mobile=mobile).count():
            raise serializers.ValidationError("用户已经存在")

        # 验证手机号格式是否正确
        if not re.match(r'^1[3-9]\d{9}', mobile):
            raise serializers.ValidationError("手机号码格式错误")

        # 短信验证码的发送频率
        one_minutes_ago = datetime.datetime.now() - datetime.timedelta(hours=0, minutes=1, seconds=0)

        # 验证短信一分钟内是否重复发送
        if verify_code.objects.filter(add_time__gt=one_minutes_ago, mobile=mobile).count():
            raise serializers.ValidationError("距离上一次发送时间未超过60秒")

        return mobile


# 获取用户的模型，认证的模型对象
User = get_user_model()


# 用户注册的序列化器
class user_register_serializer(serializers.Serializer):
    # 字段信息
    username = serializers.CharField(label='用户名', required=True,
         validators=[UniqueValidator(queryset=User.objects.all(), message="用户已存在")])
    password = serializers.CharField(label='密码', style={'input_type': 'password'}, write_only=True)
    code = serializers.CharField(label='验证码', required=True, write_only=True,
            max_length=4, min_length=4, error_messages={
                                            'blank': '请输入验证码',
                                            'required': '请输入验证码',
                                            'max_length': '验证码格式错误',
                                            'min_length': '验证码格式错误',
                                         })

    # 信息校验
    def validate(self, attrs):
        # 获取手机号(前端手机号绑死了username字段)和验证码
        mobile = attrs.get('username')
        redis_conn = get_redis_connection('verify_codes')   # 先连接到redis
        code = redis_conn.get('sms_%s' % mobile).decode()   # 从redis中取出验证码

        # 验证码的格式验证
        if len(attrs.get('code')) != 4:
            raise serializers.ValidationError('验证码格式错误')
        # 验证码是否有效
        if not code:
            raise serializers.ValidationError('验证码已过期')
        # 验证码是否正确
        if attrs.get('code') != code:
            raise serializers.ValidationError('验证码错误')
        # 验证密码的长度
        if len(attrs.get('password')) < 6 or len(attrs.get('password')) > 20:
            raise serializers.ValidationError('密码长度不正确，应该为6-20位')
        # 验证密码的组成格式
        if not attrs.get('password').isalnum():
            raise serializers.ValidationError('密码应该由字母和数字组成')
        # 验证密码
        if not re.match(r'[a-zA-Z]{1,19}\d+', attrs.get('password')):
            raise serializers.ValidationError('密码不正确')

        return attrs

    # 创建用户对象
    def create(self, validated_data):
        del validated_data['code']      # 删除验证码信息
        # user = User.objects.create(**validated_data)    # 创建用户
        user = User(**validated_data)
        user.set_password(user.password)
        user.save()
        return user

    class Meta:
        model = User
        fields = '__all__'


# 用户登录的序列化器
class login_serializer(serializers.ModelSerializer):
    # 字段信息
    username = serializers.CharField(label='用户名', required=True, allow_blank=False)
    password = serializers.CharField(label='密码', style={'input_type': 'password'}, write_only=True)

    # 校验数据
    def validate(self, attrs):
        # 获取用户名（手机号）
        mobile = attrs.get('username')

        # 判断手机号码格式
        if not re.match(r'^1[3-9]\d{9}', mobile):
            raise serializers.ValidationError('用户名（手机号）不合法，请重新输入')

        # 验证密码的长度
        if len(attrs.get('password')) < 6 or len(attrs.get('password')) > 20:
            raise serializers.ValidationError('密码长度不正确，应该为6-20位')

        # 验证密码的组成格式
        if not attrs.get('password').isalnum():
            raise serializers.ValidationError('密码应该由字母和数字组成')

        # 验证密码
        if not re.match(r'[a-zA-Z]{1,19}\d+', attrs.get('password')):
            raise serializers.ValidationError('密码不正确')

        return attrs

    class Meta:
        model = User
        fields = '__all__'


# 用户已收藏商品的序列化器
class user_favorite_detail_serializer(serializers.ModelSerializer):
    # 对商品数据进行序列化，得到商品对象
    goods = goods_serializer()

    class Meta:
        model = user_favorite
        fields = '__all__'


# 用户未收藏商品的序列化器
class user_favorite_serializer(serializers.ModelSerializer):
    # 指定当前默认的用户
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = user_favorite

        # 使用validate的方式实现唯一联合
        validators = [
            UniqueTogetherValidator(
                queryset=user_favorite.objects.all(),
                fields=('user', 'goods'),
                message='已经收藏'
            )
        ]

        fields = '__all__'
