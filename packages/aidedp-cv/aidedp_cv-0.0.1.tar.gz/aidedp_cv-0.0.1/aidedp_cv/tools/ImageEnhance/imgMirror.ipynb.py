{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 1,
   "metadata": {
    "execution": {
     "iopub.execute_input": "2022-10-04T01:16:02.808593Z",
     "iopub.status.busy": "2022-10-04T01:16:02.807781Z",
     "iopub.status.idle": "2022-10-04T01:16:03.170320Z",
     "shell.execute_reply": "2022-10-04T01:16:03.169582Z",
     "shell.execute_reply.started": "2022-10-04T01:16:02.808178Z"
    },
    "scrolled": true
   },
   "outputs": [],
   "source": [
    "import cv2 as cv\n",
    "from tqdm import tqdm\n",
    "import os\n",
    "import xml.etree.ElementTree as ET"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "metadata": {
    "execution": {
     "iopub.execute_input": "2022-10-04T01:16:03.279895Z",
     "iopub.status.busy": "2022-10-04T01:16:03.279431Z",
     "iopub.status.idle": "2022-10-04T01:16:03.289460Z",
     "shell.execute_reply": "2022-10-04T01:16:03.288816Z",
     "shell.execute_reply.started": "2022-10-04T01:16:03.279846Z"
    },
    "scrolled": true
   },
   "outputs": [],
   "source": [
    "def mirror_pic(img_path, xml_path, imgout_path, xmlout_path):\n",
    "    '''\n",
    "    水平镜像图片, 上下镜像, 可用旋转180°\n",
    "    img_path:原始单个图像,eg:/datasets/hat_person/JPEGImages/00001.jpg, 使用cv.imread()读取\n",
    "    xml_path: 原始单个图像对应的xml文件, eg:/datasets/hat_person/Annotations/00001.xml\n",
    "    imgout_path: 旋转后图像输出路径, eg: /datasets/hat_person/JPEGImages_rote/\n",
    "    xmlout_path: 旋转后xml输出路径, eg: /datasets/hat_person/Annotations_rote/\n",
    "    '''\n",
    "    img = cv.imread(img_path)\n",
    "    w=img.shape[1]\n",
    "    h=img.shape[0]\n",
    "    flip_img=cv.flip(img, 1)#水平翻转\n",
    "\n",
    "    tree = ET.parse(os.path.join(xml_path))     # 读取xml\n",
    "    root = tree.getroot()\n",
    "    objects = root.findall(\"object\")\n",
    "    for obj in objects:\n",
    "        bbox = obj.find('bndbox')\n",
    "        xmin = float(bbox.find('xmin').text)\n",
    "        ymin = float(bbox.find('ymin').text)\n",
    "        xmax = float(bbox.find('xmax').text)\n",
    "        ymax = float(bbox.find('ymax').text)\n",
    "\n",
    "        # 写入xml\n",
    "        bbox.find('xmin').text=str(int(w - xmax))\n",
    "        bbox.find('ymin').text=str(int(ymin))\n",
    "        bbox.find('xmax').text=str(int(w - xmin))\n",
    "        bbox.find('ymax').text=str(int(ymax))\n",
    "    root.find(\"size\").find(\"width\").text = str(flip_img.shape[1])\n",
    "    root.find(\"size\").find(\"height\").text = str(flip_img.shape[0])\n",
    "\n",
    "    filename = os.path.basename(xml_path)   # 获取xml名，eg：\"0001.xml\"\n",
    "    tree.write(xmlout_path+\"mirror-\"+filename)  # 保存修改后的XML文件\n",
    "\n",
    "    filename = os.path.basename(img_path)   # 获取图片名，eg：\"0001.jpg\"\n",
    "    cv.imwrite(imgout_path+\"mirror-\"+filename, flip_img)   # 保存修改后的图片\n",
    "    return None"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "metadata": {
    "execution": {
     "iopub.execute_input": "2022-10-04T01:17:17.336061Z",
     "iopub.status.busy": "2022-10-04T01:17:17.335659Z",
     "iopub.status.idle": "2022-10-04T01:17:37.342429Z",
     "shell.execute_reply": "2022-10-04T01:17:37.341730Z",
     "shell.execute_reply.started": "2022-10-04T01:17:17.336015Z"
    },
    "scrolled": true
   },
   "outputs": [
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "100%|██████████| 24/24 [00:19<00:00,  1.20it/s]\n"
     ]
    }
   ],
   "source": [
    "# 程序入口\n",
    "\"\"\"\n",
    "    img_dir: 图片路径\n",
    "    anno_dir: xml路径\n",
    "    img_write_dir: 旋转后图片保存路径\n",
    "    anno_write_dir: 旋转后xml保存路径\n",
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
    "        mirror_pic(img_path, xml_path, img_save_dir, xml_save_dir)"
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
