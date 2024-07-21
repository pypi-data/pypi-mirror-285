from ultralytics import YOLO
model = YOLO("runs/segment/train10/weights/best.pt")
model.predict("predictImg", save=True, save_txt=True, augment=True, conf=0.28)

'''
参数解析:
    source：输入源的目录，可以是图像或视频文件。
    conf：目标检测的对象置信度阈值。只有置信度高于此阈值的对象才会被检测出来。默认值为0.25。
    iou：非极大值抑制（NMS）的交并比（IoU）阈值。用于在重叠较大的候选框中选择最佳的检测结果。默认值为0.7。
    half：是否使用半精度（FP16）进行推理。半精度可以减少计算量，但可能会牺牲一些精度。默认值为False。
    device：模型运行的设备，可以是cuda设备（cuda device=0/1/2/3）或CPU（device=cpu）。
    show：是否显示检测结果。如果设置为True，则会在屏幕上显示检测到的对象。默认值为False。
    save：是否保存带有检测结果的图像。如果设置为True，则会将检测结果保存为图像文件。默认值为False。
    save_txt：是否将检测结果保存为文本文件（.txt）。默认值为False。
    save_conf：是否将检测结果与置信度分数一起保存。默认值为False。
    save_crop：是否保存裁剪后的带有检测结果的图像。默认值为False。
    hide_labels：是否隐藏标签。如果设置为True，则在显示检测结果时不显示对象标签。默认值为False。
    hide_conf：是否隐藏置信度分数。如果设置为True，则在显示检测结果时不显示置信度分数。默认值为False。
    max_det：每张图像的最大检测数。如果检测到的对象数超过此值，将保留置信度高低来保留。默认值为300。
    vid_stride：视频帧率步长。默认值为False，表示使用默认的帧率。
    line_width：边界框的线宽。如果设置为None，则根据图像大小进行自动缩放。默认值为None。
    visualize：是否可视化模型特征。默认值为False。
    augment：是否对预测源应用图像增强。默认值为False。
    agnostic_nms：是否使用类别无关的NMS。默认值为False。
    retina_masks：是否使用高分辨率的分割掩膜。默认值为False。
    classes：按类别过滤结果。可以指定单个类别（例如class=0）或多个类别（例如class=[0,2,3]）。默认值为None，表示不进行类别过滤。
    boxes：在分割预测中显示边界框。默认值为True。
'''
