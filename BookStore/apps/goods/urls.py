from goods import views
from django.urls import path, re_path
from rest_framework.routers import DefaultRouter


urlpatterns = [
    # 商品类别的路由
    # path('categories/', views.goods_category_view.as_view()),
    # 商品的搜索路由
    path('goods/', views.goods_list_view.as_view()),
    # 商品热搜词路由
    path('hotsearchs/', views.hot_search_words_view.as_view()),
    # 首页商品的路由
    path('indexgoods/', views.index_goods_view.as_view()),
    # 商品轮播图的路由
    path('banners/', views.banner_view.as_view()),
    # 商品详情页的路由
    re_path(r'^goods/(?P<pk>.*)/$', views.goods_detail_view.as_view()),
]


router = DefaultRouter()
router.register('categories', views.goods_category_view, basename='categories')
urlpatterns += router.urls
