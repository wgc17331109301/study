from django.contrib import admin
from goods.models import goods_category


# 商品分类admin
@admin.register(goods_category)
class goods_category_Admin(admin.ModelAdmin):
    pass
