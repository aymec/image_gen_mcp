# AI Image Generation Server with MCP Interface

This project provides a Model Context Protocol (MCP) server with integrated Stable Diffusion image generation capabilities, enabling AI agents to request and receive generated images.

## Setup

1. Create a virtual environment, use `.venv` mandatorily:
   ```bash
   virtualenv .venv
   ```

2. Activate the virtual environment:
   ```bash
   source .venv/bin/activate
   ```

3. Install the MCP package (for Goose integration):
   ```bash
   pip install -e .
   ```

## Running the Service

The MCP server includes the integrated image generation service. You can start both with a single command:

**Standard mode:**
```bash
source .venv/bin/activate  # Activate your virtualenv
export IMAGE_GEN_DIR=/absolute/path/to/folder # Set generated images target folder
image-gen-mcp
```

**Development mode with FastMCP Inspector:**
Open two terminals:  

Terminal 1
```bash
source .venv/bin/activate  # Activate your virtualenv
export IMAGE_GEN_DIR=/absolute/path/to/folder # Set generated images target folder
image-gen-mcp # Start image generation service (and a MCP server we won't use)
```

Terminal 2
```bash
source .venv/bin/activate  # Activate your virtualenv
export IMAGE_GEN_DIR=/absolute/path/to/folder # Set generated images target folder
mcp dev src/image_gen_mcp/server.py # Start MCP server with Inspector
```

Note: Only when using development mode, the image generation service must be started separately.

This will start the MCP server with the FastMCP Inspector, which provides:
1. A web interface at http://127.0.0.1:6274 for testing and debugging
2. A proxy server on port 6277 for forwarding MCP requests

**Using the FastMCP Inspector:**
1. Open http://127.0.0.1:6274 in your browser
2. Use the interactive interface to:
   - Explore available tools and their documentation
   - Test the `generate_image` tool with your own prompts
   - View request/response history
   - Debug any issues with the MCP server

**Custom port for image generation service:**
```bash
source .venv/bin/activate  # Activate your virtualenv
export IMAGE_GEN_DIR=/absolute/path/to/folder # Set generated images target folder
image-gen-mcp --port 5001
```

## Direct API Access

Generate an image by sending a POST request to the image generation service:

```bash
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "A futuristic cityscape at sunset"}'
```

The response will include the URL to access the generated image along with metadata:

```json
{
  "type": "image",
  "format": "png",
  "url": "http://localhost:5000/images/123e4567-e89b-12d3-a456-426614174000.png",
  "width": 512,
  "height": 512,
  "filename": "123e4567-e89b-12d3-a456-426614174000.png",
  "filepath": "generated_images/123e4567-e89b-12d3-a456-426614174000.png",
  "mime_type": "image/png",
  "prompt": "A futuristic cityscape at sunset",
  "alt_text": "AI-generated image of: A futuristic cityscape at sunset"
}
```

You can access the generated image directly via the returned `image_url`.

## File Organization

- `src/image_gen_mcp/` - Package directory containing the implementation
  - `server.py` - The MCP server implementation
  - `generator.py` - The image generation service
  - `__init__.py` - Package initialization and CLI entry point
  - `__main__.py` - Enables running the package as a module

## Integration with Goose

To add this MCP server as an extension in Goose:

1. Go to `Settings > Extensions > Add`.
2. Set the `Type` to `StandardIO`.
3. Provide ID "image_generator", name "Image Generator", and an appropriate description.
4. In the `Command` field, provide the absolute path to your executable:  
   ```
   uv run /full/path/to/your/project/.venv/bin/image-gen-mcp
   ```
5. Add an environment variable `IMAGE_GEN_DIR` and pick a folder where generated images will be stored

Once integrated, you can use the image generation tool in Goose by asking it to generate an image with a specific prompt.

## Service Architecture

Both services are integrated into a single application:

1. **Image Generation Service** (src/image_gen_mcp/generator.py)
   - Handles the actual image generation using Stable Diffusion
   - Provides a simple HTTP API for image generation
   - Returns image URL, dimensions, and metadata
   - Includes a direct endpoint to serve the generated images
   - Runs on port 5000 by default (customizable with --port)
   - Runs in a separate thread within the same process as the MCP server

2. **MCP Server** (src/image_gen_mcp/server.py)
   - Provides a standardized MCP interface for AI agents
   - Forwards requests to the integrated Image Generation Service
   - Returns a properly formatted MCP image object with URL and metadata

## Stopping the Service

Use Ctrl+C to stop both services, as they now run within the same process.