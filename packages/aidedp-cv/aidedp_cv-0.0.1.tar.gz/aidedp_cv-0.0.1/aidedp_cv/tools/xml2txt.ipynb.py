{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 2,
   "metadata": {},
   "outputs": [],
   "source": [
    "import glob\n",
    "import os\n",
    "import xml.etree.ElementTree as ET"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "metadata": {},
   "outputs": [],
   "source": [
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
    "    return (x,y,w,h)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 4,
   "metadata": {},
   "outputs": [],
   "source": [
    "#  dir_path: the path of directory containing all the xml annotation files\n",
    "#  output_path: the path to save the generated YOLO txt annotation files\n",
    "#  image_path: the path of an input image\n",
    "def convert_annotation(dir_path, output_path, image_path, classes):\n",
    "    # e.g. if imagepath='./test.jpg', then basename_no_ext='test'\n",
    "    basename = os.path.basename(image_path)\n",
    "    basename_no_ext = os.path.splitext(basename)[0]\n",
    "\n",
    "    # locate the corresponding xml annotation file of the image\n",
    "    in_file = open(dir_path + '/' + basename_no_ext + '.xml')\n",
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
    "# image_path = \"custom_dataset/hat_person/JPEGImages/000000.jpg\"\n",
    "# dir_path = \"custom_dataset/hat_person/Annotations/\"\n",
    "# output_path = \"custom_dataset/\"\n",
    "# convert_annotation(dir_path, output_path, image_path)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 5,
   "metadata": {},
   "outputs": [],
   "source": [
    "# now we need to collect all the image paths into a list,\n",
    "# and pass through the list while invoking convert_annotation function\n",
    "#  dir_path: the directory to all the images\n",
    "def getImagesInDir(dir_path):\n",
    "    image_list = []\n",
    "    for filename in glob.glob(dir_path + '/*.png'):\n",
    "        image_list.append(filename)\n",
    "    for filename in glob.glob(dir_path + '/*.jpg'):\n",
    "        image_list.append(filename)\n",
    "\n",
    "    return image_list"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 6,
   "metadata": {},
   "outputs": [],
   "source": [
    "dir_path = \"./datasets/hat_person/Annotations/\"\n",
    "images_path = \"./datasets/hat_person/JPEGImages/\"\n",
    "output_path = \"./datasets/hat_person/yolo_Annotations/\"\n",
    "classes_name = \"./datasets/hat_person/labels.txt\"\n",
    "\n",
    "with open(classes_name, 'r', encoding='utf-8') as f:\n",
    "    t = f.readlines()\n",
    "    classes = [x.split()[0] for x in t]\n",
    "# if the output directory does not exists, we should create it\n",
    "if not os.path.exists(output_path):\n",
    "    os.makedirs(output_path)\n",
    "\n",
    "image_paths = getImagesInDir(images_path)\n",
    "for img_path in image_paths:\n",
    "    convert_annotation(dir_path, output_path, img_path, classes)"
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
