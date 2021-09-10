import json
import os
import requests
def getalltxt(directory, txtfile,filter):
    for file in os.listdir(directory):
        if file.find(filter) > -1:
            txtfile.append(os.path.join(directory, file))
        elif os.path.isdir(os.path.join(directory, file)):
            getalltxt(os.path.join(directory, file), txtfile,filter)

root = "/data/label_data/class_include/protest_v1"
all_good_json = []
getalltxt(root,all_good_json,"good.json")
for gj in all_good_json:
    with open(gj,"r",encoding="utf-8")as f:
        piclist = json.load(f)
    for pic in piclist:
        url = "http://starbox.cloudwalk.work/performance/file/download?storageId={}&type=1&filename={}".format(pic,pic+".png")
        content = requests.get(url)
        pic_pth = gj.replace("good.json",pic)
        with open(pic_pth,"wb")as f:
            for chunk in content.iter_content():
                f.write(chunk)
        print(pic_pth, "download success")

# print(len(all_pics))
# with open("8w.txt","w",encoding="utf-8")as f:
#     f.write(json.dumps(all_pics,indent=4,ensure_ascii=False))
