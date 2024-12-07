from ultralytics import YOLO
import torch
import wandb

def train_model(epochs):
    # Load a model
    model = YOLO(r'runs\train\port_vision33\weights\best.pt').to(device)
    # model = YOLO(r'yolo11s.pt').to(device)

    # Train the model
    train_results = model.train(
        batch=16,            # batch size
        data="data.yaml",    # path to dataset YAML
        epochs=epochs,           # number of training epochs
        imgsz=1216,          # WARNING ⚠️ imgsz=[1200] must be multiple of max stride 32, updating to [1216]
        device=device,       # device to run on
        rect=True,           # enable rectangular training
        project='runs/train',  # directory to save training runs
        name='port_vision',            # name of the experiment
        save=True,             # save model after training
        # save_period=1,         # save model every epoch (optional)
        patience=100,           # early stopping patience (epochs)
        # Augmentation Hyperparameters
        # degrees=10.0,          # image rotation (+/- deg)
        # translate=0.1,         # image translation (+/- fraction)
        # scale=0.5,             # image scale (+/- gain)
        # perspective=0.001,       # image perspective (+/- fraction), range 0-0.001
        # hsv_h=0.015,           # image HSV-Hue (+/- fraction), range 0-0.05
        # hsv_s=0.7,             # image HSV-Saturation (+/- fraction), range 0-0.05
        # hsv_v=0.4,             # image HSV-Value (+/- fraction), range 0-0.05
        # mosaic=0.5,            # image mosaic (probability)
        # mixup=0.2,             # image mixup (probability)
        # Regularization
        # cls=1.0,            # class prediction loss weight
        # kobj=1.0,            # object prediction loss weight
        # iou=0.3,             # IoU training threshold
        # Optimizer Hyperparameters
        # optimizer='auto',      # Optimizer type ('SGD' or 'Adam')
        # lr0=0.01,              # initial learning rate (SGD=5E-3, Adam=5E-4)
        # cos_lr=False,          # cosine learning rate
        # momentum=0.937,        # SGD momentum/Adam beta1
        # weight_decay=0.0005,   # optimizer weight decay
    )

    return model, train_results

if __name__ == '__main__':
    # Initialize wandb
    epochs = 300  # Define the epochs variable
    
    wandb.init(project="port_vision", config={
    "epochs": epochs,
    "batch_size": 16,
    "architecture": "YoloV11",
    "dataset": "Port Vision"
    }, resume=False, reinit=True)

    # Device configuration
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Device: {device}")

    config = wandb.config

    model, train_results = train_model(epochs)
    # Evaluate model performance on the validation set
    metrics = model.val()

    # Export the model to ONNX format
    path = model.export(format="onnx")  # return path to exported model



