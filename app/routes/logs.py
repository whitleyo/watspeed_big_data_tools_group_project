from quart import Blueprint, render_template, current_app, Response
import os
import asyncio

bp = Blueprint("logs", __name__)

@bp.route("/logs", methods=["GET"])
async def get_logs():
    log_file_path = current_app.log_path

    try:
        with open(log_file_path, "r") as f:
            log_content = f.read()
        return Response(
            log_content,
            content_type="text/plain",
            headers={"Cache-Control": "no-cache"}
        )
    except FileNotFoundError:
        return Response("Log file not found.", status=404, content_type="text/plain")