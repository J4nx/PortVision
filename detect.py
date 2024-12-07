from ultralytics import YOLO
import torch
from PIL import Image
from bounding_boxes import draw_bboxes


# Define the prediction function
def predict(image):
    # Set up device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Device: {device}")

    # Load the YOLO model
    model = YOLO(r'runs\train\port_vision34\weights\best.pt').to(device)

    # Convert Gradio numpy image to PIL Image
    image = Image.fromarray(image)

    # Perform inference
    results = model(image, iou=0.4, conf=0.4)  # Adjust thresholds as needed
    
    # Draw custom bounding boxes and return the image
    result_img, json_output = draw_bboxes(image, results, box_thickness=2, font_scale=0.6, alpha=0.6)

    return result_img, json_output
