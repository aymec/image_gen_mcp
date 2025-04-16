from diffusers import StableDiffusionPipeline
import torch
from flask import Flask, request, jsonify, send_file
import uuid
import os
import threading
from PIL import Image
import sys

# Get the image directory from environment variables
IMAGES_DIR = os.environ.get("IMAGE_GEN_DIR")

# Create Flask app
app = Flask(__name__)

# Server configuration
SERVER_PORT = 5000

# Global variable for the model pipeline
pipe = None

# Initialize model
def initialize_model():
    global pipe
    
    # Check for available hardware acceleration
    if torch.backends.mps.is_available():
        device = "mps"  # Use Apple Silicon GPU
    elif torch.cuda.is_available():
        device = "cuda"  # Use NVIDIA GPU (not applicable for Apple Silicon)
    else:
        device = "cpu"  # Fallback to CPU

    print(f"Using device: {device}")

    # Load the Stable Diffusion model
    model_id = "runwayml/stable-diffusion-v1-5"
    pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
    pipe = pipe.to(device)
    print("Image generation model loaded and ready")

# API endpoint for image generation
@app.route('/generate', methods=['POST'])
def generate_image():
    # Get the prompt from the request
    data = request.get_json()
    
    if not data or 'prompt' not in data:
        return jsonify({"error": "Missing prompt in request"}), 400
    
    prompt = data['prompt']
    
    try:
        # Generate a unique filename
        filename = f"{uuid.uuid4()}.png"
        filepath = os.path.join(IMAGES_DIR, filename)
        
        # Generate the image
        print(f"Generating image for prompt: {prompt}")
        original_image = pipe(prompt).images[0]
        
        # Save the full resolution image to disk
        original_image.save(filepath)
        
        # Get original image dimensions
        width, height = original_image.size
        
        # Create a URL for accessing the image
        image_url = f"http://localhost:{SERVER_PORT}/images/{filename}"
        
        # Return the image information
        return jsonify({
            "filename": filename,
            "filepath": filepath,
            "image_url": image_url,
            "content_type": "image/png",
            "width": width,
            "height": height,
            "prompt": prompt
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Add a route to serve images directly
@app.route('/images/<filename>', methods=['GET'])
def serve_image(filename):
    filepath = os.path.join(IMAGES_DIR, filename)
    if os.path.exists(filepath):
        return send_file(filepath, mimetype='image/png')
    else:
        return jsonify({"error": "Image not found"}), 404

def start_image_generator(port=5000):
    """
    Start the image generation server in a separate thread
    
    Args:
        port: The port number to run the server on
    """
    global SERVER_PORT
    SERVER_PORT = port
    
    # Initialize the model
    initialize_model()
    
    # Start Flask app in a separate thread
    thread = threading.Thread(target=lambda: app.run(host='0.0.0.0', port=SERVER_PORT, threaded=True))
    thread.daemon = True
    thread.start()
    
    print(f"Image generation service started on port {SERVER_PORT}")
    return thread