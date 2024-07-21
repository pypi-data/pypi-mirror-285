from ultralytics import YOLO
model = YOLO("yolov8s-seg.pt")  # build a new model from YAML
# Train the model 
results = model.train(data='/root/autodl-tmp/yolo/data.yaml', epochs=5, imgsz=640, amp=False, multi_scale=False, cos_lr=True) 


'''
参数说明：

'''