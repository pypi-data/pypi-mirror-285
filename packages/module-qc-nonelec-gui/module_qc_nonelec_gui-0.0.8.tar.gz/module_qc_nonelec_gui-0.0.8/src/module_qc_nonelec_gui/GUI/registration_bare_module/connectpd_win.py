from __future__ import annotations

from PyQt5.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class ConnectPDWindow(QWidget):
    def __init__(self, parent=None):
        super(QWidget, self).__init__()
        self.parent = parent

        titlebox = QVBoxLayout()
        layout = QVBoxLayout()
        hbox_bottom = QHBoxLayout()
        edit_form = QFormLayout()
        # form_box = QHBoxLayout()

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

        Next_button = QPushButton("&Login")
        Next_button.clicked.connect(self.pass_accesscode)

        titlebox.addWidget(label_text)

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
        self.parent.connectpd(
            self.edit_accesscode1.text(), self.edit_accesscode2.text()
        )
