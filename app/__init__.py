from quart import Quart
import asyncio
import os

from .utils.cleanup import cleanup_old_reports  # 🔁 Import cleanup utility

def create_app():
    app = Quart(__name__, template_folder="templates")
    app.config.setdefault("PROVIDE_AUTOMATIC_OPTIONS", True)
    app.BASE_DIR = os.path.abspath(os.path.dirname(__file__))

    @app.before_serving
    async def start_background_tasks():
        async def periodic_cleanup():
            while True:
                await cleanup_old_reports(app.BASE_DIR)
                await asyncio.sleep(3600)
        asyncio.create_task(periodic_cleanup())

    # Register routes
    from .routes import abstract_query, literature_summary, index
    app.register_blueprint(abstract_query.bp)
    app.register_blueprint(literature_summary.bp)
    app.register_blueprint(index.bp)

    return app