# PortVision
PortVision automates the analysis and documentation of network switches by leveraging advanced AI models. The application identifies network switches, detects LAN ports, determines whether ports are connected, and organizes the findings into a structured JSON format.

## Problem Description
In modern network management, maintaining accurate documentation of network switches is essential for efficient operation and troubleshooting. Traditional methods involve manual surveys where technicians inspect each switch to determine which ports are in use, identify connected cables, and record switch identification details such as brand, model, ID, and serial number. This process is time-consuming, prone to human error, and often leads to outdated or inaccurate records.
**PortVision** aims to automate this process by utilizing AI to analyze images of network switches.
By addressing the inefficiencies of manual documentation, PortVision provides a faster, more accurate method for collecting and updating network infrastructure data. This solution has significant real-world applications, especially when integrated with broader site survey tools.

## Key Features

- Object Detection: Identifies network switches, LAN port stacks, and ports using a YOLO-based model.
- Connectivity Detection: Classifies ports as connected or empty.
- JSON Output: Generates structured JSON for detected switches and their ports.
- Visualization: Draws bounding boxes around detected objects with color-coded labels for easy analysis.

## Use Cases

- Network inventory management.
- Automated documentation of network infrastructure.
- Real-time port usage analysis for troubleshooting.

## Installation

### Clone the Repository:

```bash
git clone https://github.com/J4nx/PortVision.git
cd PortVision
```

Install Dependencies: Use Python 3.8+ and install the necessary libraries:

```bash
pip install -r requirements.txt
```

Prepare the Environment:

- Ensure that your system has a CUDA-compatible GPU for optimal performance.
- Place your trained YOLO model weights (best.pt) in the appropriate directory (runs/train/port_vision34/weights by default).


## How to Use

### 1. Training the Model
To train or fine-tune the YOLO model:

Edit the data.yaml file to match your dataset structure.
Run the training script:

```bash
python port_vision.py

```
Results will be saved in the runs/train/port_vision directory.

### 2. Use app with gradio interface
Place image in the input of gradio interface gui.
Run the app.py script:

```bash
python app.py
```

Output:
Processed image with bounding boxes.
JSON output detailing the detected objects and their properties.


## Configuration

- Bounding Box Visualization: Customize bounding box thickness, font scale, and transparency in bounding_boxes.py.
- YOLO Parameters: Modify detection thresholds (e.g., iou and conf) in detect.py.
- Dataset Configuration: Adjust data.yaml to match your dataset.

## Troubleshooting

- Model Not Detecting Objects: Ensure the correct weights file is specified in the script and that the training process is complete.
- Slow Performance: Use a GPU with sufficient memory and optimize image sizes.

## Future Enhancements

- Real-time video stream processing.
- Integration with site survey tools.
- Link activity assessment using port indicator lights.



