#!/usr/bin/env python3
######################################################
## Author1: Shohei Shirabe (shohei.shirabe at cern.ch)
## Copyright: Copyright 2019, ldbtools
## Date: Apr. 2020
## Project: Local Database Tools
## Description: ITkPD Interface
######################################################
from __future__ import annotations

import getpass
import logging
import sys
from pathlib import Path

import itkdb

from module_qc_nonelec_gui.dbinterface.upload_results_sample import upload_results

log = logging.getLogger(__name__)

####################################
## upload test results


def upload():
    paths = sys.argv

    log.info("ITKDB_ACCESS_CODE1:")
    code1 = getpass.getpass()
    log.info("ITKDB_ACCESS_CODE2:")
    code2 = getpass.getpass()
    token = process_request(code1, code2)

    if token == 0:
        sys.exit(1)
    else:
        if len(paths) > 1:
            for path in paths[1:]:
                with Path(path).open(encoding="utf-8") as f:
                    next(f)
                    lines = f.readlines()
                    for line in lines:
                        mod_name, stage, run_num, date, result1, result2 = line.split()
                        upload_results(
                            code1,
                            code2,
                            mod_name,
                            stage,
                            run_num,
                            date,
                            result1,
                            result2,
                        )
        else:
            log.info("path to results are not set")


def process_request(code1, code2):
    try:
        u = itkdb.core.User(access_code1=code1, access_code2=code2)
        u.authenticate()
        log.info("Authorized.")
        request = 1
    except Exception:
        log.exception(
            "Not authorized. Please login for ITkPD by using itkpd-interface/authenticate.sh"
        )
        request = 0
    return request


if __name__ == "__main__":
    upload()
