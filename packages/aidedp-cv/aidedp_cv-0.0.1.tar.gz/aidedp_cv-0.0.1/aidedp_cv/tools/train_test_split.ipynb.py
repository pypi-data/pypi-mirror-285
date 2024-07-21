{
 "cells": [
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
   "source": [
    "####从txt标签文件夹中随机抽取一定比例的txt标签，并根据txt标签名字，抽取对应的图像\n",
    "import os\n",
    "import random\n",
    "import shutil\n",
    "\n",
    "\n",
    "def moveFile(Txtdir, Imgdir, Txt_target_dir, img_target_dir):\n",
    "        pathDir = os.listdir(Txtdir)    #获取标签列表\n",
    "        filenumber=len(pathDir)\n",
    "        rate=0.2    #定义抽取图片的比例\n",
    "        random_imgnum=int(filenumber*rate) #按照比例从文件夹中取一定数量标签\n",
    "        sample = random.sample(pathDir, random_imgnum)  #随机选取random_imgnum数量的样本标签\n",
    "        print (sample)\n",
    "        for labelname in sample:\n",
    "            nameimg = os.path.splitext(labelname)[0]\n",
    "            shutil.move(Txtdir+labelname, Txt_target_dir+labelname)\n",
    "            shutil.move(Imgdir+nameimg+'.jpg', img_target_dir+nameimg+'.jpg')\n",
    "\n",
    "        '''\n",
    "        for imgname in sample:\n",
    "                #name0 = os.path.join(outdir1,os.path.basename(name))\n",
    "                nametxt=os.path.splitext(imgname)[0]\n",
    "                shutil.move(Imgdir+imgname, img_target_dir+imgname)\n",
    "                shutil.move(Txtdir+nametxt+'.txt', Txt_target_dir+nametxt+'.txt')\n",
    "        '''\n",
    "        # return\n",
    "\n",
    "\n",
    "# if __name__ == '__main__':\n",
    "    \n",
    "    \n",
    "\n",
    "\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "Imgdir = \"/images/\"#图像文件夹\n",
    "img_target_dir = \"/img/\"#划分目标图像文件夹\n",
    "Txtdir = \"/labels/\"#标签文件夹\n",
    "Txt_target_dir=\"/ann/\"#划分目标标签文件夹\n",
    "#moveFile(Imgdir)\n",
    "moveFile(Txtdir)"
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
   "name": "python",
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
