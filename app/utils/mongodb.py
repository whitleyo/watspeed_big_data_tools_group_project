from pymongo import MongoClient



def sort_db_by_date(db):
    """
    Sorts the abstracts collection in the MongoDB database by date.
    :param db: MongoDB database instance
    """
    db.abstracts.create_index([("date", 1)])

def get_latest_date_in_db(db):
    """
    Retrieves the latest date from the abstracts collection in the specified MongoDB database.
    :param db: MongoDB database instance
    :return: Latest date as a datetime object or None if no documents are found
    """
    latest = db.abstracts.find_one(sort=[("date", -1)])
    return datetime.strptime(latest["date"], "%Y-%m-%d") if latest else None