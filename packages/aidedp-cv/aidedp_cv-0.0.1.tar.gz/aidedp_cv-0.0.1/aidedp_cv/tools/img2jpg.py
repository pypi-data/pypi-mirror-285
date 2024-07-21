import os
from PIL import Image
from tqdm import tqdm

"""
图片格式转换：所有图片格式转为.jpg
    img_path:原始图片路径
    save_path:转换后图片保存路径
"""

img_path = "../datasets/fangchudian/JPEGImages/"
save_path = "../datasets/fangchudian/JPEGImages_jpg/"

# 生成保存路径
if not os.path.exists(save_path):
    os.makedirs(save_path)

imglist = os.listdir(img_path)
imglist = [x for x in imglist if x!=".ipynb_checkpoints"]
print("Start……")
for name in tqdm(imglist):
    head, _ = name.split('.')
    img = Image.open(os.path.join(img_path,name))
    img = img.convert("RGB")
    img.save(os.path.join(save_path, head+".jpg"))
print("Finished!")


# 若报错"image file is truncated"。进行如下图片修复

from PIL import Image
import os

imgname='157.jpeg'
with open(os.path.join(img_path, imgname), 'rb') as f:
    img = f.read()
img = img+B'\xff'+B'\xd9'  # 补全数据
with open(os.path.join(img_path, imgname),"wb") as f:
    f.write(img)