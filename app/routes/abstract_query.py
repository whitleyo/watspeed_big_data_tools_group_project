from quart import Blueprint, request, send_file, render_template
import asyncio
import subprocess
import tempfile
from datetime import datetime
from quart import current_app
import os
import uuid

bp = Blueprint("abstract_query", __name__)

@bp.route("/abstract-query-frontend-form", methods=["GET"])
async def abstract_query_frontend_form():
    # Serve the HTML form for the abstract query
    return await render_template("abstract_report_generator.html", mimetype="text/html")

@bp.route("/abstract-query", methods=["POST"])
async def abstract_query():
    data = await request.get_json()
    query_text = data.get("query", "")
    top_n = data.get("top_n", 5)  # Default to 5 if not provided
    if not query_text:
        return {"error": "Query text is required"}, 400
    # add a unique identifier to the report
    report_id = str(uuid.uuid4())
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_dir = os.path.join(current_app.BASE_DIR, "reports")
    report_prefix = f"abstract_query_report_{report_id}_{timestamp}"
    temp_ipynb = os.path.join(report_dir, f"{report_prefix}.ipynb")
    output_html = os.path.join(report_dir, f"{report_prefix}.html")
    # Run Papermill and nbconvert synchronously (wrapped in thread executor)
    # NOTE: change "../notebooks/template_query.ipynb" to your actual notebook path
    # Ensure that the notebook is in the correct path relative to this script
    ipynb_template_path = os.path.join(current_app.BASE_DIR, "notebooks", "template2.ipynb")
    try:
        result = await asyncio.to_thread(subprocess.run, [
            "papermill", ipynb_template_path, temp_ipynb,
            "-p", "query", query_text,
            "-p", "top_n", str(top_n)
        ], capture_output=True, text=True, check=True)
        del result
    except subprocess.CalledProcessError as e:
        print("Papermill call failed:")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return {"error": "Papermill execution failed", "details": e.stderr}, 500
    try:
        result = await asyncio.to_thread(subprocess.run, [
            "jupyter", "nbconvert", "--to", "html", temp_ipynb,
            "--output", report_prefix
        ])
        del result
    except subprocess.CalledProcessError as e:
        print("Nbconvert call failed:")
        print("STDOUT:", e.stdout)
        print("STDERR:", e.stderr)
        return {"error": "Nbconvert execution failed", "details": e.stderr}, 500
    # Ensure the output HTML file exists
    if not os.path.exists(output_html):
        return {"error": "Output HTML file not found"}, 500
    # Clean up the temporary notebook file
    os.remove(temp_ipynb)
    # Serve the generated HTML report
    return await send_file(output_html, mimetype="text/html")
