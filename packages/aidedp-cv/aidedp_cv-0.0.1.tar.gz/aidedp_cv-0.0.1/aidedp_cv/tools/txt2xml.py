"""
yolov5
批量将yolov5的输出的txt转为XML
"""
import os
from PIL import Image
import xml.etree.ElementTree as ET

path = "../datasets/hat_person/"
img_floderName = "JPEGImages"
txt_floderName = "yolo_Annotations"
label_name = "labels.txt"

"""
目录结构：
    --path
        |__img_floderName
        |__txt_floderName
        |__label_name: "label.txt"
        |__txt2xml: 保存目录
"""

# 目录不存在则创建
if not os.path.exists(os.path.join(path, 'txt2xml')):
    os.mkdir(os.path.join(path, 'txt2xml'))

# 增加换行符
def __indent(elem, level=0):
    i = "\n" + level*"\t"
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "\t"
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            __indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

# 添加节点及内容
def xmlappend(nodeName, text, fatherNode):
    node = ET.Element(nodeName)
    node.text = text
    fatherNode.append(node)

# 读取label
with open(os.path.join(path,label_name), 'r', encoding='utf-8') as f:
        labelList = f.readlines()

# txt转换XML
for imgName in os.listdir(os.path.join(path,img_floderName)):
    
    # 获取图片名称
    name = imgName.split('.')[0]
    img = Image.open(os.path.join(path,img_floderName,imgName))
    
    # 读取对应txt
    with open(os.path.join(path,txt_floderName,name+'.txt'), 'r', encoding='utf-8') as f:
        contextList = f.readlines()    

    # 获取图片尺寸及通道
    imgw, imgh = img.size[0], img.size[1]
    depth = len(img.getbands())

    # 构建XML文件
    root = ET.Element('annotation')       # 创建节点
    tree = ET.ElementTree(root)     # 创建文档
    xmlappend('folder',os.path.join(path, img_floderName),root)
    xmlappend('filename',imgName,root)
    xmlappend('path','undefined', root)
    source = ET.Element('source')
    xmlappend('database','Unknown',source)
    root.append(source)
    imgsize = ET.Element('size')
    xmlappend('width',str(imgw),imgsize)
    xmlappend('height',str(imgh),imgsize)
    xmlappend('depth',str(depth),imgsize)
    root.append(imgsize)
    xmlappend('segmented','0',root)

    # 写入object
    if contextList:
        for context in contextList:        
            context = context.split()
            num = int(context[0])
            label = labelList[num].split()[0]
            xn = float(context[1])
            yn = float(context[2])
            wn = float(context[3])
            hn = float(context[4])
            # 还原Anchor
            xmin = round(imgw*xn - imgw*wn*0.5)
            xmax = round(imgw*xn + imgw*wn*0.5)
            ymin = round(imgh*yn - imgh*hn*0.5)
            ymax = round(imgh*yn + imgh*hn*0.5)

            objectNode = ET.Element('object')
            root.append(objectNode)
            xmlappend('name', label, objectNode)
            xmlappend('pose','Unspecified',objectNode)
            xmlappend('truncated','0',objectNode)
            xmlappend('difficult','0',objectNode)
            bndbox = ET.Element('bndbox')
            objectNode.append(bndbox)
            xmlappend('xmin',str(xmin),bndbox)
            xmlappend('ymin',str(ymin),bndbox)
            xmlappend('xmax',str(xmax),bndbox)
            xmlappend('ymax',str(ymax),bndbox)

    # 输出xml
    __indent(root)          # 增加换行符
    tree.write(os.path.join(path, 'txt2xml', name+'.xml'), encoding='utf-8')
    print('finish '+name+'.txt'+' to '+name+'.xml')
    
print('All Completed!')

