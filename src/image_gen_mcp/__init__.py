import argparse
from .server import mcp

def main():
    """Image Generator MCP: Generate images using Stable Diffusion."""
    parser = argparse.ArgumentParser(
        description="Provides image generation capabilities using Stable Diffusion via MCP."
    )
    # parser.add_argument(
    #     "--port", 
    #     type=int, 
    #     default=6000,
    #     help="Port to run the MCP server on (default: 6000)"
    # )
    args = parser.parse_args()
    
    # Set port in environment if specified
    # if args.port != 6000:
    #     import os
    #     os.environ["PORT"] = str(args.port)
    
    # Run the MCP server
    # print(f"Starting MCP server on port {args.port}")
    print(f"Starting MCP server")
    mcp.run()

if __name__ == "__main__":
    main()
