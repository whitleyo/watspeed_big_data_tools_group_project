from quart import Blueprint, send_file, current_app
import os

bp = Blueprint("literature_summary", __name__)

@bp.route("/literature-summary", methods=["GET"])
async def serve_literature_summary():
    # report_path = "reports/literature_summary.html"
    # change to actual report path when implemented
    report_path = os.path.join(current_app.BASE_DIR, "notebooks/template1.html")  # Adjust this to your actual report path
    
    try:
        return await send_file(report_path, mimetype="text/html")
    except FileNotFoundError:
        return {"error": "Literature summary not available"}, 404

# TODO: Implement the actual logic to generate the literature summary report
# This can be done either through a background task or on-demand when the route is accessed.
# For now, this route serves a static HTML file as a placeholder.