{
 "cells": [
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### 零、所有图片格式转为jpg"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
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
    "img_path = \"./datasets/niaochao/JPEGImages/\"\n",
    "save_path = \"./datasets/niaochao/JPEGImages_jpg/\""
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
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
   "execution_count": null,
   "metadata": {},
   "outputs": [],
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
    "img_path = \"./datasets/niaochao/JPEGImages/\"       # 转换前的图片保存路径\n",
    "save_path = \"./datasets/niaochao/JPEGImages_jpg/\"  # 转换后的图片保存路径\n",
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
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### 一、XML转TXT，返回文件夹，包含所有Anchors及labels"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 1,
   "metadata": {
    "execution": {
     "iopub.execute_input": "2022-10-04T01:31:12.720198Z",
     "iopub.status.busy": "2022-10-04T01:31:12.719333Z",
     "iopub.status.idle": "2022-10-04T01:31:12.724173Z",
     "shell.execute_reply": "2022-10-04T01:31:12.723550Z",
     "shell.execute_reply.started": "2022-10-04T01:31:12.720147Z"
    },
    "scrolled": true
   },
   "outputs": [
    {
     "data": {
      "text/plain": [
       "'f:\\\\works\\\\VSCODE\\\\yolov5-master\\\\tools'"
      ]
     },
     "execution_count": 1,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "import os \n",
    "os.getcwd()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 4,
   "metadata": {
    "execution": {
     "iopub.execute_input": "2022-10-04T01:31:28.064385Z",
     "iopub.status.busy": "2022-10-04T01:31:28.063923Z",
     "iopub.status.idle": "2022-10-04T01:31:28.171797Z",
     "shell.execute_reply": "2022-10-04T01:31:28.171155Z",
     "shell.execute_reply.started": "2022-10-04T01:31:28.064336Z"
    },
    "scrolled": true
   },
   "outputs": [
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "100%|██████████| 408/408 [00:00<00:00, 511.74it/s]\n"
     ]
    }
   ],
   "source": [
    "import glob\n",
    "import os\n",
    "import xml.etree.ElementTree as ET\n",
    "from tqdm import tqdm\n",
    "\n",
    "# 1、Anchor坐标转换\n",
    "def convert(size, box):\n",
    "    # compute the normalized factors\n",
    "    dw = 1./(size[0])\n",
    "    dh = 1./(size[1])\n",
    "    # compute the center of the bbox\n",
    "    x = (box[0] + box[1])/2.0\n",
    "    y = (box[2] + box[3])/2.0\n",
    "    # compute the width and height of the bbox\n",
    "    w = box[1] - box[0]\n",
    "    h = box[3] - box[2]\n",
    "    # normalize the numbers\n",
    "    x = x*dw\n",
    "    w = w*dw\n",
    "    y = y*dh\n",
    "    h = h*dh\n",
    "    return (x,y,w,h)\n",
    "\n",
    "\n",
    "# 2、写XML文件\n",
    "#  dir_path: the path of directory containing all the xml annotation files\n",
    "#  output_path: the path to save the generated YOLO txt annotation files\n",
    "#  image_path: the path of an input image\n",
    "def convert_annotation(dir_path, output_path, image_path, classes):\n",
    "    # e.g. if imagepath='./test.jpg', then basename_no_ext='test'\n",
    "    basename = os.path.basename(image_path)\n",
    "    basename_no_ext = os.path.splitext(basename)[0]\n",
    "\n",
    "    # locate the corresponding xml annotation file of the image\n",
    "    in_file = open(dir_path + '/' + basename_no_ext + '.xml', encoding=\"utf-8\")\n",
    "    # set the output of the yolo annotation file\n",
    "    out_file = open(output_path + basename_no_ext + '.txt', 'w')\n",
    "    # start parsing the xml file and extract the bbox information\n",
    "    tree = ET.parse(in_file)\n",
    "    root = tree.getroot()\n",
    "    size = root.find('size')\n",
    "    w = int(size.find('width').text)\n",
    "    h = int(size.find('height').text)\n",
    "\n",
    "    # enumerate all objects (bboxes) in the xml file\n",
    "    for obj in root.iter('object'):\n",
    "        difficult = obj.find('difficult').text\n",
    "        # get class index\n",
    "        cls = obj.find('name').text\n",
    "        if cls not in classes or int(difficult)==1:\n",
    "            continue\n",
    "        cls_id = classes.index(cls)\n",
    "        # get the corner coordinates and convert to yolo format\n",
    "        xmlbox = obj.find('bndbox')\n",
    "        b = (float(xmlbox.find('xmin').text), float(xmlbox.find('xmax').text), float(xmlbox.find('ymin').text), float(xmlbox.find('ymax').text))\n",
    "        bb = convert((w,h), b)\n",
    "        # finally write the \"cls x y w h\" as a single line into the yolo annotaiton file\n",
    "        out_file.write(str(cls_id) + \" \" + \" \".join([str(a) for a in bb]) + '\\n')\n",
    "\n",
    "\n",
    "# 3、生成文件\n",
    "# now we need to collect all the image paths into a list,\n",
    "# and pass through the list while invoking convert_annotation function\n",
    "#  dir_path: the directory to all the images\n",
    "def getImagesInDir(dir_path):\n",
    "    image_list = []\n",
    "    # for filename in glob.glob(dir_path + '/*.png'):\n",
    "    #     image_list.append(filename)\n",
    "    for filename in glob.glob(dir_path + '/*.jpg'):\n",
    "        image_list.append(filename)\n",
    "\n",
    "    return image_list\n",
    "\n",
    "\n",
    "#----------------------- 由此开始--------------------------------# \n",
    "\n",
    "dir_path = \"./datasets/niaochao/Annotations/\"           # xml标签文件夹\n",
    "images_path = \"./datasets/niaochao/JPEGImages_jpg/\"     # 图像文件夹\n",
    "output_path = \"./datasets/niaochao/Annotations_txt/\"   # 转换后标签(txt)输出文件夹\n",
    "classes_name = \"./datasets/niaochao/labels.txt\"         # 标签名称txt\n",
    "\n",
    "with open(classes_name, 'r', encoding='utf-8') as f:\n",
    "    t = f.readlines()\n",
    "    classes = [x.split()[0] for x in t]\n",
    "# if the output directory does not exists, we should create it\n",
    "if not os.path.exists(output_path):\n",
    "    os.makedirs(output_path)\n",
    "\n",
    "image_paths = getImagesInDir(images_path)\n",
    "for img_path in tqdm(image_paths):\n",
    "    convert_annotation(dir_path, output_path, img_path, classes)\n",
    "\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 5,
   "metadata": {
    "execution": {
     "iopub.execute_input": "2022-10-04T01:31:32.460330Z",
     "iopub.status.busy": "2022-10-04T01:31:32.459893Z",
     "iopub.status.idle": "2022-10-04T01:31:32.464916Z",
     "shell.execute_reply": "2022-10-04T01:31:32.464333Z",
     "shell.execute_reply.started": "2022-10-04T01:31:32.460284Z"
    },
    "scrolled": true
   },
   "outputs": [
    {
     "data": {
      "text/plain": [
       "408"
      ]
     },
     "execution_count": 5,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "len(os.listdir(\"datasets/niaochao/Annotations\"))"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### 二、生成训练集、测试集、验证集.txt"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 6,
   "metadata": {
    "execution": {
     "iopub.execute_input": "2022-10-04T01:31:42.672779Z",
     "iopub.status.busy": "2022-10-04T01:31:42.672321Z",
     "iopub.status.idle": "2022-10-04T01:31:42.888444Z",
     "shell.execute_reply": "2022-10-04T01:31:42.887571Z",
     "shell.execute_reply.started": "2022-10-04T01:31:42.672730Z"
    },
    "scrolled": true
   },
   "outputs": [],
   "source": [
    "import numpy as np\n",
    "\n",
    "# datanums:样本总个数\n",
    "# rate:训练集占比，默认0.9\n",
    "datanums = 408\n",
    "rate = 0.9\n",
    "\n",
    "num = np.arange(datanums)\n",
    "np.random.shuffle(num)\n",
    "\n",
    "txtlist = os.listdir(\"./datasets/niaochao/Annotations_txt/\")   # 转换后标签(txt)输出文件夹\n",
    "imglist = os.listdir(\"./datasets/niaochao/JPEGImages_jpg/\")     # 转换后的图片保存路径\n",
    "txtlist = [x for x in txtlist if x!=\".ipynb_checkpoints\"]\n",
    "imglist = [x for x in imglist if x!=\".ipynb_checkpoints\"]\n",
    "\n",
    "txtlist = np.array(txtlist)\n",
    "imglist = np.array(imglist)\n",
    "txtlist.sort()\n",
    "imglist.sort()\n",
    "\n",
    "traindatanums = int(datanums*rate)\n",
    "trainlist = imglist[num[:traindatanums]]\n",
    "vallist = imglist[num[traindatanums:]]\n",
    "\n",
    "# 生成训练集train\n",
    "res = []\n",
    "for name in trainlist:\n",
    "    tmp = os.path.splitext(name)[0]\n",
    "    nametxt = tmp+'.txt'\n",
    "    res.append(name+' '+nametxt)\n",
    "    \n",
    "with open(\"./datasets/niaochao/train.txt\", 'w') as f:\n",
    "    f.writelines(\"\\n\".join(res))\n",
    "\n",
    "# 生成测试集test\n",
    "res = []\n",
    "for name in vallist:\n",
    "    tmp = os.path.splitext(name)[0]\n",
    "    nametxt = tmp+'.txt'\n",
    "    res.append(name+' '+nametxt)\n",
    "    \n",
    "with open(\"./datasets/niaochao/test.txt\", 'w') as f:\n",
    "    f.writelines(\"\\n\".join(res))\n",
    "\n",
    "# 生成验证集val\n",
    "res = []\n",
    "for name in vallist:\n",
    "    tmp = os.path.splitext(name)[0]\n",
    "    nametxt = tmp+'.txt'\n",
    "    res.append(name+' '+nametxt)\n",
    "    \n",
    "with open(\"./datasets/niaochao/val.txt\", 'w') as f:\n",
    "    f.writelines(\"\\n\".join(res))"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "### 三、划分VOC格式的训练、测试、验证集\n",
    "    前提：已给出 train_list.txt、test_list.txt、val_list.txt"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 7,
   "metadata": {
    "execution": {
     "iopub.execute_input": "2022-10-04T01:32:31.603001Z",
     "iopub.status.busy": "2022-10-04T01:32:31.602085Z",
     "iopub.status.idle": "2022-10-04T01:32:38.332965Z",
     "shell.execute_reply": "2022-10-04T01:32:38.332070Z",
     "shell.execute_reply.started": "2022-10-04T01:32:31.602766Z"
    },
    "scrolled": true
   },
   "outputs": [
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "100%|██████████| 534/534 [00:06<00:00, 88.91it/s] \n",
      "100%|██████████| 60/60 [00:00<00:00, 119.98it/s]\n",
      "100%|██████████| 60/60 [00:00<00:00, 401.51it/s]\n",
      "100%|██████████| 534/534 [00:00<00:00, 16658.30it/s]\n",
      "100%|██████████| 60/60 [00:00<00:00, 15247.39it/s]\n",
      "100%|██████████| 60/60 [00:00<00:00, 16452.55it/s]\n"
     ]
    }
   ],
   "source": [
    "\"\"\"\n",
    "构建VOC数据集，结构如下：\n",
    "/\n",
    "images/\n",
    "    val/\n",
    "    train/\n",
    "    test/\n",
    "labels/\n",
    "    val/\n",
    "    train/\n",
    "    test/\n",
    "\"\"\"\n",
    "import os\n",
    "from tqdm import tqdm\n",
    "# we read the list files and extract the image file names without extension\n",
    "def get_fnames_from_list(lst_path):\n",
    "    basenames = []\n",
    "    lst_txt = open(lst_path, 'r')\n",
    "    lines = lst_txt.readlines()\n",
    "    for line in lines:\n",
    "        jpg_str = (line.replace(\"\\\\\", \"/\")).split()[0]\n",
    "        basename = os.path.basename(jpg_str)\n",
    "        basename_no_ext = os.path.splitext(basename)[0]\n",
    "        # print(basename_no_ext)\n",
    "        basenames.append(basename_no_ext)\n",
    "    return basenames\n",
    "\n",
    "# 数据集标签\n",
    "train_bnames = get_fnames_from_list(\"./datasets/niaochao/train.txt\")\n",
    "test_bnames = get_fnames_from_list(\"./datasets/niaochao/test.txt\")\n",
    "val_bnames = get_fnames_from_list(\"./datasets/niaochao/val.txt\")\n",
    "\n",
    "\n",
    "# 输出目录\n",
    "# create the image directory and its sub folders\n",
    "# ImageDir/LabelsDir\n",
    "# --train\n",
    "# --val\n",
    "# --test\n",
    "img_train_path = \"./datasets/niaochao/Annotations_txt/images/train/\"       # 图片路径-训练集\n",
    "img_test_path = \"./datasets/niaochao/Annotations_txt/images/test/\"         # 图片路径-测试集\n",
    "img_val_path = \"./datasets/niaochao/Annotations_txt/images/val/\"           # 图片路径-验证集\n",
    "label_train_path = \"./datasets/niaochao/Annotations_txt/labels/train/\"     # 标签路径-训练集\n",
    "label_test_path = \"./datasets/niaochao/Annotations_txt/labels/test/\"       # 标签路径-测试集\n",
    "label_val_path = \"./datasets/niaochao/Annotations_txt/labels/val/\"         # 标签路径-验证集\n",
    "\n",
    "import shutil\n",
    "# create a specified part of the dataset\n",
    "# create the target_path folder, \n",
    "# then move the files specified by bnames in the source path into the target path\n",
    "def create_dataset_folder(target_path, source_path, ext, bnames):\n",
    "    if not os.path.exists(target_path):\n",
    "        os.makedirs(target_path)\n",
    "    for bname in tqdm(bnames):\n",
    "        source_file = source_path + bname + ext\n",
    "        if os.path.exists(source_file):\n",
    "            shutil.copy(source_file, target_path)\n",
    "\n",
    "# 图像存储位置、标签（txt文件）存储位置\n",
    "img_source_path = \"./datasets/niaochao/JPEGImages_jpg/\"     # 图片保存路径\n",
    "img_ext = \".jpg\"\n",
    "create_dataset_folder(img_train_path, img_source_path, img_ext, train_bnames)\n",
    "create_dataset_folder(img_test_path, img_source_path, img_ext, test_bnames)\n",
    "create_dataset_folder(img_val_path, img_source_path, img_ext, val_bnames)\n",
    "txt_source_path = \"./datasets/niaochao/Annotations_txt/\"   # 标签（txt）保存路径\n",
    "txt_ext = \".txt\"\n",
    "create_dataset_folder(label_train_path, txt_source_path, txt_ext, train_bnames)\n",
    "create_dataset_folder(label_test_path, txt_source_path, txt_ext, test_bnames)\n",
    "create_dataset_folder(label_val_path, txt_source_path, txt_ext, val_bnames)"
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
