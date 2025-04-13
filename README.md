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

This service runs on port 5000 by default.  
On MacOS, change the port or try disabling the 'AirPlay Receiver' service from System Preferences -> General -> AirDrop & Handoff as it already uses port 5000.

### MCP Server

The MCP server provides a standardized interface for AI agents:

```bash
python mcp_server.py
```

This service runs on port 6000 by default. You can specify a different port:
```bash
python mcp_server.py 7000
```

## Usage

### Direct API Access

Generate an image by sending a POST request to the image generation server:

```bash
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "A futuristic cityscape at sunset"}'
```

The response will be the generated image (binary data).

### MCP Interface for AI Agents

AI agents can interact with the service using the MCP protocol:

```bash
curl -X POST http://localhost:6000/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "action": "generate_image",
    "parameters": {
      "prompt": "A futuristic cityscape at sunset"
    }
  }'
```

The response will include the image as a base64-encoded string:

```json
{
  "status": "success",
  "result": {
    "image_data": "base64-encoded-image-data",
    "mime_type": "image/png",
    "prompt": "A futuristic cityscape at sunset"
  }
}
```

### MCP Schema

You can get the schema of available tools:

```bash
curl http://localhost:6000/mcp/schema
```

## Service Architecture

1. **Image Generation Server** (generate_image.py)
   - Handles the actual image generation using Stable Diffusion
   - Provides a simple HTTP API for image generation
   - Runs on port 5000

2. **MCP Server** (mcp_server.py)
   - Provides a standardized MCP interface for AI agents
   - Forwards requests to the Image Generation Server
   - Converts binary image responses to base64 for JSON compatibility
   - Runs on port 6000

## Stopping the Services

If running in daemon mode, stop the image generation server:
```bash
kill $(cat server.pid)
```

For services running in foreground mode, use Ctrl+C. 