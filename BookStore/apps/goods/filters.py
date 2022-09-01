from django.db.models import Q
from goods.models import goods
from django_filters import rest_framework as filters


# 自定义的商品过滤类
class goods_filter(filters.FilterSet):
    # 字段
    pricemin = filters.NumberFilter(field_name='shop_price', lookup_expr='gte')
    pricemax = filters.NumberFilter(field_name='shop_price', lookup_expr='lte')
    top_category = filters.NumberFilter(field_name='category', method='top_category_filter')

    # 设置商品分类的返回
    def top_category_filter(self, queryset, name, value):
        # 不论搜到的是哪一级目录的内容，都只返回一级目录分类里的内容
        return queryset.filter(Q(category_id=value) |
                               Q(category__parent_category_id=value) |
                               Q(category__parent_category__parent_category_id=value))

    class Meta:
        model = goods
        fields = ['pricemin', 'pricemax', 'name', 'is_new', 'is_hot']
