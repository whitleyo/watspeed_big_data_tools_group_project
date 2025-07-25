from quart import Quart

def create_app():
    app = Quart(__name__)
    
    # Import routes
    from .routes import ingest, abstract_query, summary_report
    app.register_blueprint(ingest.bp)
    app.register_blueprint(abstract_query.bp)
    app.register_blueprint(summary_report.bp)

    return app
