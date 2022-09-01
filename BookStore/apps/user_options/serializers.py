import re
from rest_framework import serializers
from user_options.models import user_leave_message, user_address


# 用户信息修改的序列化器
class user_update_serializer(serializers.Serializer):
    # 字段信息
    name = serializers.CharField(max_length=30, allow_null=True, label='姓名')
    gender = serializers.CharField(max_length=6, default="man", label='性别')
    mobile = serializers.CharField(max_length=11, allow_null=True, label='手机号')
    email = serializers.EmailField(max_length=100, allow_null=True, label='邮箱')
    birthday = serializers.DateField(allow_null=True, label='生日')

    # 用户的验证
    def validate(self, attrs):
        # 验证用户名(手机号)
        if not re.match(r'^1[3-9]\d{9}', attrs.get('mobile')):
            raise serializers.ValidationError('用户名错误，应该用手机号作为用户名')

        # 验证电子邮箱格式
        user_email = attrs.get('email')
        regex = r'[a-zA-Z].*@qq.com|[0-9]{5,11}@qq.com|[a-zA-Z].*@163.com'
        if not re.match(regex, user_email):
            raise serializers.ValidationError('邮箱格式错误，请重新输入')

        return attrs

    # 修改用户信息
    def update(self, instance, validated_data):
        # 如果传递的是部分内容，没有获取到数据的字段不做修改
        instance.name = validated_data.get('name')
        instance.gender = validated_data.get('gender')
        instance.mobile = validated_data.get('mobile')
        instance.email = validated_data.get('email')
        instance.birthday = validated_data.get('birthday')
        instance.save()
        return instance


# 用户留言的序列化器定义
class user_leave_message_serializer(serializers.Serializer):
    # 字段信息
    id = serializers.IntegerField(label='留言ID', read_only=True)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    add_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M')
    message_type = serializers.IntegerField(label='留言类型')
    subject = serializers.CharField(label='主题', max_length=32)
    message = serializers.CharField(label='留言内容', max_length=1024)
    file = serializers.FileField(label='上传文件', allow_empty_file=True, allow_null=True)

    # 创建一条留言
    def create(self, validated_data):
        user_leave_message.objects.create(**validated_data)
        return validated_data


# 用户收货地址的序列化器
class user_address_serializer(serializers.ModelSerializer):
    # 字段定义
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    add_time = serializers.DateTimeField(read_only=True, format='%Y-%m-%d %H:%M')

    class Meta:
        model = user_address
        fields = '__all__'
