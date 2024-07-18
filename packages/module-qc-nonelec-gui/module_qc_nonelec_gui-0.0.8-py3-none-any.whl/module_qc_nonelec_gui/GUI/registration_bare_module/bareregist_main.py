from __future__ import annotations

import logging
import sys

import itkdb
from PyQt5.QtWidgets import QApplication, QMainWindow

from module_qc_nonelec_gui.GUI.registration_bare_module import (
    bareinfo_win,
    bareregist_win,
    connectpd_win,
    feinfo_win,
    initial_win,
    sensorinfo_win,
)

log = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Bare module registration tool")
        self.setGeometry(0, 0, 340, 255)

        # self.pd_client = self.parent.pd_client
        # self.connectITKPD()
        self.baremodule_info = {
            "project": "P",
            "subproject": "PG",
            "institution": "",
            "componentType": "BARE_MODULE",
            "type": "",
            "properties": {"FECHIP_VERSION": "", "THICKNESS": "", "SENSOR_TYPE": ""},
            "child": {"FE_CHIP": [], "SENSOR_TILE": []},
        }

        self.baremodule_doc = {}
        self.fechip_doc = {}
        self.sensor_doc = {}
        self.user_info = {}
        self.connectpd()

        # other member variables
        self.bare_doc = None
        self.initial_wid = None
        self.bareinfo_wid = None
        self.bareregist_wid = None
        self.feinfo_wid = None
        self.sensorinfo_wid = None
        self.connectpd_wid = None
        self.u = None

    def init_ui(self):
        self.choose_menu()

    def choose_menu(self):
        self.bare_doc = {}
        self.baremodule_info["child"]["FE_CHIP"] = []
        self.baremodule_info["child"]["SENSOR_TILE"] = []
        self.initial_wid = initial_win.InitialWindow(self)
        self.parent.update_widget(self.initial_wid)
        log.info("\n---------------------------------------------------------------")

    def bareupdate(self):
        self.bareinfo_wid = bareinfo_win.BareInfoWindow(self)
        self.parent.update_widget(self.bareinfo_wid)

    def bareregist(self):
        self.bareregist_wid = bareregist_win.BareRegistWindow(self)
        self.parent.update_widget(self.bareregist_wid)

    def set_windowsize(self, x, y):
        self.setGeometry(0, 0, x, y)

    def feinfo(self):
        self.feinfo_wid = feinfo_win.FEInfoWindow(self)
        self.parent.update_widget(self.feinfo_wid)

    def sensorinfo(self):
        self.sensorinfo_wid = sensorinfo_win.SensorInfoWindow(self)
        self.parent.update_widget(self.sensorinfo_wid)

    def connectITKPD(self):
        self.connectpd_wid = connectpd_win.ConnectPDWindow(self)
        self.parent.update_widget(self.connectpd_wid)

    def scale_window(self, x, y):
        QApplication.processEvents()
        self.set_windowsize(x, y)

    def connectpd(self):
        # def connectpd(self,code1,code2):
        #     token = self.process_request(code1,code2)
        #     if token == 0:
        #         log.info('fail to connect ITk PD')

        # else:
        #     log.info('success to connect ITk PD')
        # self.userinfo = self.parent.pd_client.get("getUser", json={ "userIdentity":self.parent.u.identity})
        self.baremodule_info["institution"] = self.parent.userinfo["institutions"][0][
            "code"
        ]
        self.baremodule_doc = self.parent.pd_client.get(
            "getComponentTypeByCode", json={"project": "P", "code": "BARE_MODULE"}
        )
        # log.info("-----------------------")
        self.fechip_doc = self.parent.pd_client.get(
            "getComponentTypeByCode", json={"project": "P", "code": "FE_CHIP"}
        )
        # log.info(self.fechip_doc)
        # log.info("-----------------------")
        self.sensor_doc = self.parent.pd_client.get(
            "getComponentTypeByCode", json={"project": "P", "code": "SENSOR_TILE"}
        )
        # log.info(self.sensor_doc)
        # self.choose_menu()

    def register_baremodule(self):
        #####################
        #       doc = self.parent.pd_client.get('getComponent', json={"component": "20UPGB40500017"})
        #####################
        bare_ins = self.parent.pd_client.post(
            "registerComponent", json=self.baremodule_info
        )
        log.info("Register bare module!!")
        self.bare_doc = self.parent.pd_client.get(
            "getComponent", json={"component": bare_ins["component"]["serialNumber"]}
        )
        log.info("-----------------------------------")
        log.info("### Registered components ###")
        log.info("Bare Module: " + bare_ins["component"]["serialNumber"])
        log.info("")
        log.info("Check the components from your component page.")
        log.info("Link: https://itkpd-test.unicorncollege.cz/myComponents")
        # msgBox = QMessageBox.information(None, 'Information',bare_ins["component"]["serialNumber"] + " is registered", QMessageBox.Ok)
        # if msgBox == QMessageBox.Ok:
        #     self.feinfo()
        # msgBox = QMessageBox()
        # msgBox.setText("bare module is registered")
        # msgBox.setInformativeText(bare_ins["component"]["serialNumber"])
        # msgBox.setStandardButtons(QMessageBox.Ok)
        # ret = msgBox.exec_()
        # if ret == QMessageBox.Ok:

    def get_bareinfo(self, atlsn):
        self.bare_doc = self.parent.pd_client.get(
            "getComponent", json={"component": atlsn}
        )

    def get_componentinfo(self, atlsn):
        return self.parent.pd_client.get("getComponent", json={"component": atlsn})

    def assemble_fechip(self):
        for j in range(4):
            json = {
                "parent": self.bare_doc["code"],
                "slot": self.bare_doc["children"][j]["id"],
                "child": self.baremodule_info["child"]["FE_CHIP"][j],
            }
            self.parent.pd_client.post("assembleComponentBySlot", json=json)
        log.info("Assemble FE chips!!")

    def assemble_sensor(self):
        json = {"parent": self.bare_doc["code"], "child": self.sensor_id}
        self.parent.pd_client.post("assembleComponent", json=json)
        log.info("Assemble SENSOR TILE!!")

    def update_baremodule(self):
        if "FE_CHIP" in self.baremodule_info["child"]:
            for _j in range(4):
                json = {
                    "parent": self.bare_doc["code"],
                }

        if "SENSOR_TILE" in self.baremodule_info["child"]:
            json = {"parent": self.bare_doc["code"], "child": self.sensor_id}
            self.parent.pd_client.post("assembleComponent", json=json)

    def process_request(self, code1, code2):
        try:
            self.u = itkdb.core.User(access_code1=code1, access_code2=code2)
            self.u.authenticate()
            self.parent.pd_client = itkdb.Client(user=self.u)
            log.info("Authorized.")
            request = 1
        except Exception:
            log.exception(
                "Not authorized. Please login for ITkPD by using itkpd-interface/authenticate.sh"
            )
            request = 0
        return request

    #    def update_widget(self, w):
    #        self.setCentralWidget(w)
    #        self.show()
    #        self.scale_window(360,270)

    def close_window(self):
        self.close()

    def call_another_window(self, window):
        self.hide()
        self.update_statusbar(window)
        window.init_ui()

    def back_to_last_window(self, window):
        self.hide()
        window.show()

    def receive_return(self, window):
        window.hide()
        self.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
