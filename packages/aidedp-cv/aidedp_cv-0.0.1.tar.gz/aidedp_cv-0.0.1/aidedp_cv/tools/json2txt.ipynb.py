{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 18,
   "metadata": {},
   "outputs": [],
   "source": [
    "import os\n",
    "import json\n",
    "from PIL import Image\n",
    "from tqdm import tqdm"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "'f:\\\\works\\\\VSCODE\\\\yolov5\\\\tools'"
      ]
     },
     "execution_count": 2,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "\"\"\"\n",
    "将json标签格式转换为txt格式\n",
    "    json_path: JSON标签路径\n",
    "    img_path: 图片路径\n",
    "    outxml_path: 输出路径\n",
    "    classes_name: 标签\n",
    "\"\"\"\n",
    "json_path = \"../datasets/fangchudian/Annotations_json/\"\n",
    "img_path = \"../datasets/fangchudian/JPEGImages/\"\n",
    "outtxt_path = \"../datasets/fangchudian/Annotations_txt\"\n",
    "classes_name = \"../datasets/fangchudian/labels.txt\"\n",
    "\n",
    "# 不存在则构建目录\n",
    "if not os.path.exists(outtxt_path):\n",
    "    os.makedirs(outtxt_path)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "metadata": {},
   "outputs": [],
   "source": [
    "def convert(size, box):\n",
    "    # compute the normalized factors\n",
    "    dw = 1./(size[0])\n",
    "    dh = 1./(size[1])\n",
    "    # compute the center of the bbox\n",
    "    x = (box[0] + box[1])/2.0\n",
    "    y = (box[2] + box[3])/2.0\n",
    "    # compute the width and height of the bbox\n",
    "    w = box[1] - box[0]\n",
    "    h = box[3] - box[2]\n",
    "    # normalize the numbers\n",
    "    x = x*dw\n",
    "    w = w*dw\n",
    "    y = y*dh\n",
    "    h = h*dh\n",
    "    return (x,y,w,h)\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 40,
   "metadata": {},
   "outputs": [],
   "source": [
    "# 获取标签\n",
    "with open(classes_name, 'r', encoding='utf-8') as f:\n",
    "    t = f.readlines()\n",
    "    classes = [x.split()[0] for x in t]"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 47,
   "metadata": {},
   "outputs": [],
   "source": [
    "# JOSN -> txt\n",
    "for name in tqdm(os.listdir(json_path)):\n",
    "    head, _ = os.path.splitext(name)\n",
    "    if head == \".ipynb_checkpoints\":\n",
    "        continue\n",
    "    imgsize = Image.open(os.path.join(img_path,head+\".jpg\")).size   # 获取图片尺寸\n",
    "\n",
    "    res = \"\"\n",
    "    # 读取JOSN\n",
    "    with open(os.path.join(json_path,name), 'r') as f:\n",
    "        tj = json.loads(f.read())\n",
    "\n",
    "    for bndbox in tj['labels']:\n",
    "        label = classes.index(bndbox['name'])\n",
    "        box = [bndbox['x1'], bndbox['x2'], bndbox['y1'], bndbox['y2']]\n",
    "        x,y,w,h = convert(imgsize, box)\n",
    "        res += \" \".join([str(x) for x in [label,x,y,w,h]]) + \"\\n\"\n",
    "    # 写txt\n",
    "    with open(os.path.join(outtxt_path, head+\".txt\"),'w') as f:\n",
    "        f.write(res)\n",
    "print(\"Finished!\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": []
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3.7.13 ('yolo')",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.7.13"
  },
  "orig_nbformat": 4,
  "vscode": {
   "interpreter": {
    "hash": "16e2de7ec682fc3ab5066967c6aab251353c5b7be3dac1c3e5faaae13b44f4e6"
   }
  }
 },
 "nbformat": 4,
 "nbformat_minor": 2
}
