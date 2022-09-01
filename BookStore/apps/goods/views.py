from django.shortcuts import render
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from goods.filters import goods_filter
from goods.models import goods_category, goods, hot_search_words, banner
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.pagination import PageNumberPagination
from goods.serializers import goods_category_serializer, goods_serializer, goods_detail_serializer
from goods.serializers import hot_search_words_serializer, index_category_serializer, banner_serializer
from django_filters.rest_framework import DjangoFilterBackend

# 商品分类的视图
# class goods_category_view(ListAPIView):
#     queryset = goods_category.objects.all()
#     serializer_class = goods_category_serializer


# 商品分类的视图
class goods_category_view(ModelViewSet):
    queryset = goods_category.objects.all()
    serializer_class = goods_category_serializer


# 自定义商品的分页类
class goods_pagination(PageNumberPagination):
    page_size = 12      # 一页显示12条数据
    page_size_query_param = 'page_size'   # 分页的参数值
    page_query_param = 'page'   # 指定分多少页的参数
    max_page_size = 100         # 最多分多少页


# 商品搜索的视图
class goods_list_view(ListAPIView):
    queryset = goods.objects.all()
    serializer_class = goods_serializer
    # 调用自定义的分页类
    pagination_class = goods_pagination

    # 对搜索到的所有商品进行过滤 需要安装 django-filter （filter没有s）
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    # 设置过滤字段
    search_fields = ('name', 'goods_brief', 'goods_desc')

    # 使用自定义的过滤类 【新增】
    filter_class = goods_filter

    # 重写ListAPIView中的list方法，用于生成热搜词
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)

        if page is not None:
            if request.GET.get('search'):
                # 如果用户搜索的热搜词在数据库中存在
                data = hot_search_words.objects.filter(keywords=request.GET.get('search'))
                # 取出查询集中的热搜词对象
                ins = data.first()

                # 当存在用户搜索的热搜词,就给这个热搜词的搜索次数+1
                if data:
                    ins.index += 1
                    ins.save()
                else:
                    hot_search_words.objects.create(keywords=request.GET.get('search'), index=0)

            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


# 商品热搜词的视图
class hot_search_words_view(ListAPIView):
    queryset = hot_search_words.objects.all()
    serializer_class = hot_search_words_serializer


# 主页商品的视图
class index_goods_view(ListAPIView):
    queryset = goods_category.objects.filter(name__in=['文学类'])
    serializer_class = index_category_serializer


# 商品轮播图的视图
class banner_view(ListAPIView):
    queryset = banner.objects.all()
    serializer_class = banner_serializer


# 商品详情页的视图
class goods_detail_view(ListAPIView):
    queryset = goods.objects.all()
    serializer_class = goods_detail_serializer

    # 重写ListAPIView里的list方法
    def list(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        goods = self.get_queryset().filter(id=pk).first()

        serializer = self.get_serializer(goods)

        response = serializer.data
        response['images'] = 'http://192.168.159.136:8000/media/goods/images/image.png'
        return Response(response)
