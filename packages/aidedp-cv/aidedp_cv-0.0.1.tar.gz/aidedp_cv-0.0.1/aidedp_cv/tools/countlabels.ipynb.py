{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 1,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Star to count label kinds....\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "100%|██████████| 408/408 [00:01<00:00, 226.05it/s]\n"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "5 kind labels and 473 labels in total:\n",
      "['666_jkxl_jyz', 'guadianguanglanshagu', 'guanlanjinjuqinxie45º', 'jueyuanzizibao', 'niaochao']\n",
      "Label Name and it's number:\n",
      "666_jkxl_jyz\t: 6\n",
      "guadianguanglanshagu\t: 1\n",
      "guanlanjinjuqinxie45º\t: 1\n",
      "jueyuanzizibao\t: 4\n",
      "niaochao\t: 461\n"
     ]
    }
   ],
   "source": [
    "import os\n",
    "from tqdm import tqdm\n",
    "import xml.dom.minidom\n",
    "import pandas as pd\n",
    "\n",
    "\"\"\"\n",
    "统计xml数据集的label种类和个数;\n",
    "统计label种类和对应的xml文件名\n",
    "\"\"\"\n",
    "\n",
    "def ReadXml(FilePath):\n",
    "    if os.path.exists(FilePath) is False:\n",
    "        return None\n",
    "    dom = xml.dom.minidom.parse(FilePath)\n",
    "    root_ = dom.documentElement\n",
    "    object_ = root_.getElementsByTagName('object')\n",
    "    info = []\n",
    "    for object_1 in object_:\n",
    "        name = object_1.getElementsByTagName(\"name\")[0].firstChild.data\n",
    "        bndbox = object_1.getElementsByTagName(\"bndbox\")[0]\n",
    "        info.append([name])\n",
    "    return info\n",
    "\n",
    "\n",
    "def CountLabelKind(Path):\n",
    "    LabelDict = {}  # 统计类别种类和个数\n",
    "    Labellist = {}  # 统计类别种类和对应的文件名\n",
    "    print(\"Star to count label kinds....\")\n",
    "    for root, dirs, files in os.walk(Path):\n",
    "        for file in tqdm(files):\n",
    "            Infos = ReadXml(os.path.join(root,file))\n",
    "            for Info in Infos:\n",
    "                if Info[-1] not in LabelDict.keys():\n",
    "                    LabelDict[Info[-1]] = 1\n",
    "                    Labellist[Info[-1]] = [file]\n",
    "                else:\n",
    "                    LabelDict[Info[-1]] += 1\n",
    "                    Labellist[Info[-1]].append(file)\n",
    "\n",
    "    return dict(sorted(LabelDict.items(), key=lambda x: x[0])), \\\n",
    "        dict(sorted(Labellist.items(), key=lambda x: x[0]))\n",
    "\n",
    "\n",
    "if __name__ == '__main__':\n",
    "    # xml文件夹\n",
    "    SrcDir = \"../datasets/niaochao/Annotations/\"\n",
    "    outlabellist_dir = \"../datasets/niaochao/\"     # label种类和对应的xml文件名结果(Labellist)存放目录\n",
    "\n",
    "    LabelDict, Labellist = CountLabelKind(SrcDir)\n",
    "    KeyDict = sorted(LabelDict)\n",
    "    print(\"%d kind labels and %d labels in total:\" % (len(KeyDict), sum(LabelDict.values())))\n",
    "    print(KeyDict)\n",
    "    print(\"Label Name and it's number:\")\n",
    "    for key in KeyDict:\n",
    "        print(\"%s\\t: %d\" % (key, LabelDict[key]))\n",
    "    # 保存csv，并按列去除重复文件名\n",
    "    res = pd.DataFrame(dict([(k, pd.Series(pd.Series(v).unique())) for k, v in Labellist.items()]))\n",
    "    res.to_csv(os.path.join(outlabellist_dir, \"labellist.csv\"))\n",
    "\n"
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
   "execution_count": 23,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Star to count label kinds....\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "100%|██████████| 5/5 [00:00<00:00, 624.78it/s]"
     ]
    },
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "2 kind labels and 23 labels in total:\n",
      "['hat', 'person']\n",
      "Label Name and it's number:\n",
      "hat\t: 22\n",
      "person\t: 1\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "\n"
     ]
    }
   ],
   "source": [
    "import os\n",
    "from tqdm import tqdm\n",
    "import xml.dom.minidom\n",
    "import pandas as pd\n",
    "\n",
    "\"\"\"\n",
    "根据txt统计label种类与个数, 用于观察验证集中样本平衡\n",
    "\"\"\"\n",
    "\n",
    "def ReadXml(FilePath):\n",
    "    if os.path.exists(FilePath) is False:\n",
    "        return None\n",
    "    dom = xml.dom.minidom.parse(FilePath)\n",
    "    root_ = dom.documentElement\n",
    "    object_ = root_.getElementsByTagName('object')\n",
    "    info = []\n",
    "    for object_1 in object_:\n",
    "        name = object_1.getElementsByTagName(\"name\")[0].firstChild.data\n",
    "        bndbox = object_1.getElementsByTagName(\"bndbox\")[0]\n",
    "        info.append([name])\n",
    "    return info\n",
    "\n",
    "def CountLabelsFromTxt(xmlFilenameList, xmldirpath):\n",
    "    LabelDict = {}  # 统计类别种类和个数\n",
    "    Labellist = {}  # 统计类别种类和对应的文件名\n",
    "    print(\"Star to count label kinds....\")\n",
    "    \n",
    "    for file in tqdm(xmlFilenameList):\n",
    "        Infos = ReadXml(os.path.join(xmldirpath,file))\n",
    "        for Info in Infos:\n",
    "            if Info[-1] not in LabelDict.keys():\n",
    "                LabelDict[Info[-1]] = 1\n",
    "                Labellist[Info[-1]] = [file]\n",
    "            else:\n",
    "                LabelDict[Info[-1]] += 1\n",
    "                Labellist[Info[-1]].append(file)\n",
    "\n",
    "    return dict(sorted(LabelDict.items(), key=lambda x: x[0])), \\\n",
    "        dict(sorted(Labellist.items(), key=lambda x: x[0]))\n",
    "\n",
    "# 由此开始\n",
    "targettxt = \"../datasets/hat_person/val_list.txt\"\n",
    "xmldirpath = \"../datasets/hat_person/Annotations/\"\n",
    "\n",
    "# 读取val.txt中txt文件名\n",
    "with open(targettxt, \"r\") as f:\n",
    "    tmp = f.readlines()\n",
    "    xmlFilenameList = [x.split()[1].split(\".\")[0]+\".xml\" for x in tmp]\n",
    "\n",
    "# 统计样本数据集及对应的xml文件名\n",
    "LabelDict, Labellist = CountLabelsFromTxt(xmlFilenameList, xmldirpath)\n",
    "KeyDict = sorted(LabelDict)\n",
    "print(\"%d kind labels and %d labels in total:\" % (len(KeyDict), sum(LabelDict.values())))\n",
    "print(KeyDict)\n",
    "print(\"Label Name and it's number:\")\n",
    "for key in KeyDict:\n",
    "    print(\"%s\\t: %d\" % (key, LabelDict[key]))\n",
    "\n",
    "# 保存csv，并按列去除重复文件名\n",
    "res = pd.DataFrame(dict([(k, pd.Series(pd.Series(v).unique())) for k, v in Labellist.items()]))\n",
    "res.to_csv(\"../datasets/hat_person/val_labels.csv\")"
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
