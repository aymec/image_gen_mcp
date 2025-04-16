import argparse
import os
import sys
import time
from .server import mcp
from .generator import start_image_generator

def main():
    """Image Generator MCP: Generate images using Stable Diffusion."""
    # Check if the required environment variable is set
    image_gen_dir = os.environ.get("IMAGE_GEN_DIR")
    if not image_gen_dir:
        print("ERROR: Environment variable IMAGE_GEN_DIR is not set.", file=sys.stderr)
        print("Please set IMAGE_GEN_DIR to the directory where generated images should be stored.", file=sys.stderr)
        print("Example: export IMAGE_GEN_DIR=/path/to/generated_images", file=sys.stderr)
        sys.exit(1)
    
    # Create the directory if it doesn't exist
    try:
        os.makedirs(image_gen_dir, exist_ok=True)
        print(f"Using image directory: {image_gen_dir}")
    except Exception as e:
        print(f"ERROR: Failed to create image directory {image_gen_dir}: {str(e)}", file=sys.stderr)
        sys.exit(1)
    
    parser = argparse.ArgumentParser(
        description="Provides image generation capabilities using Stable Diffusion via MCP."
    )
    
    parser.add_argument("--port", type=int, default=5000,
                      help="Port for the image generation service (default: 5000)")
    
    args = parser.parse_args()
    
    print("Starting image generation service...")
    image_generator_thread = start_image_generator(port=args.port)
    
    # Give a small delay to ensure the Flask app is running
    time.sleep(1)
    
    print("Starting MCP server")
    try:
        mcp.run()
    except KeyboardInterrupt:
        print("Shutting down...")

if __name__ == "__main__":
    main()
