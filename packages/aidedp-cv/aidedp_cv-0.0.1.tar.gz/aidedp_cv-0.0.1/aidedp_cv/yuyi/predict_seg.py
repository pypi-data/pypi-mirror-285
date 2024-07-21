import os
import torch
from torchvision import transforms, models
from PIL import Image
import numpy as np

def predict(model, device, input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    model.eval()
    # transform = transforms.Compose([
    #     transforms.Resize((256, 256)),
    #     transforms.ToTensor(),
    #     transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    # ])

    # Define transformations
    image_transform = transforms.Compose([
        transforms.Resize((256, 256), interpolation=transforms.InterpolationMode.NEAREST),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    transform = image_transform
    
    with torch.no_grad():
        for image_name in os.listdir(input_folder):
            if image_name.endswith(('.png')):
                image_path = os.path.join(input_folder, image_name)
                image = Image.open(image_path).convert("RGB")
                original_size = image.size
                
                input_image = transform(image).unsqueeze(0).to(device)
                output = model(input_image)['out']
                prediction = torch.argmax(output.squeeze(), dim=0).cpu().numpy().astype(np.uint8)
                
                # Resize the prediction back to the original size
                prediction_image = Image.fromarray(prediction).resize(original_size, resample=Image.NEAREST)
                
                output_image_path = os.path.join(output_folder, image_name)
                prediction_image.save(output_image_path)

# Example usage
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = models.segmentation.deeplabv3_resnet50(pretrained=False, pretrained_backbone=False, num_classes=9)
model.load_state_dict(torch.load('best_model.pth'))
model = model.to(device)

input_folder = '/root/autodl-tmp/yolo/val_image'
output_folder = '/root/autodl-tmp/yolo/out_put'

# original_size_folder = '/home/huasi/AllNeedCopy_datasets/v5_test/yolov5-master/yolov5-master/custom_dataset/minicity/aachen_img'

predict(model, device, input_folder, output_folder)
