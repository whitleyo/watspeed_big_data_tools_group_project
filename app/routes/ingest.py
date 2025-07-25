from quart import Blueprint, request
from app.utils import s3_loader, mongo

bp = Blueprint("ingest", __name__)

@bp.route("/ingest", methods=["POST"])
async def ingest_data():
    body = await request.get_json()
    key = body["key"]
    data = await s3_loader.load_json_from_s3(key)
    await mongo.collection.insert_many(data)
    return {"status": "Ingested", "count": len(data)}
