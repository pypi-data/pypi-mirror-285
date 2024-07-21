{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 1,
   "metadata": {},
   "outputs": [],
   "source": [
    "import os\n",
    "from PIL import Image\n",
    "from tqdm import tqdm\n",
    "\n",
    "\"\"\"\n",
    "图片格式转换：所有图片格式转为.jpg\n",
    "    img_path:原始图片路径\n",
    "    save_path:转换后图片保存路径\n",
    "\"\"\"\n",
    "\n",
    "img_path = \"../datasets/niaochao/JPEGImages/\"\n",
    "save_path = \"../datasets/niaochao/JPEGImages_jpg/\""
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "metadata": {},
   "outputs": [],
   "source": [
    "# 生成保存路径\n",
    "if not os.path.exists(save_path):\n",
    "    os.makedirs(save_path)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Start……\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "100%|██████████| 408/408 [01:59<00:00,  3.40it/s]"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Finished!\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "\n"
     ]
    }
   ],
   "source": [
    "imglist = os.listdir(img_path)\n",
    "imglist = [x for x in imglist if x!=\".ipynb_checkpoints\"]\n",
    "print(\"Start……\")\n",
    "for name in tqdm(imglist):\n",
    "    head, _ = name.split('.')\n",
    "    img = Image.open(os.path.join(img_path,name))\n",
    "    img = img.convert(\"RGB\")\n",
    "    img.save(os.path.join(save_path, head+\".jpg\"))\n",
    "print(\"Finished!\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# 若报错\"image file is truncated\"。进行如下图片修复\n",
    "\n",
    "from PIL import Image\n",
    "import os\n",
    "\n",
    "img_path = \"../datasets/niaochao/JPEGImages/\"\n",
    "save_path = \"../datasets/niaochao/JPEGImages_jpg/\"\n",
    "imgname='157.jpeg'  # 报错图片名称\n",
    "\n",
    "with open(os.path.join(img_path, imgname), 'rb') as f:\n",
    "    img = f.read()\n",
    "img = img+B'\\xff'+B'\\xd9'  # 补全数据\n",
    "with open(os.path.join(img_path, imgname),\"wb\") as f:\n",
    "    f.write(img)"
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
   "execution_count": 8,
   "metadata": {},
   "outputs": [],
   "source": [
    "tmp = Image.open(r\"F:\\works\\VSCODE\\yolov5\\datasets\\niaochao\\JPEGImages_jpg\\93760_输电&110(66)KV&绝缘子类285yPCdiMOk.jpg\")\n",
    "tmp2 = Image.open(r\"F:\\works\\VSCODE\\yolov5\\datasets\\niaochao\\JPEGImages\\93760_输电&110(66)KV&绝缘子类285yPCdiMOk.jpg\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 10,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "(7360, 4912)"
      ]
     },
     "execution_count": 10,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "tmp2.size"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 11,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "(7360, 4912)"
      ]
     },
     "execution_count": 11,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "tmp.size"
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
