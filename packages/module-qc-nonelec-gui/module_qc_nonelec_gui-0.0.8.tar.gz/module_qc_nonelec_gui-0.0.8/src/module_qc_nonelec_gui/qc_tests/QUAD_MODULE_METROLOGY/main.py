from __future__ import annotations

import logging

from PyQt5.QtWidgets import QMainWindow

from module_qc_nonelec_gui.qc_tests.QUAD_MODULE_METROLOGY import initial_metrology

log = logging.getLogger(__name__)


class TestWindow(QMainWindow):
    ############################################################################################
    def __init__(self, parent=None):
        #        super(QMainWindow, self).__init__(parent)
        super(QMainWindow, self).__init__()
        self.parent = parent

        self.setGeometry(0, 0, 510, 255)

        self.componentType = "MODULE"
        self.stage = "MODULE/ASSEMBLY"

        self.init_ui()

    def receive_result(self, _result):
        for k, v in _result.get("results").items():
            self.parent.testRun.get("results").get("Measurements").update({k: v})
        self.parent.receive_result(self)

    ############################################################################################
    def init_ui(self):
        self.initial_bare_wid = initial_metrology.InitialWindow(self)
        self.parent.update_widget(self.initial_bare_wid)

    def close_and_return(self):
        self.close()
        self.parent.back_from_test()

    def back_page(self):
        self.parent.init_ui()

    def back_window(self):
        self.parent.receive_backpage()

    def call_another_window(self, window):
        self.hide()
        window.init_ui()
