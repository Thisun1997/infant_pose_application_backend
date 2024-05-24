from pymongo import ReturnDocument

from config import Config


def get_next_sequence(name):
    result = Config.counters_collection.find_one_and_update(
        {'_id': name},
        {'$inc': {'seq': 1}},
        return_document=ReturnDocument.AFTER,
        upsert=True
    )
    return result['seq']