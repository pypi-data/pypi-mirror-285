{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 4,
   "metadata": {},
   "outputs": [],
   "source": [
    "import cv2 as cv\n",
    "import os\n",
    "from tqdm import tqdm\n",
    "import xml.etree.ElementTree as ET\n",
    "import numpy as np\n",
    "import random\n",
    "import shutil"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 7,
   "metadata": {},
   "outputs": [],
   "source": [
    "#添加滤波\n",
    "def addblur_pic(img_path, xml_path, imgout_path, xmlout_path):\n",
    "    '''\n",
    "    高斯滤波\n",
    "        GaussianBlur() 第二个参数是高斯核大小,一般为奇数, b2=h/w*b1\n",
    "    img_path:原始单个图像,eg:/datasets/hat_person/JPEGImages/00001.jpg, 使用cv.imread()读取\n",
    "    xml_path: 原始单个图像对应的xml文件, eg:/datasets/hat_person/Annotations/00001.xml\n",
    "    imgout_path: 旋转后图像输出路径, eg: /datasets/hat_person/JPEGImages_rote/\n",
    "    xmlout_path: 旋转后xml输出路径, eg: /datasets/hat_person/Annotations_rote/\n",
    "    '''\n",
    "    img = cv.imread(img_path)\n",
    "    w = img.shape[1]\n",
    "    h = img.shape[0]\n",
    "    bl1 = random.randrange(1,10,2)  #随机1-10的奇数\n",
    "\n",
    "    bl2 = int(h/w*bl1)\n",
    "    if bl2%2 == 0:\n",
    "        bl3 = bl2 + 1\n",
    "    else:\n",
    "        bl3 = bl2\n",
    "\n",
    "    # 对图像高斯滤波\n",
    "    blur_img = cv.GaussianBlur(img, (bl1, bl3), 0)\n",
    "    \n",
    "    # 保存图片及xml\n",
    "    middle_name = str(bl3)\n",
    "    filename = os.path.basename(img_path)   # 获取图片名，eg：\"0001.jpg\"\n",
    "    cv.imwrite(imgout_path+\"blur-\"+middle_name+\"-\"+filename, blur_img)   # 保存修改后的图片\n",
    "\n",
    "    filename = os.path.basename(xml_path)   # 获取xml名，eg：\"0001.xml\"\n",
    "    shutil.copy(xml_path, xmlout_path+\"blur-\"+middle_name+\"-\"+filename)  # 保存修改后的XML文件\n",
    "    return None"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 28,
   "metadata": {},
   "outputs": [],
   "source": [
    "#添加噪声\n",
    "def addnoise_pic(img_path, xml_path, imgout_path, xmlout_path):\n",
    "    '''\n",
    "    添加高斯噪声\n",
    "    mean : 均值, var : 方差\n",
    "    noise: 噪声\n",
    "\n",
    "    img_path:原始单个图像,eg:/datasets/hat_person/JPEGImages/00001.jpg, 使用cv.imread()读取\n",
    "    xml_path: 原始单个图像对应的xml文件, eg:/datasets/hat_person/Annotations/00001.xml\n",
    "    imgout_path: 旋转后图像输出路径, eg: /datasets/hat_person/JPEGImages_rote/\n",
    "    xmlout_path: 旋转后xml输出路径, eg: /datasets/hat_person/Annotations_rote/\n",
    "    '''\n",
    "    mean = 0\n",
    "    var = 0.01\n",
    "    img = cv.imread(img_path)\n",
    "    img = np.array(img/255, dtype=float)    #图像进行归一化，范围为[0, 1]\n",
    "    noise = np.random.normal(mean, var ** 1, img.shape) #生成高斯分布的概率密度随机数\n",
    "    out = img + noise\n",
    "    if out.min() < 0:\n",
    "        low_clip = -1.\n",
    "    else:\n",
    "        low_clip = 0.\n",
    "    out = np.clip(out, low_clip, 1.0)   #其中out是一个数组，后面两个参数分别表示最小和最大值\n",
    "    addnoise_img = np.uint8(out*255)    #返回原色彩图\n",
    "\n",
    "    # 保存图片及xml\n",
    "    middle_name = str(noise.sum().round(4))\n",
    "    filename = os.path.basename(img_path)   # 获取图片名，eg：\"0001.jpg\"\n",
    "    cv.imwrite(imgout_path+\"noise-\"+middle_name+\"-\"+filename, addnoise_img)   # 保存修改后的图片\n",
    "    \n",
    "    filename = os.path.basename(xml_path)   # 获取xml名，eg：\"0001.xml\"\n",
    "    shutil.copy(xml_path, xmlout_path+\"noise-\"+middle_name+\"-\"+filename)  # 保存修改后的XML文件\n",
    "    return None"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 52,
   "metadata": {},
   "outputs": [],
   "source": [
    "# 调整亮度、对比度\n",
    "def changelight_pic(img_path, xml_path, imgout_path, xmlout_path):\n",
    "    '''\n",
    "    随机改变图片对比度、亮度\n",
    "        a: 对比度, 范围[0,5]可更改为固定值。 a=1, 对比度不变, a=0, 全黑\n",
    "        b: 亮度, 越大越亮。b=0, 亮度不变\n",
    "    img_path:原始单个图像,eg:/datasets/hat_person/JPEGImages/00001.jpg, 使用cv.imread()读取\n",
    "    xml_path: 原始单个图像对应的xml文件, eg:/datasets/hat_person/Annotations/00001.xml\n",
    "    imgout_path: 旋转后图像输出路径, eg: /datasets/hat_person/JPEGImages_rote/\n",
    "    xmlout_path: 旋转后xml输出路径, eg: /datasets/hat_person/Annotations_rote/\n",
    "    '''\n",
    "    img = cv.imread(img_path)\n",
    "    a = 1\n",
    "    # a = andom.uniform(0.35, 1)\n",
    "    b = random.uniform(-50, 50)\n",
    "    h, w, ch = img.shape    #获取shape的数值，height和width、通道\n",
    "\n",
    "    #新建全零图片数组src2,将height和width，类型设置为原图片的通道类型(色素全为零，输出为全黑图片)\n",
    "    blackimg = np.zeros([h, w, ch], img.dtype)  #创建一个和图像尺寸相同的纯黑图片\n",
    "    changel_img = cv.addWeighted(img, a, blackimg, 1-a, b)\n",
    "\n",
    "    # 保存图片及xml\n",
    "    middle_name = str((a.__round__(2), b.__round__(2)))\n",
    "    filename = os.path.basename(img_path)   # 获取图片名，eg：\"0001.jpg\"\n",
    "    cv.imwrite(imgout_path+\"chlight-\"+middle_name+\"-\"+filename, changel_img)   # 保存修改后的图片\n",
    "    \n",
    "    filename = os.path.basename(xml_path)   # 获取xml名，eg：\"0001.xml\"\n",
    "    shutil.copy(xml_path, xmlout_path+\"chlight-\"+middle_name+\"-\"+filename)  # 保存修改后的XML文件\n",
    "    return None"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 54,
   "metadata": {},
   "outputs": [],
   "source": [
    "# 颜色反转\n",
    "def colorInvert_pic(img_path, xml_path, imgout_path, xmlout_path):\n",
    "    '''\n",
    "    图片颜色反转\n",
    "\n",
    "    img_path:原始单个图像,eg:/datasets/hat_person/JPEGImages/00001.jpg, 使用cv.imread()读取\n",
    "    xml_path: 原始单个图像对应的xml文件, eg:/datasets/hat_person/Annotations/00001.xml\n",
    "    imgout_path: 旋转后图像输出路径, eg: /datasets/hat_person/JPEGImages_rote/\n",
    "    xmlout_path: 旋转后xml输出路径, eg: /datasets/hat_person/Annotations_rote/\n",
    "    '''\n",
    "    img = cv.imread(img_path)\n",
    "    h, w, ch = img.shape    #获取shape的数值，height和width、通道\n",
    "\n",
    "    whiteimg = np.ones([h, w, ch], img.dtype)*255  #创建一个和图像尺寸相同的纯黑图片\n",
    "    colorInvert_img = whiteimg - img\n",
    "\n",
    "    # 保存图片及xml\n",
    "    filename = os.path.basename(img_path)   # 获取图片名，eg：\"0001.jpg\"\n",
    "    cv.imwrite(imgout_path+\"colorInvert-\"+filename, colorInvert_img)   # 保存修改后的图片\n",
    "    \n",
    "    filename = os.path.basename(xml_path)   # 获取xml名，eg：\"0001.xml\"\n",
    "    shutil.copy(xml_path, xmlout_path+\"colorInvert-\"+filename)  # 保存修改后的XML文件\n",
    "    return None"
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
   "execution_count": 55,
   "metadata": {},
   "outputs": [
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "100%|██████████| 5/5 [00:00<00:00, 31.17it/s]\n"
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
    "    img_dir = '../../datasets/hat_person/testimgs/'\n",
    "    xml_dir = '../../datasets/hat_person/testAnnotations/'\n",
    "    img_save_dir = '../../datasets/hat_person/rotated_JPEGImages/'\n",
    "    xml_save_dir = '../../datasets/hat_person/rotated_Annotations/'\n",
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
    "\n",
    "        # addblur_pic(img_path, xml_path, img_save_dir, xml_save_dir)  # 开启随机添加滤波\n",
    "        # addnoise_pic(img_path, xml_path, img_save_dir, xml_save_dir)  # 开启随机添加噪声\n",
    "        # changelight_pic(img_path, xml_path, img_save_dir, xml_save_dir)  # 开启随机调整亮度\n",
    "        colorInvert_pic(img_path, xml_path, img_save_dir, xml_save_dir)  # 开启颜色反转"
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
