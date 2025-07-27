from quart import Blueprint, request, render_template
import asyncio
import subprocess
import tempfile
import os

bp = Blueprint("abstract_query", __name__)

@bp.route("/abstract-query-frontend-form", methods=["GET"])
async def abstract_query_frontend_form():
    # Serve the HTML form for the abstract query
    return await render_template("templates/abstract_report_generator.html", mimetype="text/html")

@bp.route("/abstract-query", methods=["POST"])
async def abstract_query():
    data = await request.get_json()
    query_text = data.get("query", "")
    top_n = data.get("top_n", 5)  # Default to 5 if not provided
    if not query_text:
        return {"error": "Query text is required"}, 400
    with tempfile.TemporaryDirectory() as tmp_dir:
        temp_ipynb = os.path.join(tmp_dir, "output.ipynb")
        output_html = os.path.join(tmp_dir, "report.html")

        # Run Papermill and nbconvert synchronously (wrapped in thread executor)
        # NOTE: change "../notebooks/template_query.ipynb" to your actual notebook path
        # Ensure that the notebook is in the correct path relative to this script
        await asyncio.to_thread(subprocess.run, [
            "papermill", "../notebooks/template_query.ipynb", temp_ipynb,
            "-p", "query", query_text,
            "-p", "top_n", int(top_n)
        ])

        await asyncio.to_thread(subprocess.run, [
            "jupyter", "nbconvert", "--to", "html", temp_ipynb,
            "--output", output_html
        ])

        return await render_template(output_html, mimetype="text/html")
