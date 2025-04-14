import argparse
from .server import mcp

def main():
    """Image Generator MCP: Generate images using Stable Diffusion."""
    parser = argparse.ArgumentParser(
        description="Provides image generation capabilities using Stable Diffusion via MCP."
    )
    args = parser.parse_args()
    
    print("Starting MCP server")
    mcp.run()

if __name__ == "__main__":
    main()
