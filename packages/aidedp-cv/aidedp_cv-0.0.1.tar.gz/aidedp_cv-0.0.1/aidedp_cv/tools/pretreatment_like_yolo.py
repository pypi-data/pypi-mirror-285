# ### 一、XML转TXT，返回文件夹，包含所有Anchors及labels

import glob
import os
import xml.etree.ElementTree as ET

# 1、Anchor坐标转换
def convert(size, box):
    # compute the normalized factors
    dw = 1./(size[0])
    dh = 1./(size[1])
    # compute the center of the bbox
    x = (box[0] + box[1])/2.0
    y = (box[2] + box[3])/2.0
    # compute the width and height of the bbox
    w = box[1] - box[0]
    h = box[3] - box[2]
    # normalize the numbers
    x = x*dw
    w = w*dw
    y = y*dh
    h = h*dh
    return (x,y,w,h)


# 2、写XML文件
#  dir_path: the path of directory containing all the xml annotation files
#  output_path: the path to save the generated YOLO txt annotation files
#  image_path: the path of an input image
def convert_annotation(dir_path, output_path, image_path, classes):
    # e.g. if imagepath='./test.jpg', then basename_no_ext='test'
    basename = os.path.basename(image_path)
    basename_no_ext = os.path.splitext(basename)[0]

    # locate the corresponding xml annotation file of the image
    in_file = open(dir_path + '/' + basename_no_ext + '.xml')
    # set the output of the yolo annotation file
    out_file = open(output_path + basename_no_ext + '.txt', 'w')
    # start parsing the xml file and extract the bbox information
    tree = ET.parse(in_file)
    root = tree.getroot()
    size = root.find('size')
    w = int(size.find('width').text)
    h = int(size.find('height').text)

    # enumerate all objects (bboxes) in the xml file
    for obj in root.iter('object'):
        difficult = obj.find('difficult').text
        # get class index
        cls = obj.find('name').text
        if cls not in classes or int(difficult)==1:
            continue
        cls_id = classes.index(cls)
        # get the corner coordinates and convert to yolo format
        xmlbox = obj.find('bndbox')
        b = (float(xmlbox.find('xmin').text), float(xmlbox.find('xmax').text), float(xmlbox.find('ymin').text), float(xmlbox.find('ymax').text))
        bb = convert((w,h), b)
        # finally write the "cls x y w h" as a single line into the yolo annotaiton file
        out_file.write(str(cls_id) + " " + " ".join([str(a) for a in bb]) + '\n')


# 3、生成文件
# now we need to collect all the image paths into a list,
# and pass through the list while invoking convert_annotation function
#  dir_path: the directory to all the images
def getImagesInDir(dir_path):
    image_list = []
    # for filename in glob.glob(dir_path + '/*.png'):
    #     image_list.append(filename)
    for filename in glob.glob(dir_path + '/*.jpg'):
        image_list.append(filename)

    return image_list


#----------------------- 由此开始--------------------------------# 

dir_path = "./datasets/anquanmao/Annotations/"
images_path = "./datasets/anquanmao/JPEGImages/"
output_path = "./datasets/anquanmao/yolo_Annotations/"
classes_name = "./datasets/anquanmao/labels.txt"

with open(classes_name, 'r', encoding='utf-8') as f:
    t = f.readlines()
    classes = [x.split()[0] for x in t]
# if the output directory does not exists, we should create it
if not os.path.exists(output_path):
    os.makedirs(output_path)

image_paths = getImagesInDir(images_path)
for img_path in image_paths:
    convert_annotation(dir_path, output_path, img_path, classes)


# ----------------------------------------------------------------
# ### 二、划分VOC格式的训练、测试、验证集
#     前提：已给出 train_list.txt、test_list.txt、val_list.txt
# ----------------------------------------------------------------
import numpy as np

# datanums:样本总个数
# rate:训练集占比，默认0.9
datanums = 1000
rate = 0.9

num = np.arange(datanums)
np.random.shuffle(num)

txtlist = os.listdir("./datasets/anquanmao/yolo_Annotations/")
imglist = os.listdir("./datasets/anquanmao/JPEGImages/")

txtlist = np.array(txtlist)
imglist = np.array(imglist)
txtlist.sort()
imglist.sort()

traindatanums = int(datanums*rate)
trainlist = imglist[num[:traindatanums]]
vallist = imglist[num[traindatanums:]]

# 生成训练集train
res = []
for name in trainlist:
    tmp = name.split(".")[0]
    nametxt = tmp+'.txt'
    res.append(name+' '+nametxt)
    
with open("./datasets/anquanmao/train.txt", 'w') as f:
    f.writelines("\n".join(res))

# 生成测试集val
res = []
for name in vallist:
    tmp = name.split(".")[0]
    nametxt = tmp+'.txt'
    res.append(name+' '+nametxt)
    
with open("./datasets/anquanmao/val.txt", 'w') as f:
    f.writelines("\n".join(res))


# -----------------------------------------------------------
### 三、划分VOC格式的训练、测试、验证集
    # 前提：已给出 train_list.txt、test_list.txt、val_list.txt

"""
构建VOC数据集，结构如下：
/
images/
    val/
    train/
    test/
labels/
    val/
    train/
    test/
"""
import os
# we read the list files and extract the image file names without extension
def get_fnames_from_list(lst_path):
    basenames = []
    lst_txt = open(lst_path, 'r')
    lines = lst_txt.readlines()
    for line in lines:
        jpg_str = (line.replace("\\", "/")).split()[0]
        basename = os.path.basename(jpg_str)
        basename_no_ext = os.path.splitext(basename)[0]
        # print(basename_no_ext)
        basenames.append(basename_no_ext)
    return basenames

# 数据集标签
train_bnames = get_fnames_from_list("./datasets/anquanmao/train.txt")
test_bnames = get_fnames_from_list("./datasets/anquanmao/test.txt")
val_bnames = get_fnames_from_list("./datasets/anquanmao/val.txt")


# 输出目录
# create the image directory and its sub folders
# ImageDir/LabelsDir
# --train
# --val
# --test
img_train_path = "./datasets/anquanmao/yolo_dataset/images/train/"
img_test_path = "./datasets/anquanmao/yolo_dataset/images/test/"
img_val_path = "./datasets/anquanmao/yolo_dataset/images/val/"
label_train_path = "./datasets/anquanmao/yolo_dataset/labels/train/"
label_test_path = "./datasets/anquanmao/yolo_dataset/labels/test/"
label_val_path = "./datasets/anquanmao/yolo_dataset/labels/val/"

import shutil
# create a specified part of the dataset
# create the target_path folder, 
# then move the files specified by bnames in the source path into the target path
def create_dataset_folder(target_path, source_path, ext, bnames):
    if not os.path.exists(target_path):
        os.makedirs(target_path)
    for bname in bnames:
        source_file = source_path + bname + ext
        if os.path.exists(source_file):
            shutil.copy(source_file, target_path)

# 图像存储位置、标签（txt文件）存储位置
img_source_path = "./datasets/anquanmao/JPEGImages/"
img_ext = ".jpg"
create_dataset_folder(img_train_path, img_source_path, img_ext, train_bnames)
create_dataset_folder(img_test_path, img_source_path, img_ext, test_bnames)
create_dataset_folder(img_val_path, img_source_path, img_ext, val_bnames)
txt_source_path = "./datasets/anquanmao/yolo_Annotations/"
txt_ext = ".txt"
create_dataset_folder(label_train_path, txt_source_path, txt_ext, train_bnames)
create_dataset_folder(label_test_path, txt_source_path, txt_ext, test_bnames)
create_dataset_folder(label_val_path, txt_source_path, txt_ext, val_bnames)