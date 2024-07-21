import os
from tqdm import tqdm
import xml.dom.minidom
import pandas as pd

"""
统计xml数据集的label种类和个数;
统计label种类和对应的xml文件名
"""

def ReadXml(FilePath):
    if os.path.exists(FilePath) is False:
        return None
    dom = xml.dom.minidom.parse(FilePath)
    root_ = dom.documentElement
    object_ = root_.getElementsByTagName('object')
    info = []
    for object_1 in object_:
        name = object_1.getElementsByTagName("name")[0].firstChild.data
        bndbox = object_1.getElementsByTagName("bndbox")[0]
        info.append([name])
    return info


def CountLabelKind(Path):
    LabelDict = {}  # 统计类别种类和个数
    Labellist = {}  # 统计类别种类和对应的文件名
    print("Star to count label kinds....")
    for root, dirs, files in os.walk(Path):
        for file in tqdm(files):
            Infos = ReadXml(os.path.join(root,file))
            for Info in Infos:
                if Info[-1] not in LabelDict.keys():
                    LabelDict[Info[-1]] = 1
                    Labellist[Info[-1]] = [file]
                else:
                    LabelDict[Info[-1]] += 1
                    Labellist[Info[-1]].append(file)

    return dict(sorted(LabelDict.items(), key=lambda x: x[0])), \
        dict(sorted(Labellist.items(), key=lambda x: x[0]))


if __name__ == '__main__':
    # xml文件夹
    SrcDir = "../datasets/niaochao/Annotations/"
    outlabellist_dir = "../datasets/niaochao/"     # label种类和对应的xml文件名结果(Labellist)存放目录

    LabelDict, Labellist = CountLabelKind(SrcDir)
    KeyDict = sorted(LabelDict)
    print("%d kind labels and %d labels in total:" % (len(KeyDict), sum(LabelDict.values())))
    print(KeyDict)
    print("Label Name and it's number:")
    for key in KeyDict:
        print("%s\t: %d" % (key, LabelDict[key]))
    # 保存csv，并按列去除重复文件名
    res = pd.DataFrame(dict([(k, pd.Series(pd.Series(v).unique())) for k, v in Labellist.items()]))
    res.to_csv(os.path.join(outlabellist_dir, "labellist.csv"))


# ------------------------------------------------
# 根据txt统计label种类与个数, 用于观察验证集中样本平衡
# ------------------------------------------------
import os
from tqdm import tqdm
import xml.dom.minidom
import pandas as pd

"""
根据txt统计label种类与个数, 用于观察验证集中样本平衡
"""

def ReadXml(FilePath):
    if os.path.exists(FilePath) is False:
        return None
    dom = xml.dom.minidom.parse(FilePath)
    root_ = dom.documentElement
    object_ = root_.getElementsByTagName('object')
    info = []
    for object_1 in object_:
        name = object_1.getElementsByTagName("name")[0].firstChild.data
        bndbox = object_1.getElementsByTagName("bndbox")[0]
        info.append([name])
    return info

def CountLabelsFromTxt(xmlFilenameList, xmldirpath):
    LabelDict = {}  # 统计类别种类和个数
    Labellist = {}  # 统计类别种类和对应的文件名
    print("Star to count label kinds....")
    
    for file in tqdm(xmlFilenameList):
        Infos = ReadXml(os.path.join(xmldirpath,file))
        for Info in Infos:
            if Info[-1] not in LabelDict.keys():
                LabelDict[Info[-1]] = 1
                Labellist[Info[-1]] = [file]
            else:
                LabelDict[Info[-1]] += 1
                Labellist[Info[-1]].append(file)

    return dict(sorted(LabelDict.items(), key=lambda x: x[0])), \
        dict(sorted(Labellist.items(), key=lambda x: x[0]))

# 由此开始
targettxt = "../datasets/hat_person/val_list.txt"
xmldirpath = "../datasets/hat_person/Annotations/"

# 读取val.txt中xml文件名
with open(targettxt, "r") as f:
    tmp = f.readlines()
    xmlFilenameList = [x.split()[1] for x in tmp]

# 统计样本数据集及对应的xml文件名
LabelDict, Labellist = CountLabelsFromTxt(xmlFilenameList, xmldirpath)
KeyDict = sorted(LabelDict)
print("%d kind labels and %d labels in total:" % (len(KeyDict), sum(LabelDict.values())))
print(KeyDict)
print("Label Name and it's number:")
for key in KeyDict:
    print("%s\t: %d" % (key, LabelDict[key]))

# 保存csv，并按列去除重复文件名
res = pd.DataFrame(dict([(k, pd.Series(pd.Series(v).unique())) for k, v in Labellist.items()]))
res.to_csv("../datasets/hat_person/val_labels.csv")
