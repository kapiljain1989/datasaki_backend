#!/usr/bin/env python
"""
Development server script with auto-reload enabled.
This script is meant to be used during development to automatically reload the server
when code changes are detected.
"""
import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Now import the app modules after setting up the path
import uvicorn
from app.utils.logging import logger

def run_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = True):
    """
    Run the FastAPI server with optional auto-reload.
    
    Args:
        host (str): Host to bind the server to
        port (int): Port to bind the server to
        reload (bool): Whether to enable auto-reload
    """
    # Get SSL certificate paths
    certs_dir = Path("certs")
    ssl_certfile = os.getenv("SSL_CERTFILE", certs_dir / "ssl-cert.pem")
    ssl_keyfile = os.getenv("SSL_KEYFILE", certs_dir / "ssl-key.pem")
    
    # Check if certificates exist
    if os.path.exists(ssl_certfile) and os.path.exists(ssl_keyfile):
        logger.info(f"Using existing SSL certificates from {certs_dir}")
    else:
        logger.warning("SSL certificates not found. Generating new ones...")
        from generate_certs import generate_self_signed_cert
        generate_self_signed_cert()
    
    # Run the server with HTTPS
    logger.info(f"Starting server with HTTPS on {host}:{port}")
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        reload_dirs=["app"],
        ssl_certfile=str(ssl_certfile),
        ssl_keyfile=str(ssl_keyfile)
    )

if __name__ == "__main__":
    run_server() 