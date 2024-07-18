from __future__ import annotations

import logging

from pymongo import MongoClient

log = logging.getLogger(__name__)


def connectDB(address="127.0.0.1", port="27017"):
    #    url = 'mongodb://{0}{1}'.format("127.0.0.1", "27017")
    url = f"mongodb://{address}:{port}/"
    client = MongoClient(url)
    # client = MongoClient(port=27017)
    localdb = client["localdb"]
    localdbtools = client["localdbtools"]
    return localdb, localdbtools


def authenticator(localdb, username, password):
    # localdb = connectDB()
    try:
        localdb.authenticate(username, password)
        log.info("Authentication succeeded")
        return True
    except Exception:
        log.exception("Authentication failed")
        return False
