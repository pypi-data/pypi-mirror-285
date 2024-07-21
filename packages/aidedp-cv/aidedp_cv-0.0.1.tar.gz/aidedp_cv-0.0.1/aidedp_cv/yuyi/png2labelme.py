# pip install scikit-image

import os
import json
import numpy as np
from PIL import Image
from skimage import measure

def masks_to_labelme(mask_folder, image_folder, class_mapping, output_folder):
    # Ensure the output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Reverse the class mapping
    reverse_class_mapping = {v: k for k, v in class_mapping.items()}
    
    # Process each mask file in the mask folder
    for filename in os.listdir(mask_folder):
        if filename.endswith('.png'):
            mask_path = os.path.join(mask_folder, filename)
            image_path = os.path.join(image_folder, os.path.splitext(filename)[0] + '.png')
            output_path = os.path.join(output_folder, os.path.splitext(filename)[0] + '.json')
            
            mask = np.array(Image.open(mask_path))
            image = Image.open(image_path)
            image_width, image_height = image.size
            
            shapes = []
            for class_number, class_label in reverse_class_mapping.items():
                class_mask = mask == class_number
                contours = measure.find_contours(class_mask, 0.5)
                
                for contour in contours:
                    contour = np.flip(contour, axis=1)
                    points = contour.tolist()
                    shape = {
                        "label": class_label,
                        "points": points,
                        "group_id": None,
                        "shape_type": "polygon",
                        "flags": {}
                    }
                    shapes.append(shape)
            
            labelme_json = {
                "version": "5.5.0",
                "flags": {},
                "shapes": shapes,
                "imagePath": os.path.basename(image_path),
                "imageData": None,
                "imageWidth": image_width,
                "imageHeight": image_height
            }
            
            with open(output_path, 'w') as f:
                json.dump(labelme_json, f, indent=4)

# Example usage
# class_mapping = {
#     "rocky": 100,
#     "class2": 2,
#     "class3": 3
# }
class_mapping = {
    "person": 1,
    "rider": 2,
    "car": 3,
    "truck": 4,
    "bus": 5,
    "train": 6,
    "motorcycle": 7,
    "bicycle": 8
}


mask_folder = '/root/autodl-tmp/yolo/val_mask'
image_folder = '/root/autodl-tmp/yolo/val_image'
output_folder = '/root/autodl-tmp/yolo/png2labelme'

masks_to_labelme(mask_folder, image_folder, class_mapping, output_folder)
