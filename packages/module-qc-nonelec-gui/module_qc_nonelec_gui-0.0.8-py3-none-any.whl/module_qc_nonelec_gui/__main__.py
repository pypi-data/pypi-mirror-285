from __future__ import annotations

import sys

import typer
from PyQt5.QtWidgets import QApplication

from module_qc_nonelec_gui import config_modifier
from module_qc_nonelec_gui.cli import MainWindow


def main():
    typer.echo("Launching GUI")
    app = QApplication(sys.argv[1:])
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())


def localDB_config():
    typer.echo("Setting LocalDB IP and Port...")
    conf_mod = config_modifier.config_modifier()
    conf_mod.print_current()
    ip = input("New LocalDB IP? ")
    port = input("New LocalDB Port? ")
    conf_mod.set_ip_port(ip, port)
    yesno = input("Do you want to update the config file? (Yes/No) ")
    if yesno == "Yes":
        conf_mod.wrap_up(conf_mod.module_qc_nonelec_gui_config)
        typer.echo("Configuration file was updated.")
    else:
        typer.echo("Changes discarded. Done.")


if __name__ == "__main__":
    typer.run(main)
