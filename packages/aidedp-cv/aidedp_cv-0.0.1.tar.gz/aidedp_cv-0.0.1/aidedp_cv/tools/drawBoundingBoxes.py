import matplotlib.pyplot as plt
import torch
from torchvision import transforms
from torchvision.utils import draw_bounding_boxes
import xml.etree.ElementTree as ET
import os

"""

在样本图片上标出标注框
annotations_path: 标注框路径 xml格式;
images_path: 样本图片路径;
labels_txt: 标签路径;
saveImages_path: 保存位置

"""

annotations_path = "./data/picture transform/AnnotationsTransform/"
images_path = "./data/picture transform/ImagesTransform/"
labels_txt = "./data/picture transform/ImageSets/labels.txt"
saveImages_path = "./data/picture transform/imagesAnnotations/"

def draw_bunding_boxes(images_path, annotations_path, labels_txt, saveImages_path, width=3):
    # 获取标签
    with open(labels_txt, 'r') as f:
        tmp = f.readlines()
        labels = [x.replace('\n','') for x in tmp]

    # 生成随机颜色
    import random
    get_colors = lambda n: list(map(lambda i: "#" + "%06x" % random.randint(0, 0xFFFFFF),range(n)))
    colors = get_colors(len(labels))
    labelColor = dict(zip(labels, colors))

    # 生成保存路径
    if not os.path.exists(saveImages_path):
        os.makedirs(saveImages_path)

    images = os.listdir(images_path)
    for image in images:
        img = plt.imread(os.path.join(images_path,image))
        img = transforms.ToTensor()(img)*255
        img = img.type(torch.uint8)

        name, _ = os.path.splitext(image)
        tree = ET.parse(os.path.join(annotations_path, name+".xml"))
        root = tree.getroot()
        annotations = root.findall("object")

        # 无标注，直接保存
        if not annotations:
            plt.imsave(os.path.join(saveImages_path, image))
            break
        
        boxes = []
        colors = []
        labels = []
        for anotObejct in annotations:
            difficult = anotObejct.find('difficult').text
            if int(difficult) == 1:
                continue
            label = anotObejct.find("name").text
            labels.append(label)
            colors.append(labelColor[label])
            xmin = int(anotObejct.find("bndbox").find("xmin").text)
            ymin = int(anotObejct.find("bndbox").find("ymin").text)
            xmax = int(anotObejct.find("bndbox").find("xmax").text)
            ymax = int(anotObejct.find("bndbox").find("ymax").text)
            boxes.append([xmin, ymin, xmax, ymax])

        boxes = torch.tensor(boxes)
        res = draw_bounding_boxes(image=img, boxes=boxes, colors=colors, labels=labels, width=width)
        res = transforms.ToPILImage()(res)
        res.save(os.path.join(saveImages_path, name+"box"+_))
    return print("Complete!")



if __name__ == "__main__":
    print("begin")
    draw_bunding_boxes(images_path, annotations_path, labels_txt, saveImages_path, width=3)
    print("end")
