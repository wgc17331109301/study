from django.urls import path, re_path
from user_options import views

urlpatterns = [
    # 修改用户信息的路由地址
    re_path(r'^users/(?P<pk>.*)/$', views.user_update_view.as_view()),
    # 用户留言功能的路由地址
    path('messages/', views.user_leave_message_view.as_view()),
    re_path(r'^messages/(?P<pk>.*)/$', views.user_leave_message_view.as_view()),
    # 用户的收货地址路由
    path('address/', views.user_address_view.as_view()),
    re_path('^address/(?P<pk>.*)/$', views.user_address_view.as_view()),
]
