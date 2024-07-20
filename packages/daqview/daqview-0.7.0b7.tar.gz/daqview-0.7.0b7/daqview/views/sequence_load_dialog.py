import logging

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                               QProgressBar, QPlainTextEdit,
                               QApplication)

from ..models import sequencing


logger = logging.getLogger(__name__)


class SequenceLoadDialog(QDialog):
    def __init__(self, template, variables, parent=None):
        super().__init__(parent)
        self.template = template
        self.variables = variables
        self.setWindowTitle("Loading Sequences")
        self.app = QApplication.instance()
        self.init_ui()
        self.cancelled = False
        self.got_error = False
        QTimer.singleShot(50, self.run)

    def run(self):
        self.store_json()
        self.load_daus()
        if not self.cancelled and not self.got_error:
            self.add_log("Finished.")
            self.cancel_btn.setEnabled(False)
            self.close_btn.setEnabled(True)
        if self.got_error:
            self.add_log("\nEncountered an error loading boxes.")
            self.cancel_btn.setEnabled(False)
            self.close_btn.setEnabled(True)

    def cancel_clicked(self):
        self.cancelled = True
        self.add_log("Cancelled.")
        self.cancel_btn.setEnabled(False)
        self.close_btn.setEnabled(True)

    def add_log(self, message):
        logger.info(message)
        self.log.appendPlainText(message)
        self.app.processEvents()

    def add_error(self, message):
        logger.info(message)
        self.log.appendPlainText(message)
        self.got_error = True
        self.app.processEvents()

    def increment_progress(self):
        self.progress.setValue(self.progress.value() + 1)
        self.app.processEvents()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.progress = QProgressBar(self)
        n_items = 1
        n_items += len(self.template.get('daus', []))
        n_items += len(self.template.get('unused_daus', []))
        self.progress.setRange(0, n_items)
        self.progress.setValue(0)
        layout.addWidget(self.progress)

        self.log = QPlainTextEdit(self)
        self.log.setReadOnly(True)
        layout.addWidget(self.log)

        btns_layout = QHBoxLayout()
        cancel_btn = QPushButton("Cancel", self)
        cancel_btn.clicked.connect(self.cancel_clicked)
        self.cancel_btn = cancel_btn
        close_btn = QPushButton("Close", self)
        close_btn.clicked.connect(self.accept)
        close_btn.setEnabled(False)
        self.close_btn = close_btn
        btns_layout.addStretch()
        btns_layout.addWidget(cancel_btn)
        btns_layout.addWidget(close_btn)
        layout.addLayout(btns_layout)

        self.resize(512, 320)

    def store_json(self):
        data_path = self.app.prefs.get_daqng_data_path()
        self.add_log(f"Using data directory {data_path}")
        self.add_log("Writing JSON metdata file...")
        sequencing.write_json_metadata(
            data_path, self.template, self.variables)
        self.increment_progress()

    def load_daus(self):
        # Render and load sequences and profiles to used DAUs
        for dau in self.template.get('daus', []):
            if self.cancelled:
                return
            dau_id = dau.get('dau')
            dau_type = dau.get('type', '')
            if dau_type.startswith('profile_'):
                _, _, data = sequencing.generate_profile(dau, self.variables)
                self.add_log(f"Loading profile to box {dau_id}...")
                self.load_dau(dau, data)
                self.increment_progress()
            elif dau_type == "sequence":
                _, _, data = sequencing.generate_sequence(dau, self.variables)
                self.add_log(f"Loading sequence to box {dau_id}...")
                self.load_dau(dau, data)
                self.increment_progress()

        # Send empty profiles to all unused DAUs
        nop = sequencing.generate_nop()
        for dau in self.template.get('unused_daus', []):
            if self.cancelled:
                return
            dau_id = dau.get('dau')
            self.add_log(f"Loading empty profile to box {dau_id}...")
            self.load_dau(dau, nop, unimpl_ok=True)
            self.increment_progress()

    def load_dau(self, dau, data, unimpl_ok=False):
        dau_id = dau.get('dau')
        addr = dau.get('addr')
        try:
            sequencing.load_box(dau.get('addr'), data, unimpl_ok=unimpl_ok)
        except (OSError, AssertionError, RuntimeError) as e:
            self.add_error(f"Error: Could not load {dau_id}: {e}")
            self.add_error(f"Error: Using address {addr}")
