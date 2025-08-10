from quart import Quart
import asyncio
import os
from datetime import datetime
import logging

from . import config
from .utils.cleanup import cleanup_old_reports  # 🔁 Import cleanup utility

def create_app():
    app = Quart(__name__, template_folder="templates")
    app.config.setdefault("PROVIDE_AUTOMATIC_OPTIONS", True)
    app.BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    @app.before_serving
    async def start_background_tasks():
        async def periodic_cleanup():
            while True:
                logger.info("Running periodic cleanup of old reports.")
                await cleanup_old_reports(app.BASE_DIR)
                await asyncio.sleep(86400) # Sleep for 24 hours
        
        async def nuke_db_if_chosen():
            """
            Wipes the database abstracts collection if the configuration flag is set.
            Does this for both MongoDB and S3.
            This is intended for development or testing purposes only.
            """
            if config.NUKE_DB_ON_STARTUP:
                from .services.database_service import DataBaseService
                from .utils.aws import get_boto3_client

                s3_client = get_boto3_client("s3")
                s3_bucket = config.AWS_BUCKET_NAME
                s3_prefix = config.S3_PREFIX
                mongo_uri = config.MONGO_URI

                db_service = DataBaseService(s3=s3_client, s3_bucket=s3_bucket, s3_prefix=s3_prefix,
                                             mongo_uri=mongo_uri, db_name="biorxiv")
                await db_service.setup()
                await db_service.nuke_db()
                logger.info("Database nuked on startup as per configuration.")

        async def initialize_db():
            from .services.database_service import DataBaseService
            from .utils.aws import get_boto3_client

            s3_client = get_boto3_client("s3")
            s3_bucket = config.AWS_BUCKET_NAME
            s3_prefix = config.S3_PREFIX
            mongo_uri = config.MONGO_URI

            app.db_service = DataBaseService(s3=s3_client, s3_bucket=s3_bucket, s3_prefix=s3_prefix,
                                             mongo_uri=mongo_uri, db_name="biorxiv")
            await app.db_service.setup()

        async def periodic_ingest():
            # Periodically ingest data into the database daily
            while True:
                today = datetime.utcnow().date()
                latest_date = await app.db_service.get_latest_date_in_db()
                await app.db_service.ingest(start_date=latest_date, end_date=today)
                await asyncio.sleep(86400)  # Sleep for 24 hours
        async def startup_sequence():
            await nuke_db_if_chosen()
            await initialize_db()
            asyncio.create_task(periodic_cleanup())
            asyncio.create_task(periodic_ingest())

        # Start background tasks if enabled
        if os.getenv("RUN_BACKGROUND_TASKS") == "true":
            logger.info("Starting background tasks. Assuming this is the lead worker.")
            asyncio.create_task(startup_sequence())

    # Register routes
    from .routes import abstract_query, literature_summary, index
    app.register_blueprint(abstract_query.bp)
    app.register_blueprint(literature_summary.bp)
    app.register_blueprint(index.bp)

    return app