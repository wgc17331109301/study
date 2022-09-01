from users import views
from django.urls import path
from rest_framework_jwt.views import obtain_jwt_token

# router = DefaultRouter() 只能实例化一次，否则会覆盖原有的实例化对象
from goods.urls import router

urlpatterns = [
    # 验证码的路由地址
    path('code/', views.verify_code_view.as_view()),
    # 用户注册的路由地址
    path('users/', views.register_view.as_view()),
    # 用户登录的路由地址
    path('login/', obtain_jwt_token),
]

# 用户收藏的路由
router.register('userfavs', views.user_favorite_view, basename='userfavs')
urlpatterns += router.urls
