from __future__ import annotations

import logging

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QCheckBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

log = logging.getLogger(__name__)


class ConnectPDWindow(QWidget):
    def __init__(self, parent=None):
        super(QWidget, self).__init__()
        self.parent = parent

        titlebox = QVBoxLayout()
        layout = QVBoxLayout()
        hbox_bottom = QHBoxLayout()
        edit_form = QFormLayout()

        label_text = QLabel()
        label_text.setText(
            '<center><font size="6">Log in to Production DB</font></center>'
        )
        label_accesscode1 = QLabel()
        label_accesscode1.setText("ITKDB ACCESS CODE 1:")
        label_accesscode2 = QLabel()
        label_accesscode2.setText("ITKDB ACCESS CODE 2:")

        self.edit_accesscode1 = QLineEdit()
        self.edit_accesscode1.setEchoMode(QLineEdit().Password)
        self.edit_accesscode2 = QLineEdit()
        self.edit_accesscode2.setEchoMode(QLineEdit().Password)

        Next_button = QPushButton("&Next")
        Next_button.clicked.connect(self.pass_accesscode)

        titlebox.addWidget(label_text)

        self.check_practice = QCheckBox()
        self.check_practice.setText("practice mode")
        self.check_practice.stateChanged.connect(self.change_to_practice)
        if self.parent.isPractice:
            self.check_practice.setCheckState(Qt.Checked)
        hbox_bottom.addStretch()
        hbox_bottom.addWidget(self.check_practice)
        hbox_bottom.addWidget(Next_button)

        edit_form.addRow(label_accesscode1, self.edit_accesscode1)
        edit_form.addRow(label_accesscode2, self.edit_accesscode2)

        layout.addStretch()
        layout.addLayout(titlebox)
        layout.addStretch()
        layout.addLayout(edit_form)
        layout.addLayout(hbox_bottom)

        self.setLayout(layout)

    def pass_accesscode(self):
        if self.check_practice.checkState() == Qt.Checked:
            self.parent.isPractice = True
            log.info("[Mode] practice mode")
        else:
            self.parent.isPractice = False

        self.parent.connectpd(
            self.edit_accesscode1.text(), self.edit_accesscode2.text()
        )

    def change_to_practice(self, state):
        if state == Qt.Checked:
            self.parent.isPractice = True
            self.parent.update_statusbar(self.parent)
        else:
            self.parent.isPractice = False
            self.parent.update_statusbar(self.parent)
