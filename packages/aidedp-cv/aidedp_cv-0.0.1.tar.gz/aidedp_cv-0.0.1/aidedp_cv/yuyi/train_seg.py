# Model in /root/.cache/torch/hub/checkpoints
import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
from torchvision import models, transforms
# import torch.nn.functional as F
from PIL import Image
import numpy as np
from tqdm import tqdm

class SegmentationDataset(Dataset):
    def __init__(self, image_folder, mask_folder, transform=None, mask_transform=None):
        self.image_folder = image_folder
        self.mask_folder = mask_folder
        self.transform = transform
        self.mask_transform = mask_transform
        self.image_files = sorted(os.listdir(image_folder))
        self.mask_files = sorted(os.listdir(mask_folder))
        self.class_mapping = {
            "person": 0,
            "rider": 1,
            "car": 2,
            "truck": 3,
            "bus": 4,
            "train": 5,
            "motorcycle": 6,
            "bicycle": 7
        }
        
    def __len__(self):
        return len(self.image_files)

    def __getitem__(self, idx):
        img_path = os.path.join(self.image_folder, self.image_files[idx])
        mask_path = os.path.join(self.mask_folder, self.mask_files[idx])
        
        image = Image.open(img_path).convert("RGB")
        mask = Image.open(mask_path).convert("L")
        
        if self.transform:
            image = self.transform(image)
        if self.mask_transform:
            mask = self.mask_transform(mask)
        
        mask = torch.tensor(np.array(mask), dtype=torch.long)
        
        return image, mask

# Define transformations
image_transform = transforms.Compose([
    transforms.Resize((256, 256), interpolation=transforms.InterpolationMode.NEAREST),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
])

mask_transform = transforms.Compose([
    transforms.PILToTensor(),
    transforms.Resize((256, 256), interpolation=transforms.InterpolationMode.NEAREST),
])

# Define paths
train_image_folder = '/root/autodl-tmp/yolo/aachen_image'
train_mask_folder = '/root/autodl-tmp/yolo/aachen_mask'
val_image_folder = '/root/autodl-tmp/yolo/val_image'
val_mask_folder = '/root/autodl-tmp/yolo/val_mask'

# Create datasets and dataloaders
train_dataset = SegmentationDataset(train_image_folder, train_mask_folder, transform=image_transform, mask_transform=mask_transform)
val_dataset = SegmentationDataset(val_image_folder, val_mask_folder, transform=image_transform, mask_transform=mask_transform)
train_loader = DataLoader(train_dataset, batch_size=4, shuffle=True, num_workers=4)
val_loader = DataLoader(val_dataset, batch_size=4, shuffle=False, num_workers=4)

# Tensor Board support:
# 开始训练后，在terminal运行: tensorboard --logdir=runs
# 之后根据提示在浏览器打开tensorboard可查看训练流程。
# from torch.utils.tensorboard import SummaryWriter

# Initialize the model
# 不加载预训练模型
# model = models.segmentation.deeplabv3_resnet50(pretrained=False, pretrained_backbone=False, num_classes=21)
model = models.segmentation.deeplabv3_resnet50(num_classes=21)  # 加载预训练模型

# Move the model to GPU if available
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)

# Define the loss function and optimizer
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# Function to calculate the validation loss
def validate(model, val_loader, criterion, device):
    model.eval()
    val_loss = 0.0
    with torch.no_grad():
        for images, masks in tqdm(val_loader, desc='Validation', leave=False):
            images = images.to(device)
            masks = masks.to(device).squeeze(1)  # Remove the singleton dimension
            outputs = model(images)['out']
            loss = criterion(outputs, masks)
            val_loss += loss.item()
    return val_loss / len(val_loader)

# Set up TensorBoard writer
# writer = SummaryWriter()

# Training loop
num_epochs = 3
best_val_loss = float('inf')

for epoch in range(num_epochs):
    model.train()
    running_loss = 0.0
    for images, masks in tqdm(train_loader, desc=f'Training Epoch {epoch+1}/{num_epochs}'):
        images = images.to(device)
        if (images.shape[0] < 4):
            continue
        masks = masks.to(device).squeeze(1)  # Remove the singleton dimension
        # print(masks.shape)
        
        # Zero the parameter gradients
        optimizer.zero_grad()
        
        # Forward pass
        outputs = model(images)['out']
        # print(outputs.shape)
        loss = criterion(outputs, masks)
        
        # Backward pass and optimize
        loss.backward()
        optimizer.step()
        
        running_loss += loss.item()
    
    train_loss = running_loss / len(train_loader)
    val_loss = validate(model, val_loader, criterion, device)
    # # Log the loss values to TensorBoard
    # writer.add_scalar('Loss/train', train_loss, epoch)
    # writer.add_scalar('Loss/val', val_loss, epoch)
    
    print(f"Epoch [{epoch+1}/{num_epochs}], Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}")
    
    # Save the best model
    if val_loss < best_val_loss:
        best_val_loss = val_loss
        torch.save(model.state_dict(), 'best_model.pth')

# # Close the TensorBoard writer
# writer.close()
print("Training complete")


