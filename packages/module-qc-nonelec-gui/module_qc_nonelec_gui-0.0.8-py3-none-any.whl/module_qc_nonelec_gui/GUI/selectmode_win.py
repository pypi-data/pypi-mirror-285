from __future__ import annotations

import logging

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QButtonGroup,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)

log = logging.getLogger(__name__)


class SelectmodeWindow(QWidget):
    def __init__(self, parent=None):
        super(QWidget, self).__init__()
        self.parent = parent

        layout = QVBoxLayout()
        mode_vbox = QVBoxLayout()
        mode_box = QVBoxLayout()
        button_box = QHBoxLayout()

        label_header = QLabel()
        label_header.setText(
            f'<center><font size="4">module-qc-nonelec-gui (version {self.parent.version})</font></center>'
        )

        label_text = QLabel()
        label_text.setText('<center><font size="6">Select the service</font></center>')

        Next_button = QPushButton("&Next")
        Next_button.clicked.connect(self.next_page)

        button_box.addStretch()
        button_box.addWidget(Next_button)

        radio_QC = self.make_radiobutton("Upload result of QC test to localDB")
        radio_QC.setChecked(True)
        if self.parent.isPractice:
            radio_bare = self.make_radiobutton(
                "Register Bare-module (inavailable at practice mode)"
            )
            radio_bare.setStyleSheet(
                "QRadioButton{font: 12pt; color:gray} QRadioButton::indicator { width: 12px; height: 12px; color: gray;};"
            )
            radio_bare.setCheckable(False)
        else:
            radio_bare = self.make_radiobutton("Register Bare-module")
        self.mode_radio_group = QButtonGroup()
        self.mode_radio_group.addButton(radio_QC, 0)
        self.mode_radio_group.addButton(radio_bare, 1)

        mode_vbox.addWidget(radio_QC)
        mode_vbox.addWidget(radio_bare)
        mode_box.addStretch()
        mode_box.addLayout(mode_vbox)
        mode_box.addStretch()

        mode_group = QGroupBox("")
        mode_group.setStyleSheet("QGroupBox { font-size: 15px;font-weight: bold;} ")
        mode_group.setLayout(mode_box)

        layout.addWidget(label_header)
        layout.addWidget(label_text)
        layout.addStretch()
        layout.addWidget(mode_group)
        layout.addStretch()
        layout.addLayout(button_box)

        self.setLayout(layout)

    def make_radiobutton(self, label):
        radiobutton = QRadioButton(label)
        radiobutton.setCheckable(True)
        radiobutton.setFocusPolicy(Qt.NoFocus)
        radiobutton.setStyleSheet(
            "QRadioButton{font: 12pt;} QRadioButton::indicator { width: 12px; height: 12px;};"
        )
        return radiobutton

    def next_page(self):
        try:
            log.info("[Mode] " + self.mode_radio_group.checkedButton().text())
        except Exception:
            QMessageBox.warning(
                None, "Warning", "Please check each radiobutton.", QMessageBox.Ok
            )

        self.parent.receive_mode(self.mode_radio_group.checkedId())
