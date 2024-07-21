# 语义分割-数据增强
import torch
import numpy as np
from PIL import Image

# use the trainer's dataset and data loader to generate the dataset.
from ultralytics.models.yolo.segment import SegmentationTrainer

args = dict(model='yolov8n-seg.yaml', data='coco8-seg.yaml', epochs=3)
trainer = SegmentationTrainer(overrides=args)

# ds_loader = trainer.get_dataloader(trainer.trainset, batch_size=8, rank=0, mode="train")
trainer._setup_train(world_size=1)


# Define a color palette for visualization
def get_palette(num_classes):
    palette = np.zeros((num_classes, 3), dtype=np.uint8)
    for i in range(num_classes):
        palette[i] = np.random.choice(range(256), size=3)
    return palette

palette = get_palette(100)

for i, batch in enumerate(trainer.train_loader):
    # print(type(batch))
    for j, img in enumerate(batch['img']):
        img_np = img.numpy().transpose((1, 2, 0))
        im = Image.fromarray(img_np)
        im.save(f'./vis/{i}-{j}.png')
    for j, mask in enumerate(batch['masks']):
        mask_color = palette[mask.cpu().numpy()]
        mask = Image.fromarray(mask_color)
        mask.save(f'./mask/{i}-{j}.png')

    print(batch['masks'][0].shape)