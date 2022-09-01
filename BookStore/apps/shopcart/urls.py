from shopcart import views
from django.urls import path
from goods.urls import router


urlpatterns = [
    path('shoppingCart/clear', views.shop_cart_clear_view.as_view()),
    path('alipay/return/', views.alipay_return_view.as_view()),
]

# 商品购物车的路由
router.register('shopcarts', views.shop_cart_view, basename='shopcarts')
router.register('orders', views.order_view, basename='orders')
urlpatterns += router.urls
