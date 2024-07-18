from __future__ import annotations

import json
import logging
from pathlib import Path

import gridfs

log = logging.getLogger(__name__)


def jpeg_formatter(localdb, path):
    fs = gridfs.GridFS(localdb)
    with Path(path).open(mode="rb") as f:
        binary = f.read()
    return fs.put(binary)


def uploader(localdb, json_file):
    # localdb = connectDB()
    try:
        with Path(json_file).open(encoding="utf-8") as f:
            json_load = json.load(f)
    except FileNotFoundError:
        json_load = json.loads(json_file)
    except Exception:
        json_load = json_file
    # if testname == "visual_inspection":
    localdb.QC.result.insert_one(json_load)


def property_uploader(localdb, json_file):
    # localdb = connectDB()
    try:
        with Path(json_file).open(encoding="utf-8") as f:
            json_load = json.load(f)
    except FileNotFoundError:
        json_load = json.loads(json_file)
    except Exception:
        json_load = json_file
    # if testname == "visual_inspection":
    localdb.QC.module.prop.insert_one(json_load)


def updater(localdb, testname, module_id, stage, path_jpegs, dt):
    # localdb = connectDB()
    img_dic = {}
    for page, path_jpeg in path_jpegs.items():
        img_dic[page] = str(jpeg_formatter(localdb, path_jpeg))

    if testname == "Optical":
        # module = localdb.component.find_one(
        #     {"and": [{"serialNumber": module_id}, {"componentType": "module"}]}
        # )
        doc = localdb.QC.result.find_one(
            {"and": [{"component": module_id}, {"stage": stage}, {"sys": {"mts": dt}}]}
        )
        log.info(doc)
        log.info(doc["results"])
        # # log.info(type(doc))
        # dic = doc["results"][0]
        # log.info(type(dic))
        anomaly_list = doc["results"]["anomaly"]
        comment_list = doc["results"]["comment"]
        localdb.QC.result.find_one_and_update(
            {"and": [{"component": module_id}, {"stage": stage}]},
            {
                "set": {
                    "results": {
                        "anomaly": anomaly_list,
                        "comment": comment_list,
                        "img": img_dic,
                    }
                }
            },
        )


def find_and_show(localdb, testname, _module_id, _stage):
    # localdb = connectDB()
    # doc = localdb.collectionname.find({'and':[{"component_name":module_id}, {"stage":stage}]})
    if testname == "Optical":
        docs = localdb.QC.result.find()
    for doc in docs:
        log.info(doc)
