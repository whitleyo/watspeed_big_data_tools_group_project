from quart import Blueprint, send_file, current_app
import os

bp = Blueprint("literature_summary", __name__)

@bp.route("/literature-summary", methods=["GET"])
async def serve_literature_summary():
    # report_path = "reports/literature_summary.html"
    report_path = os.path.join(current_app.BASE_DIR, "reports/template1.html")  # Adjust this to your actual report path
    
    try:
        return await send_file(report_path, mimetype="text/html")
    except FileNotFoundError:
        return {"error": "Literature summary not available"}, 404