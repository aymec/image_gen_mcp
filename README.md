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

The MCP server provides a standardized interface for AI agents:

#### Legacy Flask MCP Server

A Flask-based MCP server is provided for backward compatibility:

```bash
python flask_mcp_server.py
```

This service runs on port 6000 by default. You can specify a different port:
```bash
python flask_mcp_server.py 7000
```

#### FastMCP Server (for Goose Integration)

This project now includes a fastMCP implementation for integration with Goose:

**Running the packaged fastMCP server:**
```bash
image-gen-mcp --port 6000
```

**Using the legacy entry point (points to the packaged version):**
```bash
python mcp_server.py 7000
```

**Using MCP development server for testing:**
```bash
mcp dev src/image_gen_mcp/server.py
```

## Usage

### Direct API Access

Generate an image by sending a POST request to the image generation server:

```bash
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "A futuristic cityscape at sunset"}'
```

The response will include the filename and filepath:

```json
{
  "filename": "123e4567-e89b-12d3-a456-426614174000.png",
  "filepath": "generated_images/123e4567-e89b-12d3-a456-426614174000.png"
}
```

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

The response will include the filename and filepath:

```json
{
  "status": "success",
  "result": {
    "filename": "123e4567-e89b-12d3-a456-426614174000.png",
    "filepath": "generated_images/123e4567-e89b-12d3-a456-426614174000.png"
  }
}
```

### MCP Schema

You can get the schema of available tools:

```bash
curl http://localhost:6000/mcp/schema
```

## File Organization

- `generate_image.py` - The main image generation server using Stable Diffusion
- `flask_mcp_server.py` - Legacy Flask-based MCP server implementation
- `mcp_server.py` - Entry point script that uses the packaged fastMCP implementation
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
   - Returns filename and filepath information
   - Runs on port 5000

2. **MCP Server** (mcp_server.py / image-gen-mcp package)
   - Provides a standardized MCP interface for AI agents
   - Forwards requests to the Image Generation Server
   - Passes through the filename and filepath information
   - Runs on port 6000

## Stopping the Services

If running in daemon mode, stop the image generation server:
```bash
kill $(cat logs/server.pid)
```

For services running in foreground mode, use Ctrl+C. 