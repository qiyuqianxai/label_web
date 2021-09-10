import os
src = "/data/"    #要链接的文件
dst = "/workspace/code/label-app/static/multi_dataset_base/"#创建好的软链接
print(os.listdir('static'))
os.symlink(src, dst)
