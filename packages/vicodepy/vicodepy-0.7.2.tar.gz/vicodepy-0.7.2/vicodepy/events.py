# ViCodePy - A video coder for psychological experiments
#
# Copyright (C) 2024 Rafael Laboissière
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program. If not, see <https://www.gnu.org/licenses/>.

from PySide6.QtWidgets import (
    QColorDialog,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
)
from functools import partial
from .utils import color_fg_from_bg


class ChooseEvent(QDialog):
    def __init__(self, events, info):
        super().__init__()
        self.setWindowTitle("Choose event")
        layout = QFormLayout(self)
        info = QLabel(info)
        layout.addRow(info)
        eventbox = QHBoxLayout()
        for i, event in enumerate(events):
            button = QPushButton(event.name)
            bg_color = event.color
            fg_color = color_fg_from_bg(bg_color)
            button.setAutoFillBackground(False)
            button.setStyleSheet(
                "QPushButton {"
                "background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,"
                f"   stop:0 {bg_color.name()}, stop:1 {bg_color.name()});"
                f" color: {fg_color.name()};"
                "border: 2px solid black;"
                "border-radius: 5px"
                "}"
                "QPushButton:hover {"
                "    border: 3px solid black;"
                "}"
            )
            button.clicked.connect(partial(self.set_chosen, i))
            eventbox.addWidget(button)
        layout.addRow(eventbox)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def set_chosen(self, val):
        self.chosen = val
        self.accept()

    def get_chosen(self):
        return self.chosen


class ChangeEvent(QDialog):
    def __init__(self, event, timeline):
        super().__init__()
        self.setWindowTitle("Change event")
        self.event = event
        self.color = event.color
        self.timeline = timeline
        layout = QFormLayout(self)
        widgetbox = QHBoxLayout()
        self.label_edit = QLineEdit(self)
        self.label_edit.setText(event.name)
        widgetbox.addWidget(self.label_edit)
        self.color_button = QPushButton("color")
        self.color_button.clicked.connect(self.choose_color)
        self.set_style()
        widgetbox.addWidget(self.color_button)
        layout.addRow(widgetbox)
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel,
            self,
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def accept(self):
        self.event.name = self.label_edit.text()
        for a in self.timeline.annotations:
            if a.group == self.event:
                a.set_group(self.event)
                a.update()
        super().accept()

    def choose_color(self):
        dialog = QColorDialog(self.color, self)
        dialog.exec()
        if dialog.result() == dialog.DialogCode.Accepted:
            self.event.color = dialog.currentColor()
            self.set_style()

    def set_style(self):
        bg_color = self.event.color
        fg_color = color_fg_from_bg(bg_color)
        self.color_button.setStyleSheet(
            "QPushButton {"
            "background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,"
            f"   stop:0 {bg_color.name()}, stop:1 {bg_color.name()});"
            f" color: {fg_color.name()};"
            "border: 2px solid black;"
            "border-radius: 5px;"
            "padding: 6px"
            "}"
            "QPushButton:hover {"
            "    border: 3px solid black;"
            "}"
        )
