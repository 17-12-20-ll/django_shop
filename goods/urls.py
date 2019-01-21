from django.urls import path

from goods import views

urlpatterns = [
    # 首页
    path('index/', views.index, name='index'),
    # 商品详情
    path('detail/<int:id>/', views.detail, name='detail'),
    # 更多列表
    path('list/<int:id>/', views.list, name='list'),
    # 商品搜索
    path('shop_search/', views.shop_search, name='shop_search'),
]
