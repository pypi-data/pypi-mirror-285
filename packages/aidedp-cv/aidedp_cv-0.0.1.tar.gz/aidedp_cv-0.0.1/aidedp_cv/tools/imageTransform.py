#python+opencv+数据增强
#旋转，平移，裁减, 镜像，缩放，噪声, 滤波，亮度
import cv2 as cv
import numpy as np
import random
import os
import xml.etree.ElementTree as ET
from lxml import etree, objectify
from tqdm import tqdm

"""
修改main中的路径, 修改dataAugment()中change_num增强次数, 修改对应方法中的参数
"""

class Aug():
    def __init__(self,
                    shift_rate=0.5,#平移率
                    crop_rate=0.5,#裁减的概率
                    flip_rate=0.5,#镜像翻转概率
                    rota_rate=1,#旋转概率
                    resize_rate=0.5,#缩放概率
                    addnoise_rate=0.5,#加噪声概率
                    addblur_rate=0.5,#加滤波概率
                    change_light_rate=0.5,#改变亮度
                    is_shift_pic=False,#是否开启平移
                    is_crop_pic=False,#是否开启裁剪
                    is_flip_pic=False,#是否镜像
                    is_rota_pic=True,#是否旋转  
                    is_resize_pic=False,#是否开启缩放
                    is_addnoise=False,#是否开启噪声
                    is_addblur=False,#是否开启滤波
                    is_changelight=False#是否改变亮度
                    ):
        #参数配置 概率
        self.shift_rate=shift_rate#平移参数，默认1
        self.crop_rate=crop_rate#裁剪参数，默认1
        self.flip_rate=flip_rate#镜像参数，默认1
        self.rota_rate=rota_rate#旋转参数，默认1
        self.resize_rate=resize_rate#缩放参数，默认1
        self.addnoise_rate=addnoise_rate#噪声参数，默认1
        self.addblur_rate=addblur_rate#噪声参数，默认1
        self.change_light_rate=change_light_rate#改变亮度参数，默认1


        #是否开启增强模式
        self.is_shift_pic = is_shift_pic
        self.is_crop_pic = is_crop_pic
        self.is_flip_pic = is_flip_pic
        self.is_rota_pic = is_rota_pic
        self.is_resize_pic = is_resize_pic
        self.is_addnoise = is_addnoise
        self.is_addblur = is_addblur
        self.is_changelight = is_changelight
    
    #随机平移
    def _shift_pic(self ,img ,bboxes):
        '''
        img:原始图像
        bboxes：图片所有标注框的集合。

        返回值：
        shift_img平移后的图像
        shift_bboxes：平移后的bbox
        '''
        #防止标注目标在平移时溢出图片
        w=img.shape[1]
        h=img.shape[0]
        x_min=w
        x_max=0
        y_min=h
        y_max=0
        for bbox in bboxes:#找到最值坐标
            x_min=min(x_min,bbox[0])
            y_min=min(y_min,bbox[1])
            x_max=max(x_max,bbox[2])
            y_max=max(y_max,bbox[3])
        top_left=x_min#bbox最大左移距离
        top_right=w-x_max#bbox最大右边移动距离
        top_top=y_min#bbox最大上移距离
        top_bottom=h-y_max#bbox最大下移动距离

        #uniform:从一个均匀分布[low,high)中随机采样
        x = np.random.uniform(-(top_left - 1)/3, (top_right - 1)/3)
        y = np.random.uniform(-(top_top - 1)/3, (top_bottom - 1)/3)#为啥除以3
        
        # x为向左或右移动的像素值,正为向右负为向左; y为向上或者向下移动的像素值,正为向下负为向上
        M = np.float32([[1, 0, x], [0, 1, y]])
        #img:输入图像 M：变换矩阵 (img.shape[1], img.shape[0])：变换后的尺寸，默认没变  
        shift_img = cv.warpAffine(img, M, (img.shape[1], img.shape[0]))

        #平移bbox
        shift_bboxes=[ ]
        for bbox in bboxes:
            shift_bboxes.append([bbox[0] + x, bbox[1] + y, bbox[2] + x, bbox[3] + y])

        return shift_img,shift_bboxes

    #图像裁剪
    def _crop_pic(self,img,bboxes):
        '''
        img:原始图像
        bboxes：图片所有标注框的集合。

        返回值：
        crop_img裁剪后的图像
        crop_bboxes：裁剪后的bbox
        '''
        w=img.shape[1]
        h=img.shape[0]
        x_min=w
        x_max=0
        y_min=h
        y_max=0
        for bbox in bboxes:#找到最值坐标
            x_min=min(x_min,bbox[0])
            y_min=min(y_min,bbox[1])
            x_max=max(x_max,bbox[2])
            y_max=max(y_max,bbox[3])
        top_left=x_min#bbox最大左移距离
        top_right=w-x_max#bbox最大右边移动距离
        top_top=y_min#bbox最大上移距离
        top_bottom=h-y_max#bbox最大下移动距离

        #随机扩大这个包含所有bbox的大框
        #random.randint()方法里面的取值区间是前闭后闭区间，
        # 而np.random.randint()方法的取值区间是前闭后开区间
        crop_x_min = int(x_min - random.uniform(0, top_left))
        crop_y_min = int(y_min - random.uniform(0, top_top))
        crop_x_max = int(min(w,x_max + random.uniform(0, top_right)))#防止过大溢出边界
        crop_y_max = int(min(h,y_max + random.uniform(0, top_bottom)))

        crop_img = img[crop_y_min:crop_y_max, crop_x_min:crop_x_max]#裁剪图片
        #裁剪bbox
        crop_bboxes = []
        for bbox in bboxes:
            crop_bboxes.append([
                bbox[0]-crop_x_min, 
                bbox[1]-crop_y_min,
                bbox[2]-crop_x_min, 
                bbox[3]-crop_y_min])
 
        return crop_img, crop_bboxes

    #镜像图片
    def _flip_pic(self,img,bboxes):
        '''
        img:原始图像
        bboxes：图片所有标注框的集合。

        返回值：
        flip_img镜像后的图像
        flip_bboxes：镜像后的bbox
        '''
        w=img.shape[1]
        h=img.shape[0]
        flip_img=cv.flip(img,1)#水平翻转
        #bbox翻转
        flip_bboxes=[]
        for box in bboxes:
            x_min = box[0]
            y_min = box[1]
            x_max = box[2]
            y_max = box[3]

            flip_bboxes.append([w - x_max, y_min, w - x_min, y_max])

        return flip_img, flip_bboxes

    #旋转图片
    def _rota_pic(self,img,bboxes):
        '''
        img:原始图像
        bboxes：图片所有标注框的集合。

        返回值：
        rota_img旋转后的图像
        rota_bboxes：旋转后的bbox

        getRotationMatrix2D：
        double alpha = cos(angle)*scale;
        double beta = sin(angle)*scale;
        [[ m[0] = alpha;m[1] = beta;m[2] = (1-alpha)*center.x - beta*center.y; ],
          [m[3] = -beta;m[4] = alpha;m[5] = beta*center.x + (1-alpha)*center.y;]]     shape(2,3)
        '''
        w=img.shape[1]
        h=img.shape[0]
        #旋转图片
        center=(w/2,h/2)
        # angle=random.randint(-180,180)#随机生成角度
        angle = 90
        M = cv.getRotationMatrix2D(center, angle, 1.0)
        ##第一个参数：旋转中心点(正数为逆时针旋转，负数为正时针)  
        # 第二个参数：旋转角度 第三个参数：缩放比例
        #[[-9.87688341e-01  -1.56434465e-01  2.81539911e+03]第一个是cos角度，第二个是sin角度
        # [1.56434465e-01 -9.87688341e-01  2.34557672e+03]]

        cos = np.abs(M[0, 0])
        sin = np.abs(M[0, 1])
        nW = int((h * sin) + (w * cos))#新的尺寸 nw,nh
        nH = int((h * cos) + (w * sin))
        M[0, 2] += (nW / 2) - center[0]#新的中心坐标
        M[1, 2] += (nH / 2) - center[1]
        rota_img= cv.warpAffine(img, M, (nW, nH))
        # 第一个参数为原图，第二个参数为旋转矩阵，第三个参数为图像（宽，高）的元组，
        # 旋转后的图片需要包含所有的框，否则会对图像的原始标注造成破坏。
        # 所以要变换图片尺寸，加载数据时在resize到需要大小
        # 旋转bbox
        rota_bboxes=[]
        for bbox in bboxes:
            xmin = bbox[0]
            ymin = bbox[1]
            xmax = bbox[2]
            ymax = bbox[3]

            # 得到旋转后的坐标
            #dot(点乘)
            #取中点值是为了旋转后，用boundingRect算出最小外接正矩形，尽量避免加入无关信息
            point1 = np.dot(M, np.array([(xmin + xmax) / 2, ymin, 1]))
            point2 = np.dot(M, np.array([xmax, (ymin + ymax) / 2, 1]))
            point3 = np.dot(M, np.array([(xmin + xmax) / 2, ymax, 1]))
            point4 = np.dot(M, np.array([xmin, (ymin + ymax) / 2, 1]))
            # 合并np.array
            concat = np.vstack((point1, point2, point3, point4))
            # vstack输入[1 2 3]和[4 5 6]
            # 输出[[1 2 3], [4 5 6]]
            # 改变array类型
            concat = concat.astype(np.int32)
            rx, ry, rw, rh = cv.boundingRect(concat)#旋转后目标的距行框（没有角度）的xywh
            rx_min = rx
            ry_min = ry
            rx_max = rx + rw
            ry_max = ry + rh
            rota_bboxes.append([rx_min, ry_min, rx_max, ry_max])
        return rota_img ,rota_bboxes

    #图片缩放/放大
    def _resize_pic(self,img,bboxes):
        '''
        在实际应用中，输入图像大小是固定不变，
        这样在缩放图片后，如果是放大，
        则需要剪裁，如果缩写，则出现空余区域。

        resize函数：第一个参数为待缩放的图像，第二个参数为缩放后的图像尺寸大小.
        第三个和第四个参数为缩放尺度因子，第五个参数为缩放的插值方法。

        插值方法：
        默认时使用的是cv2.INTER_LINEAR
        缩小时推荐使用cv2.INTER_AREA
        扩展放大时推荐使用cv2.INTER_CUBIC 和 cv2.INTER_LINEAR，前者比后者运行速度慢。
        '''
        #缩小图片
        w=img.shape[1]
        h=img.shape[0]
        #resize_img=cv.resize(img,(w,h),fx=1.5,fy=1.5,interpolation=cv.INTER_CUBIC)
        resize_img=cv.resize(img,(w//2,h//2),interpolation=cv.INTER_CUBIC)#resize要整数

        #缩小bbox
        resize_bboxes = []
        for bbox in bboxes:
            resize_bboxes.append([bbox[0]//2, bbox[1]//2, bbox[2]//2, bbox[3]//2])
 
        return resize_img, resize_bboxes

    #添加滤波
    def _addblur(self, img):
        '''
        输入:
            img:图像array
        输出:
            高斯滤波
            GaussianBlur()第二个参数是高斯核大小,一般为奇数, b2=h/w*b1
    '''
        w=img.shape[1]
        h=img.shape[0]
        bl1=random.randrange(1,10,2)#随机1-10的奇数
        #print(bl1)
        bl2=int(h/w*bl1)
        if bl2%2==0:
            bl3=bl2+1
        else:
            bl3=bl2
        #print(bl3)
        addblur_img=cv.GaussianBlur(img, (bl1, bl3), 0)

        return addblur_img

    #添加噪声
    def _addnoise(self, img):
        '''
        添加高斯噪声
        mean : 均值 
        var : 方差
        输入:
            img:图像array
        输出:
            高斯噪声
    '''
        mean=0
        var=0.01
        img = np.array(img/255, dtype=float)#图像进行归一化，范围为[0, 1]
        noise = np.random.normal(mean, var ** 1, img.shape)#生成高斯分布的概率密度随机数
        out = img + noise
        if out.min() < 0:
            low_clip = -1.
        else:
            low_clip = 0.
        out = np.clip(out, low_clip, 1.0)#其中out是一个数组，后面两个参数分别表示最小和最大值
        addnoise_img = np.uint8(out*255)#返回原色彩图

        return addnoise_img

    # 调整亮度
    def _changelight(self, img):
        
        a = random.uniform(0.35, 1)#随机生成a
        h, w, ch = img.shape#获取shape的数值，height和width、通道

        #新建全零图片数组src2,将height和width，类型设置为原图片的通道类型(色素全为零，输出为全黑图片)
        src2 = np.zeros([h, w, ch], img.dtype)
        changel_img = cv.addWeighted(img, a, src2, 1-a, 10)#a为对比度  第二个为亮度数值越大越亮
    
        return changel_img

    # 图像增强方法
    def dataAugment(self, img, bboxes):
        '''
        图像增强：
        输入:
            img:图像array
            bboxes:该图像的所有框坐标
        输出:
            img:增强后的图像
            bboxes:增强后图片对应的box'''
        change_num = 2  # 改变的次数
        # print('------start-------')
        while change_num < 3:  # 增强次数
            if self.is_rota_pic:
                if random.random() < self.rota_rate:  # 旋转
                    change_num += 1
                    img, bboxes = self._rota_pic(img, bboxes)
                    # print("旋转")
            if self.is_shift_pic==True:
                if random.random() < self.shift_rate:  # 平移：随机数小于设置的概率则会触发
                    change_num += 1
                    img, bboxes = self._shift_pic(img, bboxes)
                    # print("平移")
            if self.is_resize_pic:
                if random.random() < self.resize_rate:  # 缩放：随机数小于设置的概率则会触发
                    change_num += 1
                    img, bboxes = self._resize_pic(img, bboxes)
                    # print("缩放")
            if self.is_changelight:
                if random.random() < self.change_light_rate:  # 改变亮度
                    change_num += 1
                    img = self._changelight(img)
                    # print("亮度")
            if self.is_addnoise:
                if random.random() < self.addnoise_rate:  # 加噪声
                    change_num += 1
                    img = self._addnoise(img)
                    # print("噪声")
            if self.is_addblur:
                if random.random() < self.addblur_rate:  # 加滤波
                    change_num += 1
                    img = self._addblur(img)
                    # print("滤波")
            if self.is_flip_pic:
                if random.random() < self.flip_rate:  # 翻转
                    change_num += 1
                    img, bboxes = self._flip_pic(img, bboxes)
                    # print("翻转")
            if self.is_crop_pic:
                if random.random() < self.crop_rate:  # 裁剪
                    change_num += 1
                    img, bboxes = self._crop_pic(img, bboxes)
                    # print("裁剪")
        # print('---------end---------')
        return img, bboxes

class xml():
    #xml读取
    def parse_xml(self,path):
        '''
            输入：
                xml_path: xml的文件路径
            输出：
                从xml文件中提取bounding box信息, 格式为[[x_min, y_min, x_max, y_max, name]]
    '''
        tree = ET.parse(path)
        root = tree.getroot()
        objs = root.findall('object')
        coords = list()
        for ix, obj in enumerate(objs):
            name = obj.find('name').text
            box = obj.find('bndbox')
            x_min = int(box[0].text)
            y_min = int(box[1].text)
            x_max = int(box[2].text)
            y_max = int(box[3].text)
            coords.append([x_min, y_min, x_max, y_max, name])
        return coords

        # 保持xml结果
    def save_xml(self, file_name, save_folder, img_info, height, width, channel, bboxs_info):
        '''
        :param file_name:文件名
        :param save_folder:#保存的xml文件的结果
        :param height:图片的高度
        :param width:图片的宽度
        :param channel:通道
        :return:
    '''
        folder_name, img_name = img_info  # 得到图片的信息

        E = objectify.ElementMaker(annotate=False)

        anno_tree = E.annotation(
            E.folder(folder_name),
            E.filename(img_name),
            E.path(os.path.join(folder_name, img_name)),
            E.source(
                E.database('Unknown'),
            ),
            E.size(
                E.width(width),
                E.height(height),
                E.depth(channel)
            ),
            E.segmented(0),
        )
        #添加每一个标签和bbox信息
        labels, bboxs = bboxs_info  # 得到边框和标签信息
        '''
        zip()例如输入，a = [1,2,3]和b = [4,5,6]，zip(a,b)=[(1, 4), (2, 5), (3, 6)]
        '''
        for label, box in zip(labels, bboxs):
            anno_tree.append(
                E.object(
                    E.name(label),
                    E.pose('Unspecified'),
                    E.truncated('0'),
                    E.difficult('0'),
                    E.bndbox(
                        E.xmin(box[0]),
                        E.ymin(box[1]),
                        E.xmax(box[2]),
                        E.ymax(box[3])
                    )
                ))
                
        #格式会好看
        etree.ElementTree(anno_tree).write(os.path.join(save_folder, file_name), pretty_print=True)
        

if __name__=='__main__':
    img_path="../datasets/hat_person/testimgs/"#图片路径1
    xml_path="../datasets/hat_person/testAnnotations/"#xml路径
    save_img_path="../datasets/hat_person/rotated_JPEGImages/"#图片保存路径
    save_xml_path="../datasets/hat_person/rotated_Annotations/"#xml保存路径
     
    #不存在就创建文件
    if not os.path.exists(save_img_path):
        os.mkdir(save_img_path)

    if not os.path.exists(save_xml_path):
        os.mkdir(save_xml_path)
    
    aug=Aug()
    x=xml()

    for img_file in tqdm(os.listdir(img_path)):
        #pic=os.path.join(img_path,file)
        #print(img_file)
        pic_m_path = os.path.join(img_path, img_file)
        img=cv.imread(pic_m_path)
        
        xml_m_path=os.path.join(xml_path,img_file.split(".")[0]+".xml")
        # 修改每个xml保存名称，以防重复
        xml_file=img_file.split(".")[0] + "-rote90" +".xml"
        # 修改每个图片保存名称，以防重复
        img_file = os.path.splitext(img_file)[0] + "-rote90" + os.path.splitext(img_file)[1]
        
        print(xml_m_path)
        values =x.parse_xml(xml_m_path)  # 解析得到box信息，格式为[[x_min,y_min,x_max,y_max,name]
        # values =x.parse_xml("/home/liu/下载/test/xml/000002.xml")
        coords = [v[:4] for v in values]  # 得到框
        labels = [v[-1] for v in values]  # 对象的标签

        auged_img, auged_bboxes = aug.dataAugment(img, coords)#增强后的图片和bbox

        auged_bboxes_int = np.array(auged_bboxes).astype(np.int32)#变成矩阵格式
        #img_name = '{}_{}{}'.format(_file_prefix, cnt + 1, _file_suffix)  # 图片保存的信息
        #保存增强后图片
        cv.imwrite(os.path.join(save_img_path, img_file), auged_img)
        #保存增强后的xml
        height, width, channel = auged_img.shape  # 得到图片的属性
        x.save_xml(xml_file,save_xml_path,(save_img_path,img_file),\
            height, width, channel,(labels, auged_bboxes_int))



