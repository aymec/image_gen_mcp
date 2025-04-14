# AI Image Generation Server with MCP Interface

This project provides an HTTP server for image generation using Stable Diffusion, along with a Model Context Protocol (MCP) server that enables AI agents to request image generation.

## Setup

1. Create a virtual environment:
   ```bash
   virtualenv myvirtualenv
   ```

2. Activate the virtual environment:
   ```bash
   source myvirtualenv/bin/activate
   ```

3. Install required packages using requirements.txt:
   ```bash
   pip install -r requirements.txt
   ```

4. Install the MCP package (for Goose integration):
   ```bash
   pip install 'mcp[cli]>=1.6.0'  # Note: quotes are required to escape the brackets
   pip install -e .
   ```

## Running the Services

### Image Generation Server

The base service that actually generates the images:

**Foreground mode:**
```bash
python generate_image.py
```

**Daemon mode:**
```bash
python generate_image.py --daemon
```

**Custom port:**
```bash
python generate_image.py --port 5001
```

This service runs on port 5000 by default.  
On MacOS, change the port or try disabling the 'AirPlay Receiver' service from System Preferences -> General -> AirDrop & Handoff as it already uses port 5000.

### MCP Server

The MCP server provides a standardized interface for AI agents using the Model Context Protocol (MCP):

**Recommended method for testing and development:**
```bash
source .venv/bin/activate  # Activate your virtualenv
mcp dev src/image_gen_mcp/server.py
```
This starts the MCP server with the FastMCP Inspector for easier debugging and testing.

**Running the FastMCP server directly (production):**
```bash
source .venv/bin/activate  # Activate your virtualenv
image-gen-mcp
```

## Usage

### Direct API Access

Generate an image by sending a POST request to the image generation server:

```bash
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "A futuristic cityscape at sunset"}'
```

The response will include the URL to access the generated image along with metadata:

```json
{
  "filename": "123e4567-e89b-12d3-a456-426614174000.png",
  "filepath": "generated_images/123e4567-e89b-12d3-a456-426614174000.png",
  "image_url": "http://localhost:5000/images/123e4567-e89b-12d3-a456-426614174000.png",
  "content_type": "image/png",
  "width": 512,
  "height": 512,
  "prompt": "A futuristic cityscape at sunset"
}
```

You can access the generated image directly via the returned `image_url`.

### MCP Interface for AI Agents

AI agents can interact with the service using the MCP protocol. The recommended way to test the MCP server is using the FastMCP Inspector:

**Running the MCP Inspector:**
```bash
source .venv/bin/activate  # Activate your virtualenv
mcp dev src/image_gen_mcp/server.py
```

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

The MCP response will include a structured image object with URL and metadata:

```json
{
  "status": "success",
  "result": {
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
}
```

This format is compatible with MCP tools like Goose, which can display the image through the provided URL rather than embedding it directly in the conversation context.

## File Organization

- `generate_image.py` - The main image generation server using Stable Diffusion
- `src/image_gen_mcp/` - Package directory containing the fastMCP implementation
  - `server.py` - The fastMCP server implementation
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

Once integrated, you can use the image generation tool in Goose by asking it to generate an image with a specific prompt.

## Service Architecture

1. **Image Generation Server** (generate_image.py)
   - Handles the actual image generation using Stable Diffusion
   - Provides a simple HTTP API for image generation
   - Returns image URL, dimensions, and metadata
   - Includes a direct endpoint to serve the generated images
   - Runs on port 5000

2. **MCP Server** (image-gen-mcp package)
   - Provides a standardized MCP interface for AI agents
   - Forwards requests to the Image Generation Server
   - Returns a properly formatted MCP image object with URL and metadata
   - Can be run in two modes:
     - Direct mode (via `image-gen-mcp` command)
     - Development mode with FastMCP Inspector (via `mcp dev` command)
   - Development mode provides a web interface at http://127.0.0.1:6274

## Stopping the Services

If running in daemon mode, stop the image generation server:
```bash
kill $(cat logs/server.pid)
```

For services running in foreground mode, use Ctrl+C. 