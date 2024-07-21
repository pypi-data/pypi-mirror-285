{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 10,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "[1216, 404]\n",
      "total: 1620\n"
     ]
    }
   ],
   "source": [
    "import os\n",
    " \n",
    "txt_path = r'./datasets/hat_person/yolo_dataset/labels/train/'  # txt文件所在路径\n",
    "\n",
    "class_num = 2  # 样本类别数\n",
    "class_list = [i for i in range(class_num)]\n",
    "class_num_list = [0 for i in range(class_num)]\n",
    "labels_list = os.listdir(txt_path)\n",
    "for i in labels_list:\n",
    "    file_path = os.path.join(txt_path, i)\n",
    "    file = open(file_path, 'r')  # 打开文件\n",
    "    file_data = file.readlines()  # 读取所有行\n",
    "    for every_row in file_data:\n",
    "        class_val = every_row.split(' ')[0]\n",
    "        class_ind = class_list.index(int(class_val))\n",
    "        class_num_list[class_ind] += 1\n",
    "    file.close()\n",
    "# 输出每一类的数量以及总数\n",
    "print(class_num_list)\n",
    "print('total:', sum(class_num_list))"
   ]
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
