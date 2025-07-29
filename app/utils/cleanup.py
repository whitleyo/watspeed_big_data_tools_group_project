import os
import time
import logging

REPORT_TTL = 86400  # 1 day in seconds

async def cleanup_old_reports(base_dir):
    reports_dir = os.path.join(base_dir, "reports")
    now = time.time()
    for filename in os.listdir(reports_dir):
        filepath = os.path.join(reports_dir, filename)
        try:
            if os.path.isfile(filepath) and now - os.path.getmtime(filepath) > REPORT_TTL:
                os.remove(filepath)
                logging.info(f"Deleted old report: {filename}")
        except Exception as e:
            logging.warning(f"Failed to delete {filename}: {e}")