{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 1,
   "metadata": {},
   "outputs": [],
   "source": [
    "import math\n",
    "import torch\n",
    "import pandas as pd\n",
    "import os\n",
    "from tqdm import tqdm"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "metadata": {},
   "outputs": [],
   "source": [
    "def bbox_iou(box1, box2, xywh=True, GIoU=False, DIoU=False, CIoU=False, eps=1e-7):\n",
    "    # Returns Intersection over Union (IoU) of box1(1,4) to box2(n,4)\n",
    "\n",
    "    # Get the coordinates of bounding boxes\n",
    "    if xywh:  # transform from xywh to xyxy\n",
    "        (x1, y1, w1, h1), (x2, y2, w2, h2) = box1.chunk(4, 1), box2.chunk(4, 1)\n",
    "        w1_, h1_, w2_, h2_ = w1 / 2, h1 / 2, w2 / 2, h2 / 2\n",
    "        b1_x1, b1_x2, b1_y1, b1_y2 = x1 - w1_, x1 + w1_, y1 - h1_, y1 + h1_\n",
    "        b2_x1, b2_x2, b2_y1, b2_y2 = x2 - w2_, x2 + w2_, y2 - h2_, y2 + h2_\n",
    "    else:  # x1, y1, x2, y2 = box1\n",
    "        b1_x1, b1_y1, b1_x2, b1_y2 = box1.chunk(4, 1)\n",
    "        b2_x1, b2_y1, b2_x2, b2_y2 = box2.chunk(4, 1)\n",
    "        w1, h1 = b1_x2 - b1_x1, b1_y2 - b1_y1\n",
    "        w2, h2 = b2_x2 - b2_x1, b2_y2 - b2_y1\n",
    "\n",
    "    # Intersection area\n",
    "    inter = (torch.min(b1_x2, b2_x2) - torch.max(b1_x1, b2_x1)).clamp(0) * \\\n",
    "            (torch.min(b1_y2, b2_y2) - torch.max(b1_y1, b2_y1)).clamp(0)\n",
    "\n",
    "    # Union Area\n",
    "    union = w1 * h1 + w2 * h2 - inter + eps\n",
    "\n",
    "    # IoU\n",
    "    iou = inter / union\n",
    "    if CIoU or DIoU or GIoU:\n",
    "        cw = torch.max(b1_x2, b2_x2) - torch.min(b1_x1, b2_x1)  # convex (smallest enclosing box) width\n",
    "        ch = torch.max(b1_y2, b2_y2) - torch.min(b1_y1, b2_y1)  # convex height\n",
    "        if CIoU or DIoU:  # Distance or Complete IoU https://arxiv.org/abs/1911.08287v1\n",
    "            c2 = cw ** 2 + ch ** 2 + eps  # convex diagonal squared\n",
    "            rho2 = ((b2_x1 + b2_x2 - b1_x1 - b1_x2) ** 2 + (b2_y1 + b2_y2 - b1_y1 - b1_y2) ** 2) / 4  # center dist ** 2\n",
    "            if CIoU:  # https://github.com/Zzh-tju/DIoU-SSD-pytorch/blob/master/utils/box/box_utils.py#L47\n",
    "                v = (4 / math.pi ** 2) * torch.pow(torch.atan(w2 / (h2 + eps)) - torch.atan(w1 / (h1 + eps)), 2)\n",
    "                with torch.no_grad():\n",
    "                    alpha = v / (v - iou + (1 + eps))\n",
    "                return iou - (rho2 / c2 + v * alpha)  # CIoU\n",
    "            return iou - rho2 / c2  # DIoU\n",
    "        c_area = cw * ch + eps  # convex area\n",
    "        return iou - (c_area - union) / c_area  # GIoU https://arxiv.org/pdf/1902.09630.pdf\n",
    "    return iou  # IoU"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "metadata": {},
   "outputs": [],
   "source": [
    "def calcMetrics(target_path:str, pre_path:str, iou_thres=0.45) ->list:\n",
    "    \"\"\"\n",
    "    对每张图片按lable统计boxloss, objloss, clsloss, lossSum, 按pic统计wrongRate, missRate, isOverDetect;\n",
    "    其中: lossSum = 0.4*objloss + 0.3*boxloss + 0.3*clsloss\n",
    "    argument:\n",
    "        target_path: label.txt文件路径\n",
    "        pre_path: pre.txt文件路径\n",
    "    return:\n",
    "        reslabel: list, 按label统计结果 [[imgname, labelGT, boxloss, objloss, clsloss, lossSum],...]\n",
    "        respic: list, 按pic统计结果 [imgname, wrongRate, missRate, isOverDetect]\n",
    "    \"\"\"\n",
    "    \n",
    "    with open(target_path, \"r\") as f:\n",
    "        targetlist = f.readlines()\n",
    "        targetlist = [x.split() for x in targetlist]\n",
    "    with open(pre_path, \"r\") as f:\n",
    "        prelist = f.readlines()\n",
    "        prelist = [x.split() for x in prelist]\n",
    "\n",
    "    imgname = os.path.splitext(os.path.basename(pre_path))[0]   # image name\n",
    "    reslabel = []   # 按label统计boxloss, objloss, clsloss, lossSum\n",
    "    respic = []     # 按pic统计wrongRate, missRate, isOverDetect\n",
    "    missnum = 0\n",
    "    wrongnum = 0\n",
    "\n",
    "    # 判断是否为背景\n",
    "    if prelist is None:\n",
    "        missRate = 1\n",
    "        wrongRate = 0\n",
    "        isOverDetect = False\n",
    "        reslabel = None\n",
    "        respic = [imgname, wrongRate, missRate, isOverDetect]\n",
    "        return reslabel, respic\n",
    "    isOverDetect = True if len(prelist)>len(targetlist) else False  # 判断是否过检\n",
    "\n",
    "    for target in targetlist:\n",
    "        targetbox = torch.tensor([[float(x) for x in target[1:]]], dtype=torch.float32)\n",
    "        labelGT = target[0]\n",
    "        iou = []\n",
    "        for pre in prelist:\n",
    "            prebox = torch.tensor([[float(x) for x in pre[1:-1]]], dtype=torch.float32)\n",
    "            iou.append(bbox_iou(prebox, targetbox, CIoU=True))\n",
    "        \n",
    "        if max(iou) < iou_thres:   # 判断是否属于该label\n",
    "            missnum += 1\n",
    "            continue\n",
    "\n",
    "        max_ = iou.index(max(iou))\n",
    "        if prelist[max_][0] != labelGT:    # 判断是否推理错误\n",
    "            wrongnum += 1\n",
    "            continue\n",
    "        \n",
    "        # 计算各loss\n",
    "        boxloss = float(1 - max(iou)).__round__(6)\n",
    "        objloss = (1-  float(prelist[max_][-1])).__round__(6)\n",
    "        clsloss = 1 if prelist[max_] == labelGT else 0\n",
    "        lossSum = (0.4*objloss + 0.3*boxloss + 0.3*clsloss).__round__(6)\n",
    "        reslabel.append([imgname, labelGT, boxloss, objloss, clsloss, lossSum])\n",
    "\n",
    "    wrongRate = round(wrongnum/len(targetlist), 2)  # 计算误检率\n",
    "    missRate = round(missnum/len(targetlist), 2)    # 计算漏检率\n",
    "    respic = [imgname, wrongRate, missRate, isOverDetect]\n",
    "\n",
    "    return reslabel, respic"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 4,
   "metadata": {},
   "outputs": [
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      " 69%|██████▊   | 405/591 [00:00<00:00, 478.18it/s]\n"
     ]
    },
    {
     "ename": "FileNotFoundError",
     "evalue": "[Errno 2] No such file or directory: '../datasets/niaochao/yolo_Annotations/cut-0170730794669-rote90-94119.txt'",
     "output_type": "error",
     "traceback": [
      "\u001b[1;31m---------------------------------------------------------------------------\u001b[0m",
      "\u001b[1;31mFileNotFoundError\u001b[0m                         Traceback (most recent call last)",
      "\u001b[1;32m~\\AppData\\Local\\Temp\\ipykernel_10824\\4191752901.py\u001b[0m in \u001b[0;36m<module>\u001b[1;34m\u001b[0m\n\u001b[0;32m     19\u001b[0m         \u001b[0mpre_path\u001b[0m \u001b[1;33m=\u001b[0m \u001b[0mos\u001b[0m\u001b[1;33m.\u001b[0m\u001b[0mpath\u001b[0m\u001b[1;33m.\u001b[0m\u001b[0mjoin\u001b[0m\u001b[1;33m(\u001b[0m\u001b[0mpre_dir\u001b[0m\u001b[1;33m,\u001b[0m \u001b[0mprefile\u001b[0m\u001b[1;33m)\u001b[0m\u001b[1;33m\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n\u001b[0;32m     20\u001b[0m         \u001b[0mtarget_path\u001b[0m \u001b[1;33m=\u001b[0m \u001b[0mos\u001b[0m\u001b[1;33m.\u001b[0m\u001b[0mpath\u001b[0m\u001b[1;33m.\u001b[0m\u001b[0mjoin\u001b[0m\u001b[1;33m(\u001b[0m\u001b[0mtarget_dir\u001b[0m\u001b[1;33m,\u001b[0m \u001b[0mprefile\u001b[0m\u001b[1;33m)\u001b[0m\u001b[1;33m\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n\u001b[1;32m---> 21\u001b[1;33m         \u001b[0mreslabel\u001b[0m\u001b[1;33m,\u001b[0m \u001b[0mrespic\u001b[0m \u001b[1;33m=\u001b[0m \u001b[0mcalcMetrics\u001b[0m\u001b[1;33m(\u001b[0m\u001b[0mtarget_path\u001b[0m\u001b[1;33m,\u001b[0m \u001b[0mpre_path\u001b[0m\u001b[1;33m)\u001b[0m\u001b[1;33m\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n\u001b[0m\u001b[0;32m     22\u001b[0m         \u001b[0mresult_pic\u001b[0m\u001b[1;33m.\u001b[0m\u001b[0mappend\u001b[0m\u001b[1;33m(\u001b[0m\u001b[0mrespic\u001b[0m\u001b[1;33m)\u001b[0m\u001b[1;33m\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n\u001b[0;32m     23\u001b[0m         \u001b[0mresult_label\u001b[0m\u001b[1;33m.\u001b[0m\u001b[0mextend\u001b[0m\u001b[1;33m(\u001b[0m\u001b[0mreslabel\u001b[0m\u001b[1;33m)\u001b[0m\u001b[1;33m\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n",
      "\u001b[1;32m~\\AppData\\Local\\Temp\\ipykernel_10824\\2808974081.py\u001b[0m in \u001b[0;36mcalcMetrics\u001b[1;34m(target_path, pre_path, iou_thres)\u001b[0m\n\u001b[0;32m     11\u001b[0m     \"\"\"\n\u001b[0;32m     12\u001b[0m \u001b[1;33m\u001b[0m\u001b[0m\n\u001b[1;32m---> 13\u001b[1;33m     \u001b[1;32mwith\u001b[0m \u001b[0mopen\u001b[0m\u001b[1;33m(\u001b[0m\u001b[0mtarget_path\u001b[0m\u001b[1;33m,\u001b[0m \u001b[1;34m\"r\"\u001b[0m\u001b[1;33m)\u001b[0m \u001b[1;32mas\u001b[0m \u001b[0mf\u001b[0m\u001b[1;33m:\u001b[0m\u001b[1;33m\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n\u001b[0m\u001b[0;32m     14\u001b[0m         \u001b[0mtargetlist\u001b[0m \u001b[1;33m=\u001b[0m \u001b[0mf\u001b[0m\u001b[1;33m.\u001b[0m\u001b[0mreadlines\u001b[0m\u001b[1;33m(\u001b[0m\u001b[1;33m)\u001b[0m\u001b[1;33m\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n\u001b[0;32m     15\u001b[0m         \u001b[0mtargetlist\u001b[0m \u001b[1;33m=\u001b[0m \u001b[1;33m[\u001b[0m\u001b[0mx\u001b[0m\u001b[1;33m.\u001b[0m\u001b[0msplit\u001b[0m\u001b[1;33m(\u001b[0m\u001b[1;33m)\u001b[0m \u001b[1;32mfor\u001b[0m \u001b[0mx\u001b[0m \u001b[1;32min\u001b[0m \u001b[0mtargetlist\u001b[0m\u001b[1;33m]\u001b[0m\u001b[1;33m\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n",
      "\u001b[1;31mFileNotFoundError\u001b[0m: [Errno 2] No such file or directory: '../datasets/niaochao/yolo_Annotations/cut-0170730794669-rote90-94119.txt'"
     ]
    }
   ],
   "source": [
    "if __name__ == \"__main__\":\n",
    "    \"\"\"\n",
    "    target_dir: groudTruth标签文件夹路径\n",
    "    pre_dir: 推理结果文件夹路径\n",
    "    lables: 数据集标签txt路径\n",
    "    save_path: 计算结果保存路径\n",
    "    \"\"\"\n",
    "    \n",
    "    target_dir = \"../datasets/niaochao/yolo_Annotations/\"\n",
    "    pre_dir = \"../runs/detect/niaochao/labels/\"\n",
    "    labels = \"../datasets/niaochao/labels.txt\"\n",
    "    save_path = \"../runs/detect/niaochao/\"\n",
    "    \n",
    "    result_pic = []\n",
    "    result_label = []\n",
    "    for prefile in tqdm(os.listdir(pre_dir)):\n",
    "        if prefile == \".ipynb_checkpoints\":\n",
    "            continue\n",
    "        pre_path = os.path.join(pre_dir, prefile)\n",
    "        target_path = os.path.join(target_dir, prefile)\n",
    "        reslabel, respic = calcMetrics(target_path, pre_path)\n",
    "        result_pic.append(respic)\n",
    "        result_label.extend(reslabel)\n",
    "    pd.DataFrame(result_pic, columns=[\"imgname\",\"wrongRate\",\"missRate\",\"isOverDetect\"])\\\n",
    "        .to_csv(os.path.join(save_path,\"result_pic.csv\"), index=None)\n",
    "    pd.DataFrame(result_label, columns=[\"imgname\",\"labelGT\",\"boxloss\",\"objloss\",\"clsloss\",\"lossSum\"])\\\n",
    "        .to_csv(os.path.join(save_path,\"result_label.csv\"), index=None)"
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
