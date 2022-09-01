from django.contrib.auth import get_user_model
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import UpdateAPIView, ListCreateAPIView, DestroyAPIView
from rest_framework.response import Response

from user_options.models import user_leave_message, user_address
from user_options.serializers import user_update_serializer, user_leave_message_serializer, user_address_serializer

# 获取认证的用户模型
User = get_user_model()


# 用户的信息修改
class user_update_view(UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = user_update_serializer

    def get_object(self):
        # 你登录哪个用户账号，我就给你修改哪个用户的信息
        return self.request.user


# 用户留言功能
class user_leave_message_view(ListCreateAPIView, DestroyAPIView):
    queryset = user_leave_message.objects.all()
    serializer_class = user_leave_message_serializer

    # 再次用户认证
    permission_classes = [IsAuthenticated]

    # 获取当前用户
    def get_object(self):
        return self.request.user

    # 因为list方法是返回所有人的留言信息，所以重写并限制只返回当前用户的留言
    def list(self, request, *args, **kwargs):
        queryset = self.queryset.filter(user_id=request.user.id).all()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    # 因为模型绑定了用户连带删除，所以可以单独重写删除操作
    def destroy(self, request, *args, **kwargs):
        message_id = kwargs.get('pk')
        self.queryset.filter(id=message_id).delete()
        return Response(status=204)


# 用户的收货地址视图
class user_address_view(ListCreateAPIView, DestroyAPIView, UpdateAPIView):
    # 指定查询集和序列化器
    queryset = user_address.objects.all()
    serializer_class = user_address_serializer

    # 用户认证
    permission_classes = [IsAuthenticated]

    # 获取当前用户
    def get_object(self):
        return self.request.user

    # 指定获取当前用户的收货地址，否则会获取所有人的收货地址信息（重写list方法）
    def list(self, request, *args, **kwargs):
        # 通过用户的ID来过滤查询到的所有用户的收货地址
        queryset = self.queryset.filter(user_id=request.user.id).all()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    # 修改用户的收货地址
    def update(self, request, *args, **kwargs):
        addr_id = kwargs.get('pk')      # 获取需要修改的收货地址ID
        data = request.data             # 获取前端传递过来的修改的内容

        # 获取需要修改的收货地址对象
        addr_obj = self.get_queryset().filter(id=addr_id)

        # 把前端传递过来的数据进行反序列化
        serializer = self.get_serializer(data=data, instance=addr_obj.first())
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'message': '用户收货地址更新成功'})

    # 删除用户的收货地址，需要重写 destroy 方法
    def destroy(self, request, *args, **kwargs):
        addr_id = kwargs.get('pk')

        addr_obj = self.get_queryset().filter(id=addr_id).delete()

        return Response({'message': '收货地址删除成功'})
