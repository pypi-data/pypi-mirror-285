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
# import re
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
train_bnames = get_fnames_from_list("./datasets/hat_person/train_list.txt")
test_bnames = get_fnames_from_list("./datasets/hat_person/test_list.txt")
val_bnames = get_fnames_from_list("./datasets/hat_person/val_list.txt")


# 输出目录
# create the image directory and its sub folders
# ImageDir/LabelsDir
# --train
# --val
# --test
img_train_path = "./datasets/hat_person/yolo_dataset/images/train/"
img_test_path = "./datasets/hat_person/yolo_dataset/images/test/"
img_val_path = "./datasets/hat_person/yolo_dataset/images/val/"
label_train_path = "./datasets/hat_person/yolo_dataset/labels/train/"
label_test_path = "./datasets/hat_person/yolo_dataset/labels/test/"
label_val_path = "./datasets/hat_person/yolo_dataset/labels/val/"

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
img_source_path = "./datasets/hat_person/JPEGImages/"
img_ext = ".jpg"
create_dataset_folder(img_train_path, img_source_path, img_ext, train_bnames)
create_dataset_folder(img_test_path, img_source_path, img_ext, test_bnames)
create_dataset_folder(img_val_path, img_source_path, img_ext, val_bnames)
txt_source_path = "./datasets/hat_person/yolo_Annotations/"
txt_ext = ".txt"
create_dataset_folder(label_train_path, txt_source_path, txt_ext, train_bnames)
create_dataset_folder(label_test_path, txt_source_path, txt_ext, test_bnames)
create_dataset_folder(label_val_path, txt_source_path, txt_ext, val_bnames)