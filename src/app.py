"""
Main Dash application for the PPG analysis tool.
"""

from dash import Dash, html

from .callbacks import register_data_callbacks, register_plot_callbacks, register_window_callbacks
from .components import APP_INDEX_STRING, create_layout


def create_app():
    """Create and configure the Dash application."""
    app = Dash(__name__)
    app.title = "PPG Filter Lab — Window Mode (Wide)"
    app.index_string = APP_INDEX_STRING

    # Set up the layout
    app.layout = create_layout()

    # Register all callbacks
    register_data_callbacks(app)
    register_window_callbacks(app)
    register_plot_callbacks(app)

    # Add health check endpoint
    @app.server.route("/health")
    def health_check():
        """Health check endpoint for Docker and load balancers."""
        return {"status": "healthy", "service": "ppg-analysis-tool"}, 200

    return app


# Create the app instance
app = create_app()
