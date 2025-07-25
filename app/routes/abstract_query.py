from quart import Quart, request, send_file
import asyncio
import subprocess
import tempfile
import os

app = Quart(__name__)

@app.route("/abstract_query", methods=["POST"])
async def abstract_query():
    data = await request.get_json()
    query_text = data.get("query", "")
    top_n = data.get("top_n", 5)  # Default to 5 if not provided

    with tempfile.TemporaryDirectory() as tmp_dir:
        temp_ipynb = os.path.join(tmp_dir, "output.ipynb")
        output_html = os.path.join(tmp_dir, "report.html")

        # Run Papermill and nbconvert synchronously (wrapped in thread executor)
        # NOTE: change "notebooks/template.ipynb" to your actual notebook path
        # Ensure that the notebook is in the correct path relative to this script
        await asyncio.to_thread(subprocess.run, [
            "papermill", "notebooks/template.ipynb", temp_ipynb,
            "-p", "query", query_text,
            "-p", "top_n", int(top_n)
        ])

        await asyncio.to_thread(subprocess.run, [
            "jupyter", "nbconvert", "--to", "html", temp_ipynb,
            "--output", output_html
        ])

        return await send_file(output_html, mimetype="text/html")
