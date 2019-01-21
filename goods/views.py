from django.http import HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from django.urls import reverse

from goods.models import GoodsCategory, Goods
from user.models import User


def index(request):
    if request.method == 'GET':
        # ----------我的方式------------
        # 获取分类目录
        # 根据外键获取该分类下的商品,再根据商品集合遍历取出商品
        # 注意:页面仅供四个数据,所以需要限制数据
        category = GoodsCategory.objects.all()
        # # 访问首页,返回首页的静态页面
        # category_type = GoodsCategory.CATEGORY_TYPE
        return render(request, 'index.html', {'category': category})
        # ----------老师方式------------
        # 数据传输的格式为[分类,该类所有数据]----->页面解析
        # categorys = GoodsCategory.objects.all()
        # result = []
        # for category in categorys:
        #     goods = category.goods_set.all()[:4]
        #     data = [category, goods]
        #     result.append(data)
        # return render(request, 'index.html', {'result': result})


def detail(request, id):
    if request.method == 'GET':
        category = GoodsCategory.objects.all()  # 分类目录
        goods = Goods.objects.filter(pk=id).first()  # 商品信息
        return render(request, 'detail.html', {'goods': goods, 'category': category})


def list(request, id):
    if request.method == 'GET':
        c = GoodsCategory.objects.filter(category_type=id).first()
        new_list = Goods.objects.all().order_by('-add_time')[:2]
        return render(request, 'list.html', {'c': c, 'new_list': new_list})


def shop_search(request):
    if request.method == 'GET':
        # 获取到商品名称
        new_list = Goods.objects.all().order_by('-add_time')[:2]
        goods_name = request.GET.get('name')
        goods_list = Goods.objects.filter(name__contains=goods_name).only('id', 'name', 'shop_price',
                                                                          'goods_front_image')
        return render(request, 'list.html', {'goods_list': goods_list, 'new_list': new_list})
