# -*- coding: utf8 -*-

# Create your views here.
# 人脸类内清理标注后端源码
from django.http import JsonResponse
from django.http import HttpResponse,HttpResponseRedirect
import os
import json
import shutil
import math
import re
import redis
# 使用redis存储用户信息
pool = redis.ConnectionPool(host="10.128.128.82",port="6379",db=2)
r = redis.Redis(connection_pool=pool)
# 所有数据存放目录
all_folder_path = "/data/class_include"

def index(request):
    return HttpResponseRedirect('/static/web/face_inside_label.html')

def multi_get_database(request):
    # 返回数据库列表和每个数据库对应的分块列表
    if "user_name" not in request.session:
        print("未登陆")
        ret_json = {
            'code': "get_database_camera_list",
            'message': '未登陆',
            'result': False,
            'data': None
        }
        response = JsonResponse({"msg": "请先登录！"})
        response.status_code = 403
        return response

    all_database_folder = all_folder_path

    # 数据库列表
    database_list = os.listdir(all_database_folder)
    resp = {}
    resp['database_list'] = database_list
    resp_jsondata = json.dumps(resp)
    return HttpResponse(resp_jsondata)

def get_id_range(request):
    # 返回数据库列表和每个数据库对应的分块列表
    if "user_name" not in request.session:
        print("未登陆")
        ret_json = {
            'code': "get_database_camera_list",
            'message': '未登陆',
            'result': False,
            'data': None
        }
        response = JsonResponse({"msg": "请先登录！"})
        response.status_code = 404
        return response

    req_json = json.loads(request.body)
    current_database_name = req_json['current_database_name']  # 当前数据库
    current_labelperson_name = request.session["user_name"]  # 当前用户

    # 获取标注人在该数据集下的range
    merged_dataset_images_path = os.path.join(all_folder_path, current_database_name, "images")
    users_info_path = os.path.join(all_folder_path,current_database_name,"users",current_labelperson_name+".json")
    all_id = os.listdir(merged_dataset_images_path)
    id_count = len(all_id)
    # 获取该用户已标的id列表
    if r.exists(current_database_name+"_"+current_labelperson_name):
        all_keys = r.lrange(current_database_name+"_"+current_labelperson_name, 0 , -1)
        user_labeled_id = list(map(lambda x:all_id[int(x)], all_keys))
    else:
        # all_keys = []
        if not r.hexists(current_database_name+"_info","last_id"):
            r.hset(current_database_name+"_info","last_id",0)
        if not r.hexists(current_database_name+"_info","last_id_checked"):
            r.hset(current_database_name+"_info","last_id_checked",0)
        if current_labelperson_name.find("check") > -1:
            last_id = int(r.hget(current_database_name+"_info","last_id_checked"))
        else:
            last_id = int(r.hget(current_database_name+"_info","last_id"))
        if last_id > id_count - 1:
            response = JsonResponse({"msg":"该批数据已分配完成，请选择另外的数据集开始！"})
            response.status_code = 403
            return response
        else:
            r.rpush(current_database_name+"_"+current_labelperson_name,last_id)
            user_labeled_id = [last_id]
            if current_labelperson_name.find("check") > -1:
                r.hset(current_database_name + "_info", "last_id_checked", last_id + 1)
            else:
                r.hset(current_database_name + "_info", "last_id", last_id + 1)

    current_id_range = "0--%d" % len(user_labeled_id)
    # current_id_range = "0--%d" % len(all_keys)
    resp = {}
    resp['current_id_range'] = current_id_range  # 当前标注人的标注范围
    resp['user_labeled_id'] = user_labeled_id
    # resp['user_labeled_id'] = all_keys
    resp['labeler'] = current_labelperson_name
    resp_jsondata = json.dumps(resp)
    return HttpResponse(resp_jsondata)

def get_all_data(request):
    if "user_name" not in request.session:
        print("未登陆")
        ret_json = {
            'code': "get_all_data",
            'message': '未登陆',
            'result': False,
            'data': None
        }
        response = JsonResponse(ret_json)
        response.status_code = 403
        return response

    req_json = json.loads(request.body)

    current_database_name = req_json['current_database_name'] # 当前数据库
    current_id_index = int(req_json['current_id_index']) # 当前主类图片的序列
    current_labelperson_name = request.session["user_name"] # 当前用户

    # user_labeled_id = request.session["user_labeled_id"]

    data_path = os.path.join(all_folder_path, current_database_name, "images")
    all_id = os.listdir(data_path)
    all_keys = r.lrange(current_database_name + "_" + current_labelperson_name, 0, -1)
    user_labeled_id = list(map(lambda x: all_id[int(x)], all_keys))
    if current_id_index < len(user_labeled_id):
        img_id = user_labeled_id[current_id_index]
    # if current_id_index < len(all_keys):
    #     img_id = all_id[int(all_keys[current_id_index])]
    else:
        if current_labelperson_name.find("check") > -1:
            last_id = int(r.hget(current_database_name + "_info", "last_id_checked"))
        else:
            last_id = int(r.hget(current_database_name + "_info", "last_id"))
        if last_id > len(all_id) - 1:
            response = JsonResponse({"msg": "该批数据集已标完，请选择其它数据集继续！"})
            response.status_code = 403
            return response
        else:
            r.rpush(current_database_name + "_" + current_labelperson_name, last_id)
            user_labeled_id.append(all_id[last_id])
            # all_keys.append(last_id)
            img_id = all_id[last_id]
            # 更新最新的id
            if current_labelperson_name.find("check") > -1:
                r.hset(current_database_name + "_info", "last_id_checked", last_id + 1)
            else:
                r.hset(current_database_name + "_info", "last_id", last_id + 1)

    # 获取主类图片，次类图片列表，图片类别id
    current_main_img_file_name_list,current_sec_img_url_list = \
            get_main_sec_class_pic_list(all_folder_path, current_database_name, img_id)

    # 获取标注人，审核人
    if r.hexists(current_database_name + "_id_checker", img_id):
        checker = r.hget(current_database_name + "_id_checker", img_id).decode("utf-8")
    else:
        checker = ""
        if current_labelperson_name.find("check") > -1:
            r.hset(current_database_name + "_id_checker", img_id, current_labelperson_name)
    if r.hexists(current_database_name + "_id_labeler", img_id):
        labeler = r.hget(current_database_name + "_id_labeler", img_id).decode("utf-8")
    else:
        labeler = ""
        r.hset(current_database_name + "_id_labeler", img_id, current_labelperson_name)

    resp = {}
    resp['current_id_index'] = current_id_index
    resp['current_main_img_url_list'] = current_main_img_file_name_list# 当前主类图片链接列表
    resp['current_sec_img_url_list'] = current_sec_img_url_list# 次类图片链接集合
    resp['user_labeled_id'] = user_labeled_id
    resp['current_id_range'] = "0--%d"%len(user_labeled_id)
    # resp['user_labeled_id'] = all_keys
    # resp['current_id_range'] = "0--%d" % len(all_keys)
    resp['labeler'] = labeler
    resp['checker'] = checker
    resp_jsondata = json.dumps(resp)
    return HttpResponse(resp_jsondata)

def moveTree(src, dst):
    dirs = '/'.join(dst.split('/')[:-1])
    if not os.path.exists(dirs):
        os.makedirs(dirs)
    shutil.move(src, dst)

def get_main_sec_class_pic_list(all_folder, current_database_name, img_id):
    use_star_box = False # 读取图片的方式，默认是本地
    if os.path.exists(os.path.join(all_folder,current_database_name,"load_style.txt")):
        with open(os.path.join(all_folder,current_database_name,"load_style.txt"),"r",encoding="utf-8")as f:
            content = f.read()
        if content.find("starbox") > -1:
            use_star_box = True
    data_path = os.path.join(all_folder,current_database_name,"images")
    # 获取主类图片
    main_pic_urls_txt = os.path.join(data_path, img_id, "good.json")
    mark_main_pic_urls_txt = os.path.join(data_path, img_id, "good_mark.json")
    if not os.path.exists(mark_main_pic_urls_txt):
        shutil.copyfile(main_pic_urls_txt, mark_main_pic_urls_txt)

    with open(mark_main_pic_urls_txt, "r", encoding='utf-8')as f:
        main_pic_names = json.load(f)
    if use_star_box:
        # main_pic_urls = ["http://ks3.kylin.cloudwalk.work/starbox-prd-ai/"+pic for pic in main_pic_names]
        main_pic_urls = ["http://starbox.cloudwalk.work/performance/file/download?storageId={}&type=1&filename=tmp.png".format(pic) for pic in main_pic_names]

    else:
        main_pic_urls = [os.path.join(data_path, img_id, pic).replace(all_folder,
                                                                      '/imgs/class_include') for pic in main_pic_names]

    # 获取次类图片
    sec_pic_urls_txt = os.path.join(data_path,img_id,"bad.json")
    mark_sec_pic_urls_txt = os.path.join(data_path,img_id,"bad_mark.json")
    if not os.path.exists(mark_sec_pic_urls_txt):
        shutil.copyfile(sec_pic_urls_txt, mark_sec_pic_urls_txt)
    with open(mark_sec_pic_urls_txt,"r",encoding='utf-8')as f:
        sec_pic_names=json.load(f)
    if use_star_box:
        # sec_pic_urls = ["http://ks3.kylin.cloudwalk.work/starbox-prd-ai/"+pic for pic in sec_pic_names]
        sec_pic_urls = ["http://starbox.cloudwalk.work/performance/file/download?storageId={}&type=1&filename=tmp.png".format(pic) for pic in sec_pic_names]
    else:
        sec_pic_urls = [os.path.join(data_path, img_id, pic).replace(all_folder,
                                                                     '/imgs/class_include') for pic in sec_pic_names]
    new_pic_urls = []
    for pic in sec_pic_urls:
        if pic.split("/")[-1] == img_id + ".jpg":
            new_pic_urls.append(pic)
            sec_pic_urls.remove(pic)
            break
    new_pic_urls += sec_pic_urls
    print(new_pic_urls)
    return main_pic_urls, new_pic_urls

def sorted_aphanumeric(data):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
    return sorted(data, key=alphanum_key)

def save_label_info(request):
    req_json = json.loads(request.body)
    current_database_name = req_json["current_database_name"]
    current_good_imgs = req_json["current_good_imgs"]
    current_labelperson_name = request.session["user_name"]  # 当前用户
    current_bad_imgs = req_json["current_bad_imgs"]
    # current_id_index = req_json["current_id_index"]
    data_path = os.path.join(all_folder_path, current_database_name, "images")
    # all_id = os.listdir(data_path)
    # all_keys = r.lrange(current_database_name + "_" + current_labelperson_name, 0, -1)
    img_id = req_json["img_id"]
    img_id_path = os.path.join(data_path, img_id)
    # 保存good的图片
    current_good_imgs = list(set(current_good_imgs))
    current_good_imgs = list(map(lambda pic_path:pic_path.replace("\\","/").split("/")[-1],current_good_imgs))

    current_bad_imgs = list(map(lambda pic_path: pic_path.replace("\\", "/").split("/")[-1], current_bad_imgs))
    current_bad_imgs = list(set(current_bad_imgs))

    with open(os.path.join(img_id_path, "good.json"),"r",encoding="utf-8")as f:
        org_pic = json.load(f)
    if os.path.exists(os.path.join(img_id_path, "bad.json")):
        with open(os.path.join(img_id_path, "bad.json"),"r",encoding="utf-8")as f:
            org_pic += json.load(f)
    saveflag = True
    label_imgs = current_good_imgs + current_bad_imgs
    if set(label_imgs) != set(org_pic):
        saveflag = False

    if saveflag:
        with open(os.path.join(img_id_path, "good_mark.json"), "w", encoding="utf-8")as f:
            f.write(json.dumps(current_good_imgs, indent=4, ensure_ascii=False))
    # else:
    #     if (not os.path.exists(os.path.join(img_id_path, "good_mark.json"))) and os.path.exists(os.path.join(img_id_path, "good.json")):
    #         shutil.copyfile(os.path.join(img_id_path, "good.json"),os.path.join(img_id_path, "good_mark.json"))

    # 保存bad的图片
        with open(os.path.join(img_id_path, "bad_mark.json"), "w", encoding="utf-8")as f:
            f.write(json.dumps(current_bad_imgs, indent=4, ensure_ascii=False))
    # else:
    #     if not os.path.exists(os.path.join(img_id_path, "bad_mark.json")):
    #         if os.path.exists(os.path.join(img_id_path, "bad.json")):
    #             shutil.copyfile(os.path.join(img_id_path, "bad.json"),os.path.join(img_id_path, "bad_mark.json"))

    print(current_labelperson_name, current_database_name, img_id, current_good_imgs, current_bad_imgs)
    resp_jsondata = json.dumps({"msg": img_id + "保存成功"})
    return HttpResponse(resp_jsondata)

def showpic(requsest, pic):
    pic_path = "/imgs/"+pic
    print(pic_path)
    with open(pic_path, 'rb') as f:
        image_data = f.read()
    return HttpResponse(image_data, content_type="image/png")