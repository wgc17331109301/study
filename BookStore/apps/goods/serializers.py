from django.db.models import Q
from rest_framework import serializers
from goods.models import goods_category, goods, goods_image, hot_search_words
from goods.models import goods_category_brand, index_ad, banner


# 商品一级分类的序列化器
class goods_category_serializer(serializers.ModelSerializer):

    class Meta:
        model = goods_category
        fields = '__all__'


# 商品轮播图的序列化器
class goods_image_serializer(serializers.ModelSerializer):
    class Meta:
        model = goods_image
        fields = '__all__'


# 商品搜索的序列化器
class goods_serializer(serializers.ModelSerializer):
    category = goods_category_serializer()
    images = goods_image_serializer(many=True)

    class Meta:
        model = goods
        fields = '__all__'


# 商品热搜词的序列化器
class hot_search_words_serializer(serializers.ModelSerializer):
    class Meta:
        model = hot_search_words
        fields = '__all__'


# 商品三级分类的序列化器
class goods_category3_serializer(serializers.ModelSerializer):
    class Meta:
        model = goods_category
        fields = '__all__'


# 商品二级分类的序列化器
class goods_category2_serializer(serializers.ModelSerializer):
    sub_cat = goods_category3_serializer(many=True)

    class Meta:
        model = goods_category
        fields = '__all__'


# 商品品牌类的序列化器
class brand_serializer(serializers.ModelSerializer):
    class Meta:
        model = goods_category_brand
        fields = '__all__'


# 首页分类的序列化器
class index_category_serializer(serializers.ModelSerializer):
    brands = brand_serializer(many=True)
    sub_cat = goods_category2_serializer(many=True)

    # 表示需要获取并显示的字段，要搭配（get_xxx）进行使用
    goods = serializers.SerializerMethodField()
    ad_goods = serializers.SerializerMethodField()

    # get_xxx 方法定义时，必须要和serializers.SerializerMethodField() 结合使用
    def get_goods(self, obj):
        all_goods = goods.objects.filter(
            Q(category_id=obj.id) |
            Q(category__parent_category_id=obj.id) |
            Q(category__parent_category__parent_category_id=obj.id))

        # 因为序列化器之间可以互相调用，所以在调用的时候需要告诉下一个序列化器当前的请求对象
        serializer = goods_serializer(all_goods, many=True,
                                      context={'request': self.context['request']})
        return serializer.data

    # get_xxx 方法定义时，必须要和serializers.SerializerMethodField() 结合使用
    def get_ad_goods(self, obj):
        ad_goods = index_ad.objects.filter(category_id=obj.id)

        if ad_goods:
            goods_ins = ad_goods.first().goods
            serializer = goods_serializer(goods_ins,
                                          context={'request': self.context['request']})
            return serializer.data

    class Meta:
        model = goods_category
        fields = '__all__'


# 商品轮播图的序列化器
class banner_serializer(serializers.ModelSerializer):
    class Meta:
        model = banner
        fields = '__all__'


# 商品详情页的序列化器
class goods_detail_serializer(serializers.ModelSerializer):
    class Meta:
        model = goods
        fields = '__all__'
