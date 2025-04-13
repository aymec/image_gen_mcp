from diffusers import StableDiffusionPipeline
import torch
from flask import Flask, request, jsonify, send_file
import uuid
import os
import threading
import time
import signal
import sys
import io

app = Flask(__name__)

# Create a directory for storing generated images if it doesn't exist
IMAGES_DIR = "generated_images"
os.makedirs(IMAGES_DIR, exist_ok=True)

# Server configuration
SERVER_PORT = 5000

# Initialize model globally
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
    print("Model loaded and ready")

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
        image = pipe(prompt).images[0]
        
        # Save the image
        image.save(filepath)
        
        # Return the image file path and prompt
        return jsonify({
            "filename": filename,
            "filepath": filepath
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def run_server():
    # Initialize the model
    initialize_model()
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=SERVER_PORT)

def daemonize():
    # Fork the first time
    try:
        if os.fork() > 0:
            sys.exit(0)  # Parent exits
    except OSError as e:
        print(f"Fork #1 failed: {e}")
        sys.exit(1)
    
    # Decouple from parent environment
    os.chdir(os.path.dirname(os.path.abspath(__file__)))  # Change to script directory instead of root
    os.setsid()
    os.umask(0)
    
    # Fork the second time
    try:
        if os.fork() > 0:
            sys.exit(0)  # Parent exits
        print("Server successfully daemonized")
    except OSError as e:
        print(f"Fork #2 failed: {e}")
        sys.exit(1)
    
    # Create logs directory if it doesn't exist
    LOGS_DIR = "logs"
    os.makedirs(LOGS_DIR, exist_ok=True)
    
    # Redirect standard file descriptors
    with open('/dev/null', 'r') as f:
        os.dup2(f.fileno(), sys.stdin.fileno())
    with open(os.path.join(LOGS_DIR, 'server.log'), 'a') as f:
        os.dup2(f.fileno(), sys.stdout.fileno())
        os.dup2(f.fileno(), sys.stderr.fileno())
    
    # Write PID file
    with open(os.path.join(LOGS_DIR, 'server.pid'), 'w') as f:
        f.write(str(os.getpid()))
    
    # Run the server
    run_server()

if __name__ == "__main__":
    # Check for custom port in command line arguments
    for i, arg in enumerate(sys.argv):
        if arg == "--port" and i + 1 < len(sys.argv):
            try:
                SERVER_PORT = int(sys.argv[i + 1])
                print(f"Using custom port: {SERVER_PORT}")
            except ValueError:
                print(f"Invalid port number: {sys.argv[i + 1]}, using default port {SERVER_PORT}")
    
    if len(sys.argv) > 1 and sys.argv[1] == "--daemon":
        print("Starting server as daemon...")
        daemonize()
    else:
        print("Starting server in foreground...")
        run_server()
