{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 1,
   "metadata": {
    "execution": {
     "iopub.execute_input": "2022-10-04T01:12:41.467345Z",
     "iopub.status.busy": "2022-10-04T01:12:41.466553Z",
     "iopub.status.idle": "2022-10-04T01:12:41.699047Z",
     "shell.execute_reply": "2022-10-04T01:12:41.698119Z",
     "shell.execute_reply.started": "2022-10-04T01:12:41.467193Z"
    },
    "scrolled": true
   },
   "outputs": [],
   "source": [
    "import cv2 as cv\n",
    "import numpy as np\n",
    "import os\n",
    "import xml.etree.ElementTree as ET\n",
    "from tqdm import tqdm"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "metadata": {
    "execution": {
     "iopub.execute_input": "2022-10-04T01:12:42.585980Z",
     "iopub.status.busy": "2022-10-04T01:12:42.585465Z",
     "iopub.status.idle": "2022-10-04T01:12:42.602165Z",
     "shell.execute_reply": "2022-10-04T01:12:42.601334Z",
     "shell.execute_reply.started": "2022-10-04T01:12:42.585928Z"
    },
    "scrolled": true
   },
   "outputs": [],
   "source": [
    "def rotateImage(angle, img_path, xml_path, imgout_path, xmlout_path):\n",
    "    '''\n",
    "    img_path:原始单个图像,eg:/datasets/hat_person/JPEGImages/00001.jpg, 使用cv.imread()读取\n",
    "    xml_path: 原始单个图像对应的xml文件, eg:/datasets/hat_person/Annotations/00001.xml\n",
    "    imgout_path: 旋转后图像输出路径, eg: /datasets/hat_person/JPEGImages_rote/\n",
    "    xmlout_path: 旋转后xml输出路径, eg: /datasets/hat_person/Annotations_rote/\n",
    "    angle: 旋转角度, 也可使用如下代码，随机生成\n",
    "    angle = random.randint(-180,180)#随机生成角度\n",
    "    '''\n",
    "    img = cv.imread(img_path)\n",
    "    w = img.shape[1]\n",
    "    h = img.shape[0]\n",
    "    #旋转图片\n",
    "    center = (w/2,h/2)\n",
    "    M = cv.getRotationMatrix2D(center, angle, 1.0)\n",
    "    ##第一个参数：旋转中心点(正数为逆时针旋转，负数为正时针)  第二个参数：旋转角度 第三个参数：缩放比例\n",
    "    ##[[-9.87688341e-01  -1.56434465e-01  2.81539911e+03]第一个是cos角度，第二个是sin角度\n",
    "    ## [1.56434465e-01 -9.87688341e-01  2.34557672e+03]]\n",
    "    \n",
    "    cos = np.abs(M[0, 0])\n",
    "    sin = np.abs(M[0, 1])\n",
    "    nW = int((h * sin) + (w * cos))#新的尺寸 nw,nh\n",
    "    nH = int((h * cos) + (w * sin))\n",
    "    M[0, 2] += (nW / 2) - center[0]#新的中心坐标\n",
    "    M[1, 2] += (nH / 2) - center[1]\n",
    "    rota_img= cv.warpAffine(img, M, (nW, nH))\n",
    "    #第一个参数为原图，第二个参数为旋转矩阵，第三个参数为图像（宽，高）的元组，\n",
    "    # 旋转后的图片需要包含所有的框，否则会对图像的原始标注造成破坏。\n",
    "    #所以要变换图片尺寸，加载数据时在resize到需要大小\n",
    "\n",
    "    #旋转bbox，处理xml\n",
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
    "        # 得到旋转后的坐标\n",
    "        #dot(点乘)\n",
    "        #取中点值是为了旋转后，用boundingRect算出最小外接正矩形，尽量避免加入无关信息\n",
    "        point1 = np.dot(M, np.array([(xmin + xmax) / 2, ymin, 1]))\n",
    "        point2 = np.dot(M, np.array([xmax, (ymin + ymax) / 2, 1]))\n",
    "        point3 = np.dot(M, np.array([(xmin + xmax) / 2, ymax, 1]))\n",
    "        point4 = np.dot(M, np.array([xmin, (ymin + ymax) / 2, 1]))\n",
    "        # 合并np.array\n",
    "        concat = np.vstack((point1, point2, point3, point4))#vstack输入[1 2 3]和[4 5 6]输出[[123]\n",
    "                                                                                                                    #                                                             [4 5 6]]\n",
    "        # 改变array类型\n",
    "        concat = concat.astype(np.int32)\n",
    "        rx, ry, rw, rh = cv.boundingRect(concat)#旋转后目标的距行框（没有角度）的xywh\n",
    "        rx_min = rx\n",
    "        ry_min = ry\n",
    "        rx_max = rx + rw\n",
    "        ry_max = ry + rh\n",
    "\n",
    "        # 写入xml\n",
    "        bbox.find('xmin').text=str(int(rx_min))\n",
    "        bbox.find('ymin').text=str(int(ry_min))\n",
    "        bbox.find('xmax').text=str(int(rx_max))\n",
    "        bbox.find('ymax').text=str(int(ry_max))\n",
    "    root.find(\"size\").find(\"width\").text = str(rota_img.shape[1])\n",
    "    root.find(\"size\").find(\"height\").text = str(rota_img.shape[0])\n",
    "    # return \n",
    "    \n",
    "    filename = os.path.basename(xml_path)   # 获取xml名，eg：\"0001.xml\"\n",
    "    tree.write(xmlout_path+\"rote\"+str(angle)+\"-\"+filename)  # 保存修改后的XML文件\n",
    "\n",
    "    filename = os.path.basename(img_path)   # 获取图片名，eg：\"0001.jpg\"\n",
    "    cv.imwrite(imgout_path+\"rote\"+str(angle)+\"-\"+filename, rota_img)   # 保存修改后的图片\n",
    "    return None"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 5,
   "metadata": {
    "execution": {
     "iopub.execute_input": "2022-10-04T01:13:31.853928Z",
     "iopub.status.busy": "2022-10-04T01:13:31.853405Z",
     "iopub.status.idle": "2022-10-04T01:13:37.253916Z",
     "shell.execute_reply": "2022-10-04T01:13:37.252864Z",
     "shell.execute_reply.started": "2022-10-04T01:13:31.853857Z"
    },
    "scrolled": true
   },
   "outputs": [
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "100%|██████████| 6/6 [00:05<00:00,  1.11it/s]\n"
     ]
    }
   ],
   "source": [
    "# 程序入口\n",
    "\"\"\"\n",
    "    angle: 旋转角度，角度制；\n",
    "    img_dir: 图片路径\n",
    "    anno_dir: xml路径\n",
    "    img_write_dir: 旋转后图片保存路径\n",
    "    anno_write_dir: 旋转后xml保存路径\n",
    "\"\"\"\n",
    "if __name__ == \"__main__\":\n",
    "    # 逆时针旋转角度\n",
    "    angle = 270 \n",
    "    \n",
    "    img_dir = '../../datasets/niaochao/JPEGImages_target/'\n",
    "    xml_dir = '../../datasets/niaochao/Annotations_target/'\n",
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
    "        rotateImage(angle, img_path, xml_path, img_save_dir, xml_save_dir)\n",
    "    "
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
