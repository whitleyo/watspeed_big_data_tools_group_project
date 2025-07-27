from quart import Quart
import os

def create_app():
    app = Quart(
        __name__, 
        template_folder="templates" # Base path for render_template (renders html)
        )
    app.config.setdefault("PROVIDE_AUTOMATIC_OPTIONS", True)
    # Set base directory
    app.BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    # Import routes
    from .routes import abstract_query, literature_summary, index
    app.register_blueprint(abstract_query.bp)
    app.register_blueprint(literature_summary.bp)
    app.register_blueprint(index.bp)

    return app
