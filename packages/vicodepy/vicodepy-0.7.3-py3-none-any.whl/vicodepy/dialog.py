# ViCodePy - A video coder for psychological experiments
#
# Copyright (C) 2024 Esteban Milleret
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
    QDialog,
    QLineEdit,
    QFormLayout,
    QDialogButtonBox,
    QStyle,
    QPushButton,
    QVBoxLayout,
    QLabel,
)


class TimelineLineDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add a new timeline line")

        self.nameLineEdit = QLineEdit(self)
        self.layout = QFormLayout(self)
        self.layout.addRow(
            "Enter name of the new timeline line :", self.nameLineEdit
        )

        self.buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel,
            self,
        )
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        self.layout.addWidget(self.buttons)

    def get_text(self):
        return self.nameLineEdit.text()


class OpenProjectDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Open a project")

        self.layout = QVBoxLayout(self)

        self.open_video_btn = QPushButton(
            self.style().standardIcon(QStyle.StandardPixmap.SP_DirOpenIcon),
            "Open video",
            self,
        )
        self.open_project_btn = QPushButton(
            self.style().standardIcon(QStyle.StandardPixmap.SP_DirOpenIcon),
            "Open project",
            self,
        )

        self.buttons = QDialogButtonBox(self)
        self.buttons.addButton(
            self.open_video_btn, QDialogButtonBox.ButtonRole.AcceptRole
        )
        self.buttons.addButton(
            self.open_project_btn, QDialogButtonBox.ButtonRole.AcceptRole
        )
        self.buttons.addButton(QDialogButtonBox.StandardButton.Cancel)

        self.buttons.clicked.connect(self.perform_action)
        self.buttons.rejected.connect(self.reject)

        self.layout.addWidget(
            QLabel("Choose a video or a project file to start coding")
        )
        self.layout.addWidget(self.buttons)
        self.setLayout(self.layout)

    def perform_action(self, button):
        if button == self.open_video_btn:
            self.parent().open_file()
        elif button == self.open_project_btn:
            self.parent().open_project()
        self.accept()
