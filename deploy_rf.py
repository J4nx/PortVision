import roboflow
from my_secrets import ROBOFLOW_API_KEY

# Initialize the Roboflow project with your API key
rf = roboflow.Roboflow(api_key=ROBOFLOW_API_KEY)

# Access your workspace and project
project = rf.workspace().project("port-vision")

# Select the version of the dataset
version = project.version(4)  # Replace 1 with the correct version number

# Upload the custom YOLOv11 weights to Roboflow
version.deploy(
    "yolov11",  # Specify the model type (yolov11 for your case)
    r'runs\train\port_vision5\weights',  # Path to the directory containing the weights
    "best.pt"  # Filename of the weights file (e.g., best.pt)
)
