{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 2,
   "metadata": {
    "execution": {
     "iopub.execute_input": "2022-10-04T01:20:00.066348Z",
     "iopub.status.busy": "2022-10-04T01:20:00.065764Z",
     "iopub.status.idle": "2022-10-04T01:20:00.363235Z",
     "shell.execute_reply": "2022-10-04T01:20:00.362473Z",
     "shell.execute_reply.started": "2022-10-04T01:20:00.066166Z"
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
   "execution_count": 3,
   "metadata": {
    "execution": {
     "iopub.execute_input": "2022-10-04T01:20:00.487206Z",
     "iopub.status.busy": "2022-10-04T01:20:00.486694Z",
     "iopub.status.idle": "2022-10-04T01:20:00.502120Z",
     "shell.execute_reply": "2022-10-04T01:20:00.501450Z",
     "shell.execute_reply.started": "2022-10-04T01:20:00.487154Z"
    },
    "scrolled": true
   },
   "outputs": [],
   "source": [
    "#随机平移\n",
    "def shift_pic(img_path, xml_path, imgout_path, xmlout_path):\n",
    "    '''\n",
    "    随机平移图片, 上下左右平移\n",
    "    img_path:原始单个图像,eg:/datasets/hat_person/JPEGImages/00001.jpg, 使用cv.imread()读取\n",
    "    xml_path: 原始单个图像对应的xml文件, eg:/datasets/hat_person/Annotations/00001.xml\n",
    "    imgout_path: 旋转后图像输出路径, eg: /datasets/hat_person/JPEGImages_rote/\n",
    "    xmlout_path: 旋转后xml输出路径, eg: /datasets/hat_person/Annotations_rote/\n",
    "    '''\n",
    "    img = cv.imread(img_path)\n",
    "    #防止标注目标在平移时溢出图片\n",
    "    w=img.shape[1]\n",
    "    h=img.shape[0]\n",
    "    x_min, x_max, y_min, y_max= w, 0, h, 0\n",
    "\n",
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
    "    for bbox in bboxes:#找到最值坐标\n",
    "        x_min=min(x_min, bbox[0])\n",
    "        y_min=min(y_min, bbox[1])\n",
    "        x_max=max(x_max, bbox[2])\n",
    "        y_max=max(y_max, bbox[3])\n",
    "    top_left = x_min        #bbox最大左移距离\n",
    "    top_right = w-x_max     #bbox最大右边移动距离\n",
    "    top_top = y_min         #bbox最大上移距离\n",
    "    top_bottom = h-y_max    #bbox最大下移动距离\n",
    "\n",
    "    #uniform:从一个均匀分布[low,high)中随机采样\n",
    "    x = np.random.uniform(-top_left, top_right)\n",
    "    y = np.random.uniform(-top_top, top_bottom)\n",
    "    \n",
    "    # x为向左或右移动的像素值,正为向右负为向左; y为向上或者向下移动的像素值,正为向下负为向上\n",
    "    M = np.float32([[1, 0, x], [0, 1, y]])\n",
    "    #img:输入图像 M：变换矩阵 (img.shape[1], img.shape[0])：变换后的尺寸，默认没变  \n",
    "    shift_img = cv.warpAffine(img, M, (img.shape[1], img.shape[0]))\n",
    "\n",
    "    # 平移bbox\n",
    "    for obj in objects:\n",
    "        bbox = obj.find('bndbox')\n",
    "        xmin = float(bbox.find('xmin').text)\n",
    "        ymin = float(bbox.find('ymin').text)\n",
    "        xmax = float(bbox.find('xmax').text)\n",
    "        ymax = float(bbox.find('ymax').text)\n",
    "        # 写入xml\n",
    "        bbox.find('xmin').text=str(int(xmin + x))\n",
    "        bbox.find('ymin').text=str(int(ymin + y))\n",
    "        bbox.find('xmax').text=str(int(xmax + x))\n",
    "        bbox.find('ymax').text=str(int(ymax + y))\n",
    "    root.find(\"size\").find(\"width\").text = str(shift_img.shape[1])\n",
    "    root.find(\"size\").find(\"height\").text = str(shift_img.shape[0])\n",
    "\n",
    "    middle_name = str(x.__round__(2))+\"-\"+str(y.__round__(2))\n",
    "    filename = os.path.basename(xml_path)   # 获取xml名，eg：\"0001.xml\"\n",
    "    tree.write(xmlout_path+\"shift-\"+middle_name+\"-\"+filename)  # 保存修改后的XML文件\n",
    "\n",
    "    filename = os.path.basename(img_path)   # 获取图片名，eg：\"0001.jpg\"\n",
    "    cv.imwrite(imgout_path+\"shift-\"+middle_name+\"-\"+filename, shift_img)   # 保存修改后的图片\n",
    "\n",
    "    return None"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 4,
   "metadata": {
    "execution": {
     "iopub.execute_input": "2022-10-04T01:20:02.043740Z",
     "iopub.status.busy": "2022-10-04T01:20:02.042796Z",
     "iopub.status.idle": "2022-10-04T01:20:56.758473Z",
     "shell.execute_reply": "2022-10-04T01:20:56.757755Z",
     "shell.execute_reply.started": "2022-10-04T01:20:02.043678Z"
    },
    "scrolled": true
   },
   "outputs": [
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "100%|██████████| 96/96 [00:54<00:00,  1.75it/s]\n"
     ]
    }
   ],
   "source": [
    "# 程序入口\n",
    "\"\"\"\n",
    "    img_dir: 图片路径\n",
    "    anno_dir: xml路径\n",
    "    img_write_dir: 随机平移后图片保存路径\n",
    "    anno_write_dir: 随机平移后xml保存路径\n",
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
    "        shift_pic(img_path, xml_path, img_save_dir, xml_save_dir)"
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
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "naas"
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
   "version": "3.7.4"
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
