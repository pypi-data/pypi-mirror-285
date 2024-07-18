from __future__ import annotations

import json
import logging
import os
from pathlib import Path

log = logging.getLogger(__name__)


class config_modifier:
    def __init__(self):
        self.module_qc_nonelec_gui_dir = "/".join(
            os.path.realpath(__file__).split("/")[:-2]
        )
        self.module_qc_nonelec_gui_config = (
            self.module_qc_nonelec_gui_dir + "/configuration/configuration.json"
        )

        with Path(self.module_qc_nonelec_gui_config).open(encoding="utf-8") as f_conf:
            self.configuration = json.load(f_conf)

    def print_current(self):
        # Print current setting of LocalDB
        log.info(f"Config File : {self.module_qc_nonelec_gui_config}")
        log.info(f"LocalDB IP  : {self.configuration['localDB_info']['address']}")
        log.info(f"LocalDB Port: {self.configuration['localDB_info']['port']}")

    def set_ip_port(self, ip="127.0.0.1", port="27017"):
        self.configuration["localDB_info"]["address"] = ip
        self.configuration["localDB_info"]["port"] = port

    def wrap_up(self, filename=""):
        if filename == "":
            filename = self.module_qc_nonelec_gui_config
        with Path(filename).open(mode="w", encoding="utf-8") as f_new:
            json.dump(self.configuration, f_new, indent=4, ensure_ascii=False)
