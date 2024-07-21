{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 1,
   "metadata": {
    "execution": {
     "iopub.execute_input": "2022-10-04T01:17:50.714574Z",
     "iopub.status.busy": "2022-10-04T01:17:50.714027Z",
     "iopub.status.idle": "2022-10-04T01:17:50.995660Z",
     "shell.execute_reply": "2022-10-04T01:17:50.994744Z",
     "shell.execute_reply.started": "2022-10-04T01:17:50.714434Z"
    },
    "scrolled": true
   },
   "outputs": [],
   "source": [
    "import cv2 as cv\n",
    "import os\n",
    "from tqdm import tqdm\n",
    "import xml.etree.ElementTree as ET\n",
    "import numpy as np\n",
    "import random"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "metadata": {
    "execution": {
     "iopub.execute_input": "2022-10-04T01:17:51.086314Z",
     "iopub.status.busy": "2022-10-04T01:17:51.085860Z",
     "iopub.status.idle": "2022-10-04T01:17:51.101335Z",
     "shell.execute_reply": "2022-10-04T01:17:51.100618Z",
     "shell.execute_reply.started": "2022-10-04T01:17:51.086264Z"
    },
    "scrolled": true
   },
   "outputs": [],
   "source": [
    "# 随机裁剪图片，包含所有锚框\n",
    "def cut_pic(img_path, xml_path, imgout_path, xmlout_path):\n",
    "    '''\n",
    "    随机裁剪图片\n",
    "    img_path:原始单个图像,eg:/datasets/hat_person/JPEGImages/00001.jpg, 使用cv.imread()读取\n",
    "    xml_path: 原始单个图像对应的xml文件, eg:/datasets/hat_person/Annotations/00001.xml\n",
    "    imgout_path: 旋转后图像输出路径, eg: /datasets/hat_person/JPEGImages_rote/\n",
    "    xmlout_path: 旋转后xml输出路径, eg: /datasets/hat_person/Annotations_rote/\n",
    "    '''\n",
    "    img = cv.imread(img_path)\n",
    "    w = img.shape[1]\n",
    "    h = img.shape[0]\n",
    "    x_min, x_max, y_min, y_max= w, 0, h, 0\n",
    "    \n",
    "    tree = ET.parse(os.path.join(xml_path))     # 读取xml\n",
    "    root = tree.getroot()\n",
    "    objects = root.findall(\"object\")\n",
    "    bboxes = []  # 统计所有boundingBox的坐标(xmin, ymin, xmax, ymax)\n",
    "    for obj in objects:\n",
    "        bbox = obj.find('bndbox')\n",
    "        xmin = float(bbox.find('xmin').text)\n",
    "        ymin = float(bbox.find('ymin').text)\n",
    "        xmax = float(bbox.find('xmax').text)\n",
    "        ymax = float(bbox.find('ymax').text)\n",
    "        bboxes.append([xmin, ymin, xmax, ymax])\n",
    "    \n",
    "    for bbox in bboxes: #找到最值坐标\n",
    "        x_min=min(x_min,bbox[0])\n",
    "        y_min=min(y_min,bbox[1])\n",
    "        x_max=max(x_max,bbox[2])\n",
    "        y_max=max(y_max,bbox[3])\n",
    "    top_left = x_min        #bbox最大左移距离\n",
    "    top_right = w-x_max     #bbox最大右边移动距离\n",
    "    top_top = y_min         #bbox最大上移距离\n",
    "    top_bottom = h-y_max    #bbox最大下移动距离\n",
    "\n",
    "    # 随机扩大这个包含所有bbox的大框\n",
    "    # random.randint()方法里面的取值区间是前闭后闭区间，\n",
    "    # 而np.random.randint()方法的取值区间是前闭后开区间\n",
    "    # 使用固定值，可以更改random.randint()，变为 n*top_left, n*top_top, n*top_right...\n",
    "    # cut_x(y)_min(max)为裁剪宽度\n",
    "    cut_x_min = int(x_min - random.uniform(0, top_left))\n",
    "    cut_y_min = int(y_min - random.uniform(0, top_top))\n",
    "    crop_x_max = int(min(w,x_max + random.uniform(0, top_right)))   #防止过大溢出边界\n",
    "    crop_y_max = int(min(h,y_max + random.uniform(0, top_bottom)))\n",
    "\n",
    "    #裁剪图片\n",
    "    cut_img = img[cut_y_min:crop_y_max, cut_x_min:crop_x_max]   \n",
    "    #裁剪bbox\n",
    "    for obj in objects:\n",
    "        bbox = obj.find('bndbox')\n",
    "        xmin = float(bbox.find('xmin').text)\n",
    "        ymin = float(bbox.find('ymin').text)\n",
    "        xmax = float(bbox.find('xmax').text)\n",
    "        ymax = float(bbox.find('ymax').text)\n",
    "        # 写入xml\n",
    "        bbox.find('xmin').text=str(int(xmin-cut_x_min))\n",
    "        bbox.find('ymin').text=str(int(ymin-cut_y_min))\n",
    "        bbox.find('xmax').text=str(int(xmax-cut_x_min))\n",
    "        bbox.find('ymax').text=str(int(ymax-cut_y_min))\n",
    "    root.find(\"size\").find(\"width\").text = str(cut_img.shape[1])\n",
    "    root.find(\"size\").find(\"height\").text = str(cut_img.shape[0])\n",
    "\n",
    "    middle_name = str(cut_x_min)+str(cut_y_min)+str(crop_x_max)+str(crop_y_max)\n",
    "    filename = os.path.basename(xml_path)   # 获取xml名，eg：\"0001.xml\"\n",
    "    tree.write(xmlout_path+\"cut-\"+middle_name+\"-\"+filename)  # 保存修改后的XML文件\n",
    "\n",
    "    filename = os.path.basename(img_path)   # 获取图片名，eg：\"0001.jpg\"\n",
    "    cv.imwrite(imgout_path+\"cut-\"+middle_name+\"-\"+filename, cut_img)   # 保存修改后的图片\n",
    "\n",
    "    return None"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "execution": {
     "iopub.execute_input": "2022-10-04T01:19:22.226221Z",
     "iopub.status.busy": "2022-10-04T01:19:22.225803Z"
    },
    "scrolled": true
   },
   "outputs": [
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      " 44%|████▍     | 21/48 [00:12<00:17,  1.52it/s]"
     ]
    }
   ],
   "source": [
    "# 程序入口\n",
    "\"\"\"\n",
    "    img_dir: 图片路径\n",
    "    anno_dir: xml路径\n",
    "    img_write_dir: 随机剪切后图片保存路径\n",
    "    anno_write_dir: 随机剪切后xml保存路径\n",
    "\"\"\"\n",
    "if __name__ == \"__main__\":    \n",
    "    img_dir = '../../datasets/niaochao/JPEGImages_transform/'\n",
    "    xml_dir = '../../datasets/niaochao/Annotations_transform/'\n",
    "    img_save_dir = '../../datasets/niaochao/JPEGImages_transform/'\n",
    "    xml_save_dir = '../../datasets/niaochao/Annotations_transform/'\n",
    "\n",
    "    if not os.path.exists(img_save_dir):\n",
    "        os.makedirs(img_save_dir)\n",
    "\n",
    "    if not os.path.exists(xml_save_dir):\n",
    "        os.makedirs(xml_save_dir)\n",
    "    \n",
    "    img_names = [x for x in os.listdir(img_dir) if x != \".ipynb_checkpoints\"]\n",
    "    for img_name in tqdm(img_names):\n",
    "        xml_name = os.path.splitext(img_name)[0] + \".xml\"\n",
    "        xml_path = os.path.join(xml_dir, xml_name)\n",
    "        img_path = os.path.join(img_dir, img_name)\n",
    "        cut_pic(img_path, xml_path, img_save_dir, xml_save_dir)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "scrolled": true
   },
   "outputs": [],
   "source": []
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {
    "scrolled": true
   },
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
  "vscode": {
   "interpreter": {
    "hash": "16e2de7ec682fc3ab5066967c6aab251353c5b7be3dac1c3e5faaae13b44f4e6"
   }
  }
 },
 "nbformat": 4,
 "nbformat_minor": 4
}
