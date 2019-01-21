import re
import time

from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.deprecation import MiddlewareMixin

from cart.models import ShoppingCart
from user.models import User, UserAction


class IsLoginMiddleWare(MiddlewareMixin):

    def process_request(self, request):
        # 拦截请求之前的函数
        # 1. 给requesy.user属性赋值,赋值为当前登录的用户
        user_id = request.session.get('user_id')
        if user_id:
            user = User.objects.filter(pk=user_id).first()
            request.user = user
        # 2. 登录校验,需区分哪些地址不需要做登录校验
        # 如果请求的path为去结算的路由:/order/place_order/,不能匹配下面序列的路由,就会跳转到登录
        path = request.path
        if path == '/':
            return None
        not_need_check = ['/user/register/', '/user/login/', '/goods/index/', '/goods/detail/.*/', '/cart/.*/',
                          '/goods/shop_search/', '/static/.*', '/media/.*']
        for check_path in not_need_check:
            if re.match(check_path, path):
                # 当前path路径不需要做登录校验的路由
                return None
        # path 为需要做登录校验的路由时,判断用户是否登录,没有登录则跳转到登录
        if not user_id:
            return HttpResponseRedirect(reverse('user:login'))


class SessionToDbMiddleWare(MiddlewareMixin):
    def process_response(self, request, response):
        # 同步session中的商品信息到数据库中购物车表的商品信息
        # 1. 判断用户是否登录,登录才做数据同步操作
        user_id = request.session.get('user_id')
        if user_id:
            # 2. 同步信息
            # 2.1判断session中的商品是否存在数据库中,如果存在,则更新
            # 2.2如果不存在,则创建
            session_goods = request.session.get('goods')
            if session_goods:
                for se_goods in session_goods:
                    # se_goods组装存储的商品格式:[goods_id,num,is_select]
                    cart = ShoppingCart.objects.filter(user_id=user_id, goods_id=se_goods[0]).first()
                    if cart:
                        # 更新商品信息
                        if cart.nums != se_goods[1] or cart.is_select != se_goods[2]:
                            cart.nums = se_goods[1]
                            cart.is_select = se_goods[2]
                            cart.save()
                    else:
                        # 创建
                        ShoppingCart.objects.create(user_id=user_id, goods_id=se_goods[0], nums=se_goods[1],
                                                    is_select=se_goods[2])

            # 同步数据库中的数据到session中
            db_carts = ShoppingCart.objects.filter(user_id=user_id)
            # 组装多个商品格式:[[goods_id,num,is_select],[goods_id,num,is_select],]
            if db_carts:
                # 第一:生成式方法
                new_session_goods = [[cart.goods_id, cart.nums, cart.is_select] for cart in db_carts]
                # 第二:循环添加
                # result = []
                # for cart in db_carts:
                #     data = [cart.goods_id, cart.nums, cart.is_select]
                #     result.append(data)
                request.session['goods'] = new_session_goods
            # 2.3如果数据库存在信息,session中不存在,就要删除数据库中数据(同步数据库数据到session中)
        return response


class RecentBrowseMiddleWare(MiddlewareMixin):
    # 最近浏览中间件
    def process_response(self, request, response):
        # 1. 获取user
        user = request.user
        if user.id:
            # 2. 将最近浏览商品id,时间存在mysql中
            path = request.path
            scan_path = ['/goods/detail/.*/']
            for scan in scan_path:
                if re.match(scan, path):
                    # 将数据存入数据库(商品id,商品点击次数,商品最后浏览时间)
                    goods_id = path.split('/')[3]
                    user_active = UserAction.objects.filter(goods_id=goods_id, user_id=user.id).first()
                    if user_active:
                        user_active.click += 1
                        user_active.save()
                    else:
                        user_active = UserAction()
                        user_active.goods_id = goods_id
                        user_active.user_id = user.id
                        user_active.click = 1
                        user_active.save()
            # self.scan_list = request.session.get('scan_list')
            # # 数据组装格式为:[[id,num,time],[id,num,time],....]
            # if self.scan_list:
            #     # 如果有当前session,遍历对应id值,将num+1
            #     for i in self.scan_list:
            #         for goods_id in self.scan_id:
            #             if i[0] == goods_id:
            #                 i[1] += 1
            #                 i[2] = time.time()
            #             else:
            #                 self.scan_list.append([goods_id, 1, time.time(), user.id])
            #     request.session['scan_list'] = self.scan_list
            # else:
            #     if path.split('/')[3] in self.scan_id:
            #         self.scan_list = [[path.split('/')[3], 1, time.time(), user.id]]
            #         request.session['scan_list'] = self.scan_list
            # print(self.scan_list)
        # 每一次访问页面时,都保存一次session,
        # 如果session中存在,就把数据加一,
        # if request.session.get('scan_id'):
        #     request.session['scan_id'] = self.scan_id
        #     request.session['scan_num'] += 1
        #     request.session['scan_time'] = time.time()
        # else:  # 不存在就新建
        #     # 存入浏览商品id
        #     request.session['scan_id'] = self.scan_id
        #     # 存入浏览次数
        #     request.session['scan_num'] = 1
        #     # 存入浏览时间戳
        #     request.session['scan_time'] = time.time()

        # 3. 退出时,同步到数据库表中
        # 4. 登录时,同步到session中
        return response
