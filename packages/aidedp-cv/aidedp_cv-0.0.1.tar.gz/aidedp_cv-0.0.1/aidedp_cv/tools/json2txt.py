import os
import json
from PIL import Image
from tqdm import tqdm

"""
将json标签格式转换为txt格式
    json_path: JSON标签路径
    img_path: 图片路径
    outxml_path: 输出路径
    classes_name: 标签
"""
json_path = "../datasets/fangchudian/Annotations_json/"
img_path = "../datasets/fangchudian/JPEGImages/"
outtxt_path = "../datasets/fangchudian/Annotations_txt"
classes_name = "../datasets/fangchudian/labels.txt"
# 不存在则构建目录
if not os.path.exists(outtxt_path):
    os.makedirs(outtxt_path)

def convert(size, box):
    # compute the normalized factors
    dw = 1./(size[0])
    dh = 1./(size[1])
    # compute the center of the bbox
    x = (box[0] + box[1])/2.0
    y = (box[2] + box[3])/2.0
    # compute the width and height of the bbox
    w = box[1] - box[0]
    h = box[3] - box[2]
    # normalize the numbers
    x = x*dw
    w = w*dw
    y = y*dh
    h = h*dh
    return (x,y,w,h)

# 获取标签
with open(classes_name, 'r', encoding='utf-8') as f:
    t = f.readlines()
    classes = [x.split()[0] for x in t]

# JOSN -> txt
for name in tqdm(os.listdir(json_path)):
    head, _ = os.path.splitext(name)
    if head == ".ipynb_checkpoints":
        continue
    imgsize = Image.open(os.path.join(img_path,head+".jpg")).size   # 获取图片尺寸

    res = ""
    # 读取JOSN
    with open(os.path.join(json_path,name), 'r') as f:
        tj = json.loads(f.read())

    for bndbox in tj['labels']:
        label = classes.index(bndbox['name'])
        box = [bndbox['x1'], bndbox['x2'], bndbox['y1'], bndbox['y2']]
        x,y,w,h = convert(imgsize, box)
        res += " ".join([str(x) for x in [label,x,y,w,h]]) + "\n"
    # 写txt
    with open(os.path.join(outtxt_path, head+".txt"),'w') as f:
        f.write(res)
print("Finished!")