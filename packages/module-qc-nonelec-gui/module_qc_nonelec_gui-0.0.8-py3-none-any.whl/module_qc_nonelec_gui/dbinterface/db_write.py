from __future__ import annotations

import argparse
import sys
from logging import (
    INFO,
    getLogger,
)
from pathlib import Path

import yaml
from pymongo import MongoClient

logger = getLogger("Log")
logger.setLevel(INFO)


##################
def readConfig(conf_path):
    logger.debug("Read Config File.")
    if Path(conf_path).is_file():
        with Path(conf_path).open(encoding="utf-8") as f:
            return yaml.load(f, Loader=yaml.SafeLoader)
    return None


def readKey(i_path):
    with Path(i_path).open(encoding="utf-8") as file_text:
        file_keys = file_text.read().split()
        return {"username": file_keys[0], "password": file_keys[1]}


##################
# get arguments
def getArgs():
    logger.debug("Get Arguments.")
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument(
        "command",
        help="option*\tfunction\ninit\tFunction initialization & Connection check",
        type=str,
        nargs="+",
    )
    parser.add_argument(
        "--config", help="Set User Config Path to Local DB Server.", type=str
    )
    parser.add_argument(
        "--username", help="Set the User Name of Local DB Server", type=str
    )
    parser.add_argument(
        "--password", help="Set the Password of Local DB Server", type=str
    )
    parser.add_argument("--database", help="Set Database Config Path", type=str)
    parser.add_argument("--user", help="Set User Config Path", type=str)
    parser.add_argument("--site", help="Set Site Config Path", type=str)
    parser.add_argument("--log", help="Set Log Mode", action="store_true")

    args = parser.parse_args()

    if args.config:
        conf = readConfig(args.config)
        if "username" in conf and not args.username:
            args.username = conf["username"]
        if "password" in conf and not args.password:
            args.password = conf["password"]

    return args


def init(db_cfg):
    logger.debug("Initialize.")

    if db_cfg == {}:
        logger.error("There is no default database config")
        sys.exit(1)

    url = f"mongodb://{db_cfg['hostIp']}:{db_cfg['hostPort']}"
    msg = f"[Connection Test] DB Server: {url}/{db_cfg.get('dbName', 'localdb')}"
    logger.info(msg)

    ##################
    # Connection check
    ##################

    # max_server_delay = 1
    # username = None
    # password = None
    # authSource = db_cfg.get("dbName", "localdb")
    ### check tls/ssl
    db_tls = db_cfg.get("tls", {}).get("enabled", False)
    db_ssl = db_cfg.get("ssl", {}).get("enabled", False)
    if db_tls:
        db_certfile = db_cfg.get("tls", {}).get("CertificateKeyFile", None)
        db_ca_certs = db_cfg.get("tls", {}).get("CAFile", None)
    elif db_ssl:
        db_certfile = db_cfg.get("ssl", {}).get("PEMKeyFile", None)
        db_ca_certs = db_cfg.get("ssl", {}).get("CAFile", None)
    if db_tls or db_ssl:
        url += f"/?ssl=true&ssl_ca_certs={db_ca_certs}&ssl_certfile={db_certfile}&ssl_match_hostname=false"
        ### authenticate mechanism
        if db_cfg.get("auth", None) == "x509":
            url += "&authMechnism=MONGODB-X509"
    # client = MongoClient(url, serverSelectionTimeoutMS=max_server_delay)
    # localdb = client[db_cfg.get("dbName", "localdb")]
    # try:
    #    # localdb['fs.files'].create_index([('hash', DESCENDING), ('_id', DESCENDING)])
    #    # lcoaldb['component'].create_index([('serialNumber', DESCENDING)])
    #    # localdb['testRun'].create_index([('startTime', DESCENDING),('user_id', DESCENDING), ('address', DESCENDING)])
    #    # localdb['componentTestRun'].create_index([('name', DESCENDING), ('testRun', DESCENDING)])
    #    # localdb["vi_results"].create_index([("component_id", DESCENDING)])
    # except errors.ServerSelectionTimeoutError as err:
    #     ### Connection failed
    #     logger.error("---> Connection is BAD.")
    #     logger.error(f"     {err}")
    #     logger.error(
    #         "     Access https://localdb-docs.readthedocs.io/en/master/faq/ to check more detail"
    #     )
    # except errors.OperationFailure as err:
    #     ### Need user authentication
    #     if db_cfg.get("KeyFile", None) and db_cfg["KeyFile"] != "null":
    #         keys = readKey(db_cfg["KeyFile"])
    #         username = keys["username"]
    #         password = keys["password"]
    #     if args.username:
    #         username = args.username
    #     elif db_cfg.get("username", None):
    #         username = db_cfg["username"]
    #     elif os.environ.get("username", None):
    #         username = os.environ["username"]
    #     if args.password:
    #         password = args.password
    #     elif db_cfg.get("password", None):
    #         password = db_cfg.get("password", None)
    #     elif os.environ.get("password", None):
    #         password = os.environ["password"]
    #     if username and password:
    #         try:
    #             localdb.authenticate(username, password)
    #         except errors.OperationFailure as err:
    #             logger.error("Authentication failed.")
    #             return False
    #     else:
    #         return False

    #     # localdb["vi_results"].create_index([("component_id", DESCENDING)])

    #     # register.__set_localdb(localdb)
    #     # register.__set_list(db_cfg.get("stage", []), "stage")
    #     # register.__set_list(db_cfg.get("environment", []), "environment")
    #     # register.__set_list(db_cfg.get("component", []), "component")

    #     logger.info("---> Connection is GOOD.")

    return True


def connectDB():
    return MongoClient(port=27017)


def write_vi_result(moduleid, inspector, stage, results, comments):
    c = connectDB()
    localdb = c["test"]

    localdb.vi_collection.insert_one(
        {"compomet_name": moduleid},
        {"inspector": inspector},
        {"stage": stage},
        {"result": results},
        {"comment": comments},
    )
    # localdb.test_collection.insert_one({"component_name":'20UPBMO0000007',"stage":'TEST',"number":1 })


def update_vi_result(moduleid, results, comments):
    c = connectDB()
    localdb = c["test"]

    localdb.vi_collection.update_one(
        {"compomet_name": moduleid}, {set: {"result": results}}
    )
    localdb.vi_collection.update_one(
        {"compomet_name": moduleid}, {set: {"comment": comments}}
    )
    # localdb.test_collection.insert_one({"component_name":'20UPBMO0000007',"stage":'TEST',"number":1 })
