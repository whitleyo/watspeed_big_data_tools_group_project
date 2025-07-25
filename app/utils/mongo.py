from motor.motor_asyncio import AsyncIOMotorClient
from app.config import DOCUMENTDB_URI, DOCUMENTDB_CA_FILE

client = AsyncIOMotorClient(
    DOCUMENTDB_URI,
    tls=True,
    tlsCAFile=DOCUMENTDB_CA_FILE,
    serverSelectionTimeoutMS=5000
)

db = client["literature_db"]
collection = db["abstracts"]
