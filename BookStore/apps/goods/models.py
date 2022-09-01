from django.db import models
from ckeditor.fields import RichTextField


# 商品分类的模型类
class goods_category(models.Model):
    # 商品多级分类
    CATEGORY_TYPE = (
        (1, '一级类目'),
        (2, '二级类目'),
        (3, '三级类目'),
    )

    # 模型字段
    name = models.CharField(default='', max_length=30, verbose_name='类别名')
    code = models.CharField(default='', max_length=30, verbose_name='类别编号')

    # 需要将原来的models.TextField更换为RichTextField，才能支持富文本格式
    desc = RichTextField(default='', verbose_name='类别描述')

    is_tab = models.BooleanField(default=False, verbose_name='是否导航')
    add_time = models.DateTimeField(auto_now_add=True, verbose_name='添加时间')
    category_type = models.IntegerField(choices=CATEGORY_TYPE, verbose_name='类目级别')
    # 设置一个指向自己的外键
    parent_category = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True,
                                        verbose_name='父类目级别', related_name='sub_cat')

    class Meta:
        verbose_name = '商品类别'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


# 商品的模型类
class goods(models.Model):
    # 模型字段
    category = models.ForeignKey(goods_category, on_delete=models.CASCADE, verbose_name='商品类别')
    goods_sn = models.CharField(max_length=50, default='', verbose_name='商品编号')
    name = models.CharField(max_length=100, verbose_name='商品名称')
    click_num = models.IntegerField(default=0, verbose_name="点击数")
    sold_num = models.IntegerField(default=0, verbose_name="商品销售量")
    fav_num = models.IntegerField(default=0, verbose_name="收藏数")
    goods_num = models.IntegerField(default=0, verbose_name="库存数")
    market_price = models.FloatField(default=0, verbose_name="市场价格")
    shop_price = models.FloatField(default=0, verbose_name="本店价格")
    goods_brief = RichTextField(max_length=500, verbose_name="商品简短描述")
    goods_desc = RichTextField(default='', verbose_name="内容")
    ship_free = models.BooleanField(default=True, verbose_name="是否包邮")
    # 首页中的商品封面
    goods_front_image = models.ImageField(upload_to="goods/images/", null=True, blank=True, verbose_name="封面图")
    is_new = models.BooleanField(default=False, verbose_name="是否新品")
    is_hot = models.BooleanField(default=False, verbose_name="是否热销")
    add_time = models.DateTimeField(auto_now_add=True, verbose_name="添加时间")

    class Meta:
        verbose_name = '商品信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


# 商品轮播图的图片
class goods_image(models.Model):
    # 轮播图图片字段
    goods = models.ForeignKey(goods, on_delete=models.CASCADE, related_name='images', verbose_name='轮播图')
    image = models.ImageField(upload_to='', verbose_name='图片', null=True, blank=True)
    add_time = models.DateTimeField(auto_now_add=True, verbose_name='添加时间')

    class Meta:
        verbose_name = '商品轮播图'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.goods.name


# 热搜词的模型
class hot_search_words(models.Model):
    # 模型字段
    keywords = models.CharField(default='', max_length=20, verbose_name='热搜词')
    index = models.IntegerField(default=0, verbose_name='排序')
    add_time = models.DateTimeField(auto_now_add=True, verbose_name='添加时间')

    class Meta:
        verbose_name = '热搜排行'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.keywords


# 商品的品牌类目模型
class goods_category_brand(models.Model):
    # 模型字段
    category = models.ForeignKey(goods_category, on_delete=models.CASCADE,
            related_name='brands', null=True, blank=True, verbose_name='商品类目')
    name = models.CharField(default='', max_length=30, verbose_name='品牌名')
    desc = RichTextField(default='', max_length=200, verbose_name='品牌描述')
    image = models.ImageField(upload_to='brands/', verbose_name='品牌图片')
    add_time = models.DateTimeField(auto_now_add=True, verbose_name='添加时间')

    class Meta:
        verbose_name = '品牌名称'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.name


# 首页展示的商品广告
class index_ad(models.Model):
    category = models.ForeignKey(goods_category, on_delete=models.CASCADE,
                                 related_name='category', verbose_name='商品类目')
    goods = models.ForeignKey(goods, on_delete=models.CASCADE, related_name='goods')

    class Meta:
        verbose_name = '首页广告'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.goods.name


# 商品轮播图
class banner(models.Model):
    # 字段
    goods = models.ForeignKey(goods, on_delete=models.CASCADE, verbose_name='商品')
    image = models.ImageField(upload_to='banner', verbose_name='轮播图片')
    index = models.IntegerField(default=0, verbose_name='轮播顺序')
    add_time = models.DateTimeField(auto_now_add=True, verbose_name='添加时间')

    class Meta:
        verbose_name = '首页轮播'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.goods.name
