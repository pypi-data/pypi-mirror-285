import logging

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
                               QApplication)

from .tab_dock import TabDock
from ..models.profile_dataset import ProfileDataset


logger = logging.getLogger(__name__)


class SequenceViewDialog(QDialog):
    def __init__(self, template, variables, parent=None):
        super().__init__(parent)
        self.template = template
        self.variables = variables
        self.ds = ProfileDataset(template, variables)
        self.setWindowTitle("Sequence View")
        self.app = QApplication.instance()
        self.init_ui()
        self.add_profile_channels()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.dock = TabDock(False)
        layout.addWidget(self.dock.dock_area)

        groups = self.ds.channels_by_group()
        if groups.get('profiles', []):
            self.prof_pw = self.dock.new_plot_window("Profiles")
        if groups.get('run_seq', []):
            self.run_pw = self.dock.new_plot_window("Run Sequences")
            self.stop_pw = self.dock.new_plot_window("Stop Sequences")

        btns_layout = QHBoxLayout()
        cancel_btn = QPushButton("Cancel", self)
        cancel_btn.clicked.connect(self.reject)
        accept_btn = QPushButton("Load Boxes", self)
        accept_btn.clicked.connect(self.accept)
        btns_layout.addStretch()
        btns_layout.addWidget(cancel_btn)
        btns_layout.addWidget(accept_btn)
        layout.addLayout(btns_layout)

    def add_profile_channels(self):
        groups = self.ds.channels_by_group()
        for ch in groups.get('profiles', []):
            self.prof_pw.add_channel(self.ds, ch['id'])
        run_chs = groups.get('run_seq', [])
        stop_chs = groups.get('stop_seq', [])
        for ch in sorted(run_chs, key=lambda ch: ch['id'], reverse=True):
            self.run_pw.add_channel(self.ds, ch['id'])
        for ch in sorted(stop_chs, key=lambda ch: ch['id'], reverse=True):
            self.stop_pw.add_channel(self.ds, ch['id'])
