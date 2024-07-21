# pip install opencv-python
import cv2
import os

# 视频文件路径
video_path = r"E:\NLP\20240709082801-NLP授课-视频-1.mp4"

# 输出图片的文件夹路径
output_folder = "output folder"

# 检查输出文件夹是否存在，如果不存在则创建
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# 打开视频文件
cap = cv2.VideoCapture(video_path)

# 获取视频总帧数
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

# 设置每隔多少帧保存一次图片
frame_interval = 60  # 例如，每隔60帧保存一次

# 输出将要保存的图片数量
print(f"将每隔 {frame_interval} 帧保存一次图片，共将保存 {total_frames // frame_interval} 张图片（如果有余数则最后一张也会保存）。")

# 开始截帧
frame_count = 0
save_count = 0
while True:
    # 读取一帧
    ret, frame = cap.read()
    
    # 如果正确读取帧，ret为True
    if not ret:
        break
    
    # 如果帧计数是帧间隔的倍数，则保存图片
    if frame_count % frame_interval == 0:
        # 保存图片
        image_filename = os.path.join(output_folder, f"frame_{save_count:06d}.png")
        cv2.imwrite(image_filename, frame)
        save_count += 1
    
    # 更新帧计数
    frame_count += 1
    if frame_count>=300:
        break

# 释放视频捕获对象
cap.release()
print("图片保存完成。")