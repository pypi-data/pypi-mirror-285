# 1 安装环境
# pip install ultralytics 

# 验证环境是否安装完备
'''
  import ultralytics
  ultralytics.__version__
  import torch
  torch.cuda.is_available()
'''

# 2 数据集格式转化 labelme->yolo
# 注意：json与图片放一个文件夹
# pip install labelme2yolo
'''
labelme2yolo --json_dir 数据存放文件夹
'''
# 注释yolov8自动下载的代码
# miniconda3/envs/yolo/lib/python3.10/site-packages/ultralytics/utils/checks.py 里面搜索"def check_font.."
# 注释最后三行，'if downloads.is_url(ur...'




