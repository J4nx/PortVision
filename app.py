import gradio as gr
from detect import predict

# Create the Gradio interface
iface = gr.Interface(
    fn=predict,
    inputs=gr.Image(type="numpy"),  # Gradio provides a numpy array
    outputs=[gr.Image(type="numpy"), gr.Textbox(label="JSON Output")],  # Output is the image and JSON
    title="PortVision",
    description="Upload an image of a network switch and the model will draw bounding boxes around detected ports, along with the port status in JSON."
)

# Launch the Gradio app
iface.launch(share=True)