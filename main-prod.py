"""
Production entry point for the PPG analysis tool.
Optimized for Docker deployment on Render.com or GCP.
"""

import os
from src.app import create_app

# Create the app instance
app = create_app()

if __name__ == "__main__":
    # Get port from environment variable (for cloud platforms)
    port = int(os.environ.get("PORT", 8080))
    
    # Get debug mode from environment variable
    debug = os.environ.get("DEBUG", "false").lower() == "true"
    
    # Run the app using the stable Dash API
    app.run_server(
        host="0.0.0.0",  # Bind to all interfaces for Docker
        port=port,
        debug=debug,
        dev_tools_hot_reload=False,  # Disable hot reload in production
        dev_tools_ui=False,  # Disable debug UI in production
    )
