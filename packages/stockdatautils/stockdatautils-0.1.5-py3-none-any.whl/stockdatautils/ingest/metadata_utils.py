from pymongo import MongoClient
from datetime import datetime, timedelta

from stockdatautils.ingest.utils import get_current_date_utc


def add_breakout_event(symbol, collection, status="potential_breakout"):
    current_utc_datetime = get_current_date_utc()
    event = {
        'symbol': symbol,
        'event_date': current_utc_datetime,
        'status': status
    }
    collection.insert_one(event)


def is_recent_potential_breakout(symbol, collection):
    cutoff_date = datetime.now() - timedelta(weeks=12)

    # Query to check for the symbol in the last 3 months
    recent_event = collection.find_one({
        'symbol': symbol,
        'event_date': {'$gte': cutoff_date},
        'status': 'potential_breakout'
    })

    return recent_event is not None
