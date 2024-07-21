{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 7,
   "metadata": {},
   "outputs": [],
   "source": [
    "import matplotlib.pyplot as plt\n",
    "import torch\n",
    "from torchvision import transforms\n",
    "from torchvision.utils import draw_bounding_boxes\n",
    "import xml.etree.ElementTree as ET\n",
    "import os"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 16,
   "metadata": {},
   "outputs": [],
   "source": [
    "\"\"\"\n",
    "\n",
    "在样本图片上标出标注框\n",
    "annotations_path: 标注框路径 xml格式;\n",
    "images_path: 样本图片路径;\n",
    "labels_txt: 标签路径;\n",
    "saveImages_path: 保存位置\n",
    "\n",
    "\"\"\"\n",
    "\n",
    "annotations_path = \"../datasets/fangchudian/Annotations/\"\n",
    "images_path = \"../datasets/fangchudian/JPEGImages_jpg/\"\n",
    "labels_txt = \"../datasets/fangchudian/labels.txt\"\n",
    "saveImages_path = \"../datasets/fangchudian/imagesAnnotations/\""
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 17,
   "metadata": {},
   "outputs": [],
   "source": [
    "def draw_bunding_boxes(images_path, annotations_path, labels_txt, saveImages_path):\n",
    "    # 获取标签\n",
    "    with open(labels_txt, 'r') as f:\n",
    "        tmp = f.readlines()\n",
    "        labels = [x.replace('\\n','') for x in tmp]\n",
    "\n",
    "    # 生成随机颜色\n",
    "    import random\n",
    "    get_colors = lambda n: list(map(lambda i: \"#\" + \"%06x\" % random.randint(0, 0xFFFFFF),range(n)))\n",
    "    colors = get_colors(len(labels))\n",
    "    labelColor = dict(zip(labels, colors))\n",
    "\n",
    "    # 生成保存路径\n",
    "    if not os.path.exists(saveImages_path):\n",
    "        os.makedirs(saveImages_path)\n",
    "\n",
    "    images = os.listdir(images_path)\n",
    "    for image in images:\n",
    "        img = plt.imread(os.path.join(images_path,image))\n",
    "        img = transforms.ToTensor()(img)*255\n",
    "        img = img.type(torch.uint8)\n",
    "\n",
    "        name, _ = os.path.splitext(image)\n",
    "        tree = ET.parse(os.path.join(annotations_path, name+\".xml\"))\n",
    "        root = tree.getroot()\n",
    "        annotations = root.findall(\"object\")\n",
    "\n",
    "        # 无标注，直接保存\n",
    "        if not annotations:\n",
    "            plt.imsave(os.path.join(saveImages_path, image))\n",
    "            break\n",
    "        \n",
    "        boxes = []\n",
    "        colors = []\n",
    "        labels = []\n",
    "        for anotObejct in annotations:\n",
    "            difficult = anotObejct.find('difficult').text\n",
    "            if int(difficult) == 1:\n",
    "                continue\n",
    "            label = anotObejct.find(\"name\").text\n",
    "            labels.append(label)\n",
    "            colors.append(labelColor[label])\n",
    "            xmin = int(anotObejct.find(\"bndbox\").find(\"xmin\").text)\n",
    "            ymin = int(anotObejct.find(\"bndbox\").find(\"ymin\").text)\n",
    "            xmax = int(anotObejct.find(\"bndbox\").find(\"xmax\").text)\n",
    "            ymax = int(anotObejct.find(\"bndbox\").find(\"ymax\").text)\n",
    "            boxes.append([xmin, ymin, xmax, ymax])\n",
    "\n",
    "        boxes = torch.tensor(boxes)\n",
    "        res = draw_bounding_boxes(image=img, boxes=boxes, colors=colors, labels=labels, width=3)\n",
    "        res = transforms.ToPILImage()(res)\n",
    "        res.save(os.path.join(saveImages_path, name+\"box\"+_))\n",
    "    return print(\"Complete!\")\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 18,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "begin\n",
      "Complete!\n",
      "end\n"
     ]
    }
   ],
   "source": [
    "if __name__ == \"__main__\":\n",
    "    print(\"begin\")\n",
    "    draw_bunding_boxes(images_path, annotations_path, labels_txt, saveImages_path)\n",
    "    print(\"end\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 119,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Complete!\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "d:\\Anaconda3\\envs\\yolo\\lib\\site-packages\\torchvision\\transforms\\functional.py:150: UserWarning: The given NumPy array is not writable, and PyTorch does not support non-writable tensors. This means writing to this tensor will result in undefined behavior. You may want to copy the array to protect its data or make it writable before converting it to a tensor. This type of warning will be suppressed for the rest of this program. (Triggered internally at  C:\\actions-runner\\_work\\pytorch\\pytorch\\builder\\windows\\pytorch\\torch\\csrc\\utils\\tensor_numpy.cpp:178.)\n",
      "  img = torch.from_numpy(pic.transpose((2, 0, 1))).contiguous()\n"
     ]
    }
   ],
   "source": [
    "!python drawBoundingBoxes.py"
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
