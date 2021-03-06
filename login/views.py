# -*- coding: utf8 -*-

# Create your views here.
from django.shortcuts import render, redirect
from login.models import User
from login.forms import UserForm, RegisterForm

import hashlib
import os
import json

def hash_code(s, salt='mysite'):# 加点盐
    h = hashlib.sha256()
    s += salt
    h.update(s.encode())  # update方法只接收bytes类型
    return h.hexdigest()

def getImglib():
    """"""
    temp = {}
    imgroot = 'static/img'
    # print(os.getcwd())
    for dirpath, dirnames, filenames in os.walk(imgroot):
        if not filenames:
            continue
        realpth = os.path.relpath(dirpath, '../static')
        camera_info, person_id = dirpath.split(os.sep)[-2:]
        camera_info = camera_info.split('_')
        camera_id = camera_info[0]
        camera_time_range = '_'.join(camera_info[1:])
        select = [filenames[0], filenames[-1]]
        imgs = []
        for name in select:
            path = os.path.join(realpth, name)
            path = path.replace('\\', '\/')
            # imgs.append()
        if camera_id not in temp:
            temp[camera_id] = {camera_time_range: {person_id: [os.path.join(realpth, name) for name in select]}}
        elif camera_time_range not in temp[camera_id]:
            temp[camera_id][camera_time_range] = {person_id: [os.path.join(realpth, name) for name in select]}
        else:
            temp[camera_id][camera_time_range][person_id] = [os.path.join(realpth, name) for name in select]
    return temp

imglibs = getImglib()

def index(request):
    """"""
    # if request.session.get('is_login', None):
    #     # 登录状态不允许注册。你可以修改这条原则！
    return render(request, 'login/index.html', {'imglibs': imglibs, 'imgstr':json.dumps(imglibs)})


def login(request):
    if request.session.get('is_login', None):
        return redirect("/index/")
    if request.method == "POST":
        login_form = UserForm(request.POST)
        message = "请检查填写的内容！"
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            try:
                user = User.objects.get(name=username)
                print(User.objects.all())
                print(username, user.passwd, hash_code(password))
                #if user.passwd == hash_code(password):  # 哈希值和数据库内的值进行比对
                if user.passwd == password:
                    request.session['is_login'] = True
                    request.session['user_id'] = user.id
                    request.session['user_name'] = user.name
                    return redirect('/index/')
                else:
                    message = "密码不正确！"
            except Exception as e:
                print(e)
                message = "用户不存在！"
        return render(request, 'login/login.html', locals())

    login_form = UserForm()
    return render(request, 'login/login.html', locals())


def register(request):
    if request.session.get('is_login', None):
        # 登录状态不允许注册。你可以修改这条原则！
        return redirect("/index/")
    if request.method == "POST":
        register_form = RegisterForm(request.POST)
        message = "请检查填写的内容！"
        if register_form.is_valid():  # 获取数据
            username = register_form.cleaned_data['username']
            password1 = register_form.cleaned_data['password1']
            password2 = register_form.cleaned_data['password2']
            #email = register_form.cleaned_data['email']
            #sex = register_form.cleaned_data['sex']
            if password1 != password2:  # 判断两次密码是否相同
                message = "两次输入的密码不同！"
                return render(request, 'login/register.html', locals())
            else:
                same_name_user = User.objects.filter(name=username)
                if same_name_user:  # 用户名唯一
                    message = '用户已经存在，请重新选择用户名！'
                    return render(request, 'login/register.html', locals())
                #same_email_user = User.objects.filter(email=email)
                #if same_email_user:  # 邮箱地址唯一
                #    message = '该邮箱地址已被注册，请使用别的邮箱！'
                #    return render(request, 'login/register.html', locals())

                # 当一切都OK的情况下，创建新用户

                new_user = User()
                new_user.name = username
                #new_user.passwd = hash_code(password1)  # 使用加密密码
                new_user.passwd = password1
                #new_user.email = email
                #new_user.sex = sex
                new_user.save()
                return redirect('/login/')  # 自动跳转到登录页面
    register_form = RegisterForm()
    return render(request, 'login/register.html', locals())

def logout(request):
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/index/")
    request.session.flush()
    # 或者使用下面的方法
    # del request.session['is_login']
    # del request.session['user_id']
    # del request.session['user_name']
    return redirect("/index/")
