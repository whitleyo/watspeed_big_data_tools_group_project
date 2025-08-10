from pymongo import MongoClient
from datetime import datetime, timedelta
import json
from bson import json_util
import requests
from warnings import warn
import logging

logger = logging.getLogger(__name__)

class DataBaseService:
    def __init__(self, s3, s3_bucket, s3_prefix, mongo_uri="mongodb://localhost:27017", db_name="biorxiv"):
        logger.info(f"Initializing DataBaseService with S3 bucket '{s3_bucket}' and prefix '{s3_prefix}'")
        self.s3 = s3
        self.s3_bucket = s3_bucket
        self.s3_prefix = s3_prefix
        self.mongo_uri = mongo_uri
        self.db_name = db_name
        logger.info(f"Connecting to MongoDB at {mongo_uri} and database '{db_name}'")
        self.db = MongoClient(self.mongo_uri)[self.db_name]

    async def setup(self):
        """
        Explicitly initializes the MongoDB database from S3 and sets up indexes.
        Should be called only by the background worker or setup script.
        """
        logger.info(f"Setting up MongoDB database '{self.db_name}' from S3 bucket '{self.s3_bucket}'")
        await self.initialize_mongodb_from_s3()
        logger.info(f"Creating indexes for database '{self.db_name}'")
        self.sort_db_by_date()
        logger.info(f"Database '{self.db_name}' setup complete with indexes created.")

    async def initialize_mongodb_from_s3(self):
        """
        Loads JSON documents from S3 and inserts them into MongoDB.
        Skips documents that already exist based on DOI.
        """
        collection = self.db.abstracts
        objects = self.s3.list_objects_v2(Bucket=self.s3_bucket, Prefix=self.s3_prefix).get("Contents", [])
        if not objects:
            logger.info(f"No objects found in S3 bucket '{self.s3_bucket}' with prefix '{self.s3_prefix}'.")
            return

        total_inserted = 0
        logger.info(f"Found {len(objects)} objects in S3 bucket '{self.s3_bucket}' with prefix '{self.s3_prefix}'.")
        # Iterate through each object in the S3 bucket
        # and load JSON documents into MongoDB
        logger.info("Loading JSON documents from S3 into MongoDB.")
        for obj in objects:
            key = obj["Key"]
            if key.endswith(".json"):
                response = self.s3.get_object(Bucket=self.s3_bucket, Key=key)
                content = response["Body"].read().decode("utf-8")
                data = json.loads(content)
                documents = data if isinstance(data, list) else [data]

                new_docs = []
                for doc in documents:
                    doi = doc.get("doi")
                    if doi and not collection.find_one({"doi": doi}):
                        new_docs.append(doc)

                # Insert new documents into MongoDB
                logger.info(f"Inserting {len(new_docs)} new documents from {key} into MongoDB.")
                if new_docs:
                    collection.insert_many(new_docs)
                    total_inserted += len(new_docs)

        logger.info(f"MongoDB '{self.db_name}' initialized with {total_inserted} new documents from S3.")

    def sort_db_by_date(self):
        """        
        Creates indexes on the abstracts collection for efficient querying.
        """
        self.db.abstracts.create_index([("date", 1)])
        self.db.abstracts.create_index("doi", unique=True)


    async def get_max_index_in_db(self):
        """
        Retrieves the maximum index from the abstracts collection.
        Returns:
            int: The maximum index found in the database, or None if no documents exist.
        """
        doc = self.db.abstracts.find_one(sort=[("index", -1)])
        return doc["index"] if doc else None

    async def get_latest_date_in_db(self, beginning_date=datetime(2025, 8, 1).date()):
        """
        Retrieves the latest date from the abstracts collection.
        If the collection is empty, returns the specified beginning_date.
        Args:
            beginning_date (datetime.date): The date to return if the collection is empty.
        Returns:
            datetime: The latest date found in the database, or None if no documents exist.
        """
        if self.db.abstracts.count_documents({}) == 0:
            return beginning_date
        try:
            doc = self.db.abstracts.find_one(sort=[("date", -1)])
            return datetime.strptime(doc["date"], "%Y-%m-%d").date()
        except Exception as e:
            assert False, f"Error retrieving latest date from DB: {e}"

    async def ingest(self, start_date, end_date):
        """
        Ingests abstracts from the biorxiv API into MongoDB and stores them in S3.
        Skips documents that already exist in the DB based on DOI.
        """
        current = start_date
        logger.info(f"Starting ingestion from {start_date} to {end_date}.")
        while current <= end_date:
            date_str = current.strftime("%Y-%m-%d")
            page = 0
            max_pages = 20
            new_abstracts = []

            while page < max_pages:
                url = f"https://api.biorxiv.org/details/biorxiv/{date_str}/{date_str}/{page}"
                logger.info(f"Fetching abstracts from {url})")
                response = requests.get(url)
                data = response.json()
                abstracts = data.get("collection", [])

                if not abstracts:
                    break

                for abstract in abstracts:
                    doi = abstract.get("doi")
                    if doi and not self.db.abstracts.find_one({"doi": doi}):
                        self.db.abstracts.insert_one(abstract)
                        new_abstracts.append(abstract)

                # Save only new abstracts to S3
                if new_abstracts:
                    s3_key = f"{self.s3_prefix}/{date_str}/page_{page}.json"
                    self.s3.put_object(
                        Bucket=self.s3_bucket,
                        Key=s3_key,
                        Body=json_util.dumps(new_abstracts),
                        ContentType="application/json"
                    )

                if len(abstracts) < 100:
                    break

                page += 1
                if page >= max_pages:
                    warn(f"Reached max page limit ({max_pages}) for {date_str}. Stopping ingestion.")
                    break

            current += timedelta(days=1)

    async def retrieve_by_doi(self, doi):
        return self.db.abstracts.find_one({"doi": doi})

    async def retrieve_by_index(self, index):
        return self.db.abstracts.find_one({"index": index})
