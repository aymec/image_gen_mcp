import json
import requests
from flask import Flask, request, jsonify
import base64
import io
from PIL import Image

app = Flask(__name__)

# Configuration for the image generation service
IMAGE_GEN_URL = "http://localhost:5000/generate"

@app.route('/mcp', methods=['POST'])
def mcp_handler():
    try:
        # Parse the incoming request
        mcp_request = request.json
        
        if not mcp_request:
            return jsonify({"error": "Invalid MCP request"}), 400
        
        # Extract the 'action' field which should specify the tool to use
        action = mcp_request.get('action')
        
        if action == 'generate_image':
            return handle_generate_image(mcp_request)
        else:
            return jsonify({
                "status": "error",
                "message": f"Unknown action: {action}",
                "schema": {
                    "generate_image": {
                        "description": "Generate an image based on a text prompt",
                        "parameters": {
                            "prompt": "Text description of the image to generate"
                        }
                    }
                }
            }), 400
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

def handle_generate_image(mcp_request):
    # Extract parameters
    parameters = mcp_request.get('parameters', {})
    prompt = parameters.get('prompt')
    
    if not prompt:
        return jsonify({
            "status": "error",
            "message": "Missing required parameter: prompt"
        }), 400
    
    try:
        # Call the image generation service
        response = requests.post(
            IMAGE_GEN_URL,
            json={"prompt": prompt},
            stream=True
        )
        
        if response.status_code != 200:
            return jsonify({
                "status": "error",
                "message": f"Image generation failed: {response.text}"
            }), response.status_code
        
        # Convert the image to base64 for inclusion in the response
        image = Image.open(io.BytesIO(response.content))
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        # Return a successful MCP response with the image data
        return jsonify({
            "status": "success",
            "result": {
                "image_data": img_str,
                "mime_type": "image/png",
                "prompt": prompt
            }
        })
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to generate image: {str(e)}"
        }), 500

@app.route('/mcp/schema', methods=['GET'])
def get_schema():
    # Return the schema of available tools
    return jsonify({
        "schema": {
            "generate_image": {
                "description": "Generate an image based on a text prompt",
                "parameters": {
                    "prompt": "Text description of the image to generate"
                }
            }
        }
    })

if __name__ == "__main__":
    import sys
    
    # Default port for MCP server
    port = 6000
    
    # Check if port is provided as argument
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"Invalid port: {sys.argv[1]}, using default port {port}")
    
    print(f"Starting MCP server on port {port}")
    print(f"Image generation service URL: {IMAGE_GEN_URL}")
    
    # Run the Flask app
    app.run(host='0.0.0.0', port=port) 