import glob
import os
import xml.etree.ElementTree as ET

# Anchor坐标转换
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


# 写XML文件
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


# 生成文件
# now we need to collect all the image paths into a list,
# and pass through the list while invoking convert_annotation function
#  dir_path: the directory to all the images
def getImagesInDir(dir_path):
    image_list = []
    for filename in glob.glob(dir_path + '/*.png'):
        image_list.append(filename)
    for filename in glob.glob(dir_path + '/*.jpg'):
        image_list.append(filename)

    return image_list


# 由此开始
dir_path = "./datasets/hat_person/Annotations/"
images_path = "./datasets/hat_person/JPEGImages/"
output_path = "./datasets/hat_person/yolo_Annotations1/"
classes_name = "./datasets/hat_person/labels.txt"

with open(classes_name, 'r', encoding='utf-8') as f:
    t = f.readlines()
    classes = [x.split()[0] for x in t]
# if the output directory does not exists, we should create it
if not os.path.exists(output_path):
    os.makedirs(output_path)

image_paths = getImagesInDir(images_path)
for img_path in image_paths:
    convert_annotation(dir_path, output_path, img_path, classes)

