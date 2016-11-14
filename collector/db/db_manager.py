import logging
import os
from pymongo import MongoClient, DESCENDING
from pymongo.errors import DuplicateKeyError

logger = logging.getLogger(__name__)

MONGODB_URI = os.environ.get('MONGODB_URI')

client = MongoClient(MONGODB_URI)
db = client.get_default_database()


def save_full_sample_data(data):
    db.sampledata.insert_one(data)


def save_new(songdata):
    artist = str(songdata['artist'])
    song = str(songdata['song'])
    logger.info('++ Saving: ' + artist + " - " + song)
    try:
        db_result = db.nowplaying.insert_one(songdata)
        logger.info('Saved _id: ' + str(db_result.inserted_id) + " acknowledged: " + str(db_result.acknowledged))
    except DuplicateKeyError:
        logger.fatal("Duplicate Key Error. This should never happen, and is last resort data check from the db.")


def get_last_streamed():
    last = db.nowplaying.find({}).sort("startTime", direction=DESCENDING).limit(1).next()
    return last


def check_init_db():
    logger.info("Checking Database")
    if 'nowplaying' in db.collection_names():
        stats = db.command("collstats", "nowplaying")
        if stats['count'] == 0:
            insert_nowplaying_dummy()
    else:
        logger.info("Must be the first run. Creating Collection")
        insert_nowplaying_dummy()
    # Indices
    logger.info("Checking Indices")
    db.nowplaying.create_index([('startTime', DESCENDING)], unique=True, background=True)


def insert_nowplaying_dummy():
    # Insert dummy record
    data = {}
    data['artist_id'] = ''
    data['artist'] = 'Some Artist'
    data['song_id'] = ''
    data['song'] = 'Some Song Name'
    data['album'] = 'Some Album Name'
    data['startTime'] = '2016-06-29T16:06:23.016Z'
    data['spotify'] = {}
    data['spotify']['artist'] = ''
    data['spotify']['song'] = ''
    data['spotify']['url'] = ''
    data['spotify']['uri'] = ''
    data['spotify']['album'] = ''
    data['spotify']['album_image'] = ''
    db.nowplaying.insert_one(data)