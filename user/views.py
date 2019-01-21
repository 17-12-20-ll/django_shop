from django.contrib.auth.hashers import make_password
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from user.forms import RegisterForm, LoginForm, AddressForm
from user.models import User, UserAddress, UserAction


def register(request):
    if request.method == 'GET':
        return render(request, 'register.html')
    if request.method == "POST":
        # 使用表单form做校验
        form = RegisterForm(request.POST)
        if form.is_valid():
            # 校验成功
            # 账号不存在数据库,密码和确认密码一致,邮箱格式正确
            username = form.cleaned_data['user_name']
            password = make_password(form.cleaned_data['pwd'])
            email = form.cleaned_data['email']
            User.objects.create(username=username, password=password, email=email)
            return HttpResponseRedirect(reverse('user:login'))
        else:
            # 获取表单校验不通过的错误信息
            errors = form.errors
            return render(request, 'register.html', {'errors': errors})


def login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            # 登录成功
            username = form.cleaned_data['username']
            user = User.objects.filter(username=username).first()
            request.session['user_id'] = user.id
            # 在这里开始向index页面发送请求,该请求就会被中间件拦截.
            return HttpResponseRedirect(reverse('goods:index'))
        else:
            errors = form.errors
            return render(request, 'login.html', {'errors': errors})


def logout(request):
    if request.method == 'GET':
        # 退出方式一:清空session中的数据
        request.session.flush()
        # 退出方式二:删除键值对
        # del request.session['user_id']
        # if request.session.get('goods')
        #     del request.session['goods']
        return HttpResponseRedirect(reverse('goods:index'))


def user_site(request):
    if request.method == "GET":
        user_id = request.session.get('user_id')
        user_address = UserAddress.objects.filter(user_id=user_id)
        return render(request, 'user_center_site.html', {'user_address': user_address, 'flag': 3})
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            address = form.cleaned_data['address']
            postcode = form.cleaned_data['postcode']
            mobile = form.cleaned_data['mobile']
            user_id = request.session.get('user_id')
            UserAddress.objects.create(user_id=user_id, address=address, signer_name=username, signer_mobile=mobile,
                                       signer_postcode=postcode)
            return HttpResponseRedirect(reverse('user:user_site'))
        else:
            errors = form.errors
            return render(request, 'user_center_site.html', {'errors': errors})


def user_info(request):
    user_id = request.session.get('user_id')
    user = User.objects.filter(pk=user_id)
    user_address_info = user.first().useraddress_set.all().order_by('-add_time')
    # 用户浏览最多次数的商品
    like_list = UserAction.objects.filter(user_id=user_id).order_by('-click')[:5]
    # 用户最新浏览的商品
    recent_list = UserAction.objects.filter(user_id=user_id).order_by('-last_time')[:5]
    return render(request, 'user_center_info.html',
                  {'like_list': like_list, 'recent_list': recent_list, 'user_address_info': user_address_info,
                   'flag': 1})
