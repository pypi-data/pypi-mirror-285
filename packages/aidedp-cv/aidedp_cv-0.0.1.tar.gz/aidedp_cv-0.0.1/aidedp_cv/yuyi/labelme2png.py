import json
# import numpy as np
from PIL import Image, ImageDraw

# def labelme_to_mask(json_file, class_mapping, output_path):
#     # Load the JSON file
#     with open(json_file, 'r') as f:
#         data = json.load(f)
    
#     # Get the image dimensions
#     image_width = data['imageWidth']
#     image_height = data['imageHeight']
    
#     # Create a blank mask image
#     mask = Image.new('L', (image_width, image_height), 0)
#     draw = ImageDraw.Draw(mask)
    
#     # Draw polygons on the mask
#     for shape in data['shapes']:
#         label = shape['label']
#         if label in class_mapping:
#             class_number = class_mapping[label]
#         else:
#             continue
        
#         points = shape['points']
#         polygon = [(point[0], point[1]) for point in points]
#         draw.polygon(polygon, outline=class_number, fill=class_number)
    
#     # Save the mask image
#     mask.save(output_path)

import json
import os
from PIL import Image, ImageDraw

def labelme_folder_to_masks(input_folder, class_mapping, output_folder):
    # Ensure the output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Process each JSON file in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith('.json'):
            json_path = os.path.join(input_folder, filename)
            with open(json_path, 'r') as f:
                data = json.load(f)
            
            # Get the image dimensions
            image_width = data['imageWidth']
            image_height = data['imageHeight']
            
            # Create a blank mask image
            mask = Image.new('L', (image_width, image_height), 0)
            draw = ImageDraw.Draw(mask)
            
            # Draw polygons on the mask
            for shape in data['shapes']:
                label = shape['label']
                if label in class_mapping:
                    class_number = class_mapping[label]
                else:
                    continue
                
                points = shape['points']
                polygon = [(point[0], point[1]) for point in points]
                draw.polygon(polygon, outline=class_number, fill=class_number)
            
            # Save the mask image
            mask_filename = os.path.splitext(filename)[0] + '.png'
            mask_path = os.path.join(output_folder, mask_filename)
            mask.save(mask_path)

# Example usage
class_mapping = {
    # "road": 0,
    # "sidewalk": 1,
    # "building": 2,
    # "wall": 3,
    # "fence": 4,
    # "pole": 5,
    # "traffic light": 6,
    # "traffic sign": 7,
    # "vegetation": 8,
    # "terrain": 9,
    # "sky": 10,
    "person": 1,
    "rider": 2,
    "car": 3,
    "truck": 4,
    "bus": 5,
    "train": 6,
    "motorcycle": 7,
    "bicycle": 8
}
input_folder = '/root/autodl-tmp/yolo/png2labelme'
output_folder = '/root/autodl-tmp/yolo/labelme2png'

labelme_folder_to_masks(input_folder, class_mapping, output_folder)

