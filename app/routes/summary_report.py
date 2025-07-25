from quart import Blueprint, send_file
import os

bp = Blueprint("weekly_summary", __name__)

@bp.route("/literature-summary", methods=["GET"])
async def serve_weekly_summary():
    report_path = "compiled/literature_summary.html"
    
    if os.path.exists(report_path):
        return await send_file(report_path, mimetype="text/html")
    return {"error": "Literature summary not available"}, 404