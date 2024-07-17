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

import csv
import os
import platform
import re
import tempfile
import zipfile
from math import floor
from pathlib import Path

import yaml
from PySide6.QtCore import (
    Qt,
    QUrl,
    QSize,
    QTimer,
    QEvent,
)
from PySide6.QtGui import (
    QAction,
    QColor,
    QIcon,
    QKeySequence,
)
from PySide6.QtMultimedia import (
    QMediaPlayer,
    QAudioOutput,
    QMediaMetaData,
    QMediaFormat,
)
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWidgets import (
    QMainWindow,
    QFileDialog,
    QHBoxLayout,
    QPushButton,
    QSlider,
    QStyle,
    QVBoxLayout,
    QWidget,
    QLabel,
    QMessageBox,
    QSplitter,
)

from .config import Config
from .dialog import OpenProjectDialog
from .exceptions import LoadProjectError
from .utils import (
    milliseconds_to_formatted_string,
)
from .widgets import (
    AnnotationDialogCode,
    AnnotationGroup,
    TimelineLine,
    TimeLineWidget,
    Annotation,
)
from .format import FORMAT, format_ok
from .about import About
from .coders import Coders

with open(Path(__file__).parent.joinpath("images.py")) as f:
    exec(f.read())


class Player(QMainWindow):
    """A simple Media Player using Qt"""

    def __init__(self, master=None):
        QMainWindow.__init__(self, master)
        self.setWindowTitle("Media Player")
        self.setMinimumSize(QSize(640, 320))

        self.mediaplayer = QMediaPlayer()
        self.media = None
        self.mfps = None
        self.timelineWidget = None
        self.project_file_path = None
        self.csv_to_load = None

        self.config_file_name = "config.yml"
        self.data_file_name = "metadata.yml"

        self.csv_delimiter = ","

        self.coders = None

        # Load the QSS file
        with open(self.get_asset("style.qss"), "r") as f:
            qss = f.read()

        if qss:
            self.setStyleSheet(qss)

        self.installEventFilter(self)

        self.__create_ui()

    def __create_ui(self):
        """Set up the user interface, signals & slots"""
        splitter = QSplitter(Qt.Orientation.Vertical)
        self.widget = QWidget(self)
        self.setCentralWidget(splitter)
        splitter.addWidget(self.widget)

        # Create the video widget
        self.videoframe = QVideoWidget()

        # Create the time box
        self.htimebox = QHBoxLayout()

        # Create the time label
        self.timeLabel = QLabel()
        self.timeLabel.setText("00:00:00.000")
        self.timeLabel.setFixedHeight(24)
        self.htimebox.addWidget(self.timeLabel)

        # Create the position slider
        self.positionslider = QSlider(Qt.Orientation.Horizontal, self)
        self.positionslider.setToolTip("Position")
        self.positionslider.setRange(0, 0)
        self.positionslider.sliderMoved.connect(self.set_position)
        # Add the position slider to the time box
        self.htimebox.addWidget(self.positionslider)

        # Create the duration time box
        self.durationLabel = QLabel()
        self.durationLabel.setText("00:00:00.000")
        self.durationLabel.setFixedHeight(24)
        self.htimebox.addWidget(self.durationLabel)

        # Create the button layout
        self.hbuttonbox = QHBoxLayout()

        # Create the -10 frame button
        self.minus10frame = self.add_player_button(
            QIcon(self.get_asset("minus10.png")),
            "10th Previous Frame",
            self.move_to_ten_previous_frame,
            self.hbuttonbox,
        )

        # Create the -5 frame button
        self.minus5frame = self.add_player_button(
            QIcon(self.get_asset("minus5.png")),
            "5th Previous Frame",
            self.move_to_five_previous_frame,
            self.hbuttonbox,
        )

        # Create the previous frame button
        self.previousframe = self.add_player_button(
            QIcon(self.get_asset("minus1.png")),
            "Previous Frame",
            self.move_to_one_previous_frame,
            self.hbuttonbox,
        )

        # Create the play/pause button
        self.playbutton = self.add_player_button(
            self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay),
            "Play",
            self.play_pause,
            self.hbuttonbox,
        )

        # Create the stop button
        self.stopbutton = self.add_player_button(
            self.style().standardIcon(QStyle.StandardPixmap.SP_MediaStop),
            "Stop",
            self.stop,
            self.hbuttonbox,
        )

        # Create the next frame button
        self.nextframe = self.add_player_button(
            QIcon(self.get_asset("plus1.png")),
            "Next Frame",
            self.move_to_one_next_frame,
            self.hbuttonbox,
        )

        # Create the +5 frame button
        self.plus5frame = self.add_player_button(
            QIcon(self.get_asset("plus5.png")),
            "5th Next Frame",
            self.move_to_five_next_frame,
            self.hbuttonbox,
        )

        # Create the +10 frame button
        self.plus10frame = self.add_player_button(
            QIcon(self.get_asset("plus10.png")),
            "10th Next Frame",
            self.move_to_ten_next_frame,
            self.hbuttonbox,
        )

        self.hbuttonbox.addStretch(1)

        # Create the volume slider
        self.volumeslider = QSlider(Qt.Orientation.Horizontal, self)
        self.volumeslider.setMaximum(100)
        self.volumeslider.setValue(100)
        self.volumeslider.setToolTip("Volume")
        # Add the volume slider to the button layout
        self.hbuttonbox.addWidget(self.volumeslider)
        self.volumeslider.valueChanged.connect(self.set_volume)

        # Create the main layout and add the button layout and video widget
        self.vboxlayout = QVBoxLayout()
        self.vboxlayout.addWidget(self.videoframe)
        self.vboxlayout.addLayout(self.htimebox)
        self.vboxlayout.addLayout(self.hbuttonbox)

        # Add TimeLineWidget
        self.timelineWidget = TimeLineWidget(self)

        # Setup the media player
        self.mediaplayer.setVideoOutput(self.videoframe)
        self.mediaplayer.playbackStateChanged.connect(
            self.playback_state_changed
        )
        self.mediaplayer.mediaStatusChanged.connect(self.media_status_changed)
        self.mediaplayer.positionChanged.connect(self.position_changed)
        self.mediaplayer.durationChanged.connect(self.duration_changed)

        # Setup the audio output
        self.audiooutput = QAudioOutput()
        self.mediaplayer.setAudioOutput(self.audiooutput)

        # Prevent the individual UIs from getting the focus
        for ui in [
            self.playbutton,
            self.stopbutton,
            self.nextframe,
            self.minus5frame,
            self.minus10frame,
            self.plus5frame,
            self.plus10frame,
            self.previousframe,
            self.volumeslider,
            self.positionslider,
            self.videoframe,
        ]:
            ui.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        # Add the main layout to the main window
        self.widget.setLayout(self.vboxlayout)
        splitter.addWidget(self.timelineWidget)

        # Create menu bar
        menu_bar = self.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("&File")

        # Add actions to file menu
        icon = self.style().standardIcon(QStyle.StandardPixmap.SP_DirOpenIcon)
        open_action = QAction(
            icon,
            "&Open video",
            self,
            shortcut=QKeySequence.StandardKey.Open,
            triggered=self.open_file,
        )

        icon = self.style().standardIcon(QStyle.StandardPixmap.SP_DirOpenIcon)
        open_project_action = QAction(
            icon,
            "Open &project",
            self,
            shortcut=QKeySequence(
                Qt.Modifier.CTRL | Qt.Modifier.SHIFT | Qt.Key.Key_O
            ),
            triggered=self.open_project,
        )

        icon = self.style().standardIcon(
            QStyle.StandardPixmap.SP_DialogSaveButton
        )
        self.save_project_action = QAction(
            icon,
            "Save project",
            self,
            shortcut=QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_S),
            triggered=self.save_project,
            enabled=False,
        )

        export_action = QAction(
            "Export...",
            self,
            shortcut=QKeySequence(
                Qt.Modifier.CTRL | Qt.Modifier.SHIFT | Qt.Key.Key_S
            ),
            triggered=self.export_csv_file,
        )

        close_action = QAction(
            "Quit",
            self,
            shortcut=(
                QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_Q)
                if platform.system() == "Windows"
                else QKeySequence.StandardKey.Quit
            ),
            triggered=self.close,
        )

        file_menu.addAction(open_action)
        file_menu.addAction(open_project_action)
        file_menu.addAction(self.save_project_action)
        file_menu.addAction(export_action)
        file_menu.addAction(close_action)

        # Add actions to play menu
        play_menu = menu_bar.addMenu("&Play")
        icon = self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
        self.play_action = QAction(
            icon,
            "Play/Pause",
            self,
            shortcut=Qt.Key.Key_Space,
            triggered=self.play_pause,
            enabled=False,
        )

        icon = self.style().standardIcon(QStyle.StandardPixmap.SP_MediaStop)
        self.stop_action = QAction(
            icon,
            "Stop",
            self,
            shortcut=Qt.Key.Key_S,
            triggered=self.stop,
            enabled=False,
        )

        icon = self.style().standardIcon(
            QStyle.StandardPixmap.SP_MediaSkipBackward
        )
        self.previous_frame_action = QAction(
            icon,
            "Go to the previous frame",
            self,
            shortcut=Qt.Key.Key_Left,
            triggered=self.move_to_one_previous_frame,
            enabled=False,
        )
        self.fifth_previous_frame_action = QAction(
            icon,
            "Go to the fifth previous frame",
            self,
            shortcut=QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_Left),
            triggered=self.move_to_five_previous_frame,
            enabled=False,
        )
        self.tenth_previous_frame_action = QAction(
            icon,
            "Go to the tenth previous frame",
            self,
            shortcut=QKeySequence(
                Qt.Modifier.CTRL | Qt.Modifier.SHIFT | Qt.Key.Key_Left
            ),
            triggered=self.move_to_ten_previous_frame,
            enabled=False,
        )

        icon = self.style().standardIcon(
            QStyle.StandardPixmap.SP_MediaSkipForward
        )
        self.next_frame_action = QAction(
            icon,
            "Go to the next frame",
            self,
            shortcut=Qt.Key.Key_Right,
            triggered=self.move_to_one_next_frame,
            enabled=False,
        )
        self.fifth_next_frame_action = QAction(
            icon,
            "Go to the fifth next frame",
            self,
            shortcut=QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_Right),
            triggered=self.move_to_five_next_frame,
            enabled=False,
        )
        self.tenth_next_frame_action = QAction(
            icon,
            "Go to the tenth next frame",
            self,
            shortcut=QKeySequence(
                Qt.Modifier.CTRL | Qt.Modifier.SHIFT | Qt.Key.Key_Right
            ),
            triggered=self.move_to_ten_next_frame,
            enabled=False,
        )

        play_menu.addAction(self.play_action)
        play_menu.addAction(self.stop_action)
        play_menu.addAction(self.previous_frame_action)
        play_menu.addAction(self.fifth_previous_frame_action)
        play_menu.addAction(self.tenth_previous_frame_action)
        play_menu.addAction(self.next_frame_action)
        play_menu.addAction(self.fifth_next_frame_action)
        play_menu.addAction(self.tenth_next_frame_action)

        edit_menu = menu_bar.addMenu("&Edit")

        # Add actions to edit menu
        self.add_timeline_line_action = QAction(
            "Add Timeline line",
            self,
            triggered=self.timelineWidget.handle_timeline_line,
            enabled=False,
        )
        self.add_timeline_line_action.setShortcuts(
            [
                QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_Return),
                QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_Enter),
            ]
        )

        self.add_annotation_action = QAction(
            "Start Annotation",
            self,
            triggered=self.timelineWidget.handle_annotation,
            enabled=False,
        )
        self.add_annotation_action.setShortcuts(
            [Qt.Key.Key_Return, Qt.Key.Key_Enter]
        )

        edit_menu.addAction(self.add_timeline_line_action)
        edit_menu.addAction(self.add_annotation_action)

        # Add actions to view menu
        view_menu = menu_bar.addMenu("&View")
        self.fullscreen_action = QAction(
            "Toggle Fullscreen",
            self,
            shortcut=Qt.Key.Key_F11,
            triggered=self.on_fullscreen,
        )

        view_menu.addAction(self.fullscreen_action)

        self.timer = QTimer(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.update_time_label)

        # Search for supported video file formats
        self.video_file_extensions = []
        for f in QMediaFormat().supportedFileFormats(QMediaFormat.Decode):
            mime_type = QMediaFormat(f).mimeType()
            name = mime_type.name()
            if re.search("^video/", name):
                self.video_file_extensions.extend(mime_type.suffixes())
        self.file_name_filters = [
            f"Video Files ({' '.join(['*.' + x for x in self.video_file_extensions])})",
            "All Files (*.*)",
        ]

        self.project_file_filters = [
            f"Zip files ({' '.join(['*.zip'])})",
            "All Files (*.*)",
        ]

        # Help menu
        help_menu = menu_bar.addMenu("&Help")
        self.about_action = QAction(
            "About ViCodePy",
            self,
            triggered=self.about,
        )
        help_menu.addAction(self.about_action)

    def about(self):
        About().exec()

    def on_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def play_pause(self):
        """Toggle play/pause status"""
        if (
            self.mediaplayer.playbackState()
            == QMediaPlayer.PlaybackState.PlayingState
        ):
            self.mediaplayer.pause()
        else:
            self.mediaplayer.play()

    def stop(self):
        """Stop player"""
        self.mediaplayer.stop()
        self.playbutton.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
        )

    def no_video_loaded(self):
        dialog = OpenProjectDialog(self)
        dialog.exec()

    def closeEvent(self, event):
        """Display a warning dialog to user when app is closing"""
        if not self.timelineWidget.hasAnnotations():
            return

        action = "ok"
        if self.timelineWidget.csv_needs_save:
            msgBox = QMessageBox(
                QMessageBox.Icon.Warning,
                "Quit the application",
                (
                    "You are about to quit the application. "
                    "The changes made in this session will be lost."
                ),
                QMessageBox.StandardButton.Cancel
                | QMessageBox.StandardButton.Save
                | QMessageBox.StandardButton.Ok,
                self,
            )

            msgBox.button(QMessageBox.StandardButton.Save).setText(
                "Save and Quit"
            )
            msgBox.button(QMessageBox.StandardButton.Ok).setText("Quit")
            msgBox.exec()

            if msgBox.clickedButton() == msgBox.button(
                QMessageBox.StandardButton.Ok
            ):
                action = "ok"
            elif msgBox.clickedButton() == msgBox.button(
                QMessageBox.StandardButton.Save
            ):
                action = "save"
            else:
                action = "ignore"

        if action == "ok":
            # Clean up temp dir
            if self.temp_dir:
                self.temp_dir.cleanup()
            event.accept()
        elif action == "save":
            if self.save_project():
                # Clean up temp dir
                if self.temp_dir:
                    self.temp_dir.cleanup()
                event.accept()
            else:
                event.ignore()
        else:
            event.ignore()

    def open_file(self, filename=None):
        """Open a media file in a MediaPlayer"""
        dialog_txt = "Open Video File"
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle(dialog_txt)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setNameFilters(self.file_name_filters)
        file_dialog.exec()
        if file_dialog.result() == AnnotationDialogCode.Accepted:
            # Load only the first of the selected file
            try:
                filename = file_dialog.selectedFiles()[0]
                self.load_video_file(filename)
                self.load_config_file()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"{e}")

    def open_project(self, filename=None):
        """Open a media project in a MediaPlayer"""
        dialog_txt = "Open Project File"
        project_dialog = QFileDialog(self)
        project_dialog.setWindowTitle(dialog_txt)
        project_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        project_dialog.setNameFilters(self.project_file_filters)
        project_dialog.exec()
        if project_dialog.result() == AnnotationDialogCode.Accepted:
            try:
                filename = project_dialog.selectedFiles()[0]
                self.load_project_file(filename)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"{e}")

    def load_file(self, filename):
        try:
            if os.path.splitext(filename)[1] in [
                "." + ext for ext in self.video_file_extensions
            ]:
                self.load_video_file(filename)
                self.load_config_file()
            elif os.path.splitext(filename)[1] == ".zip":
                self.load_project_file(filename)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"{e}")

    def load_video_file(self, filename):
        """Load video file"""
        if not os.path.exists(filename) or not os.path.isfile(filename):
            raise FileNotFoundError(
                f"FileNotFoundError : {filename} doesn't exist"
            )

        # getOpenFileName returns a tuple, so use only the actual file name
        self.media = QUrl.fromLocalFile(filename)

        # Enable the buttons
        self.playbutton.setEnabled(True)
        self.stopbutton.setEnabled(True)

        # Put the media in the media player
        self.mediaplayer.setSource(self.media)

        # Set the title of the track as window title
        self.setWindowTitle(filename)

        # Show first frame
        self.mediaplayer.play()
        self.mediaplayer.pause()

        # Clear the timelineWidget
        if bool(self.media):
            self.timelineWidget.clear()
        self.timelineWidget.load_common()

    def load_project_file(self, filename):
        """Load project file"""
        if not os.path.exists(filename) or not os.path.isfile(filename):
            raise FileNotFoundError(
                f"FileNotFoundError : {filename} doesn't exist"
            )

        # filename is a zip file
        self.project_file_path = filename

        with zipfile.ZipFile(filename, "r") as zip_file:
            # Create temp dir
            temp_dir = tempfile.TemporaryDirectory()

            # Find metadata.yml file
            data_file = zip_file.open(self.data_file_name)
            if not data_file:
                raise LoadProjectError().add_note("Data file not found")

            # Load data from metadata.yml
            with zip_file.open(self.data_file_name) as f:
                data = yaml.load(f, Loader=yaml.FullLoader)
                if not format_ok(data["format"]):
                    raise LoadProjectError("Format problem")
                files = zip_file.namelist()

                # Search for video in temp dir
                video_file = data["video"]
                if video_file not in files:
                    raise LoadProjectError("Failed to load video file")

                # Search for config.yml in temp dir
                config_file = self.config_file_name
                if config_file not in files:
                    raise LoadProjectError("Failed to load config file")

                # Search for csv file in temp dir
                csv_file = os.path.splitext(video_file)[0] + ".csv"
                if csv_file not in files:
                    raise LoadProjectError("Failed to load csv file")

                # Extract all files in temp dir
                zip_file.extractall(temp_dir.name)

                # Load video file from temp dir
                self.load_video_file(os.path.join(temp_dir.name, video_file))

                # Load config file from in temp dir
                self.load_config_file(os.path.join(temp_dir.name, config_file))

                # Load csv data file from in temp dir
                self.csv_to_load = os.path.join(temp_dir.name, csv_file)

            self.temp_dir = temp_dir

    def load_config_file(self, filename=None):
        """load presets from config.yml file"""
        # Read the YAML file
        config = Config() if filename is None else Config(filename)

        # Access the values
        if "timelines" in config:
            # Loop through timesline lines from config file
            for i, timelineLine in enumerate(config["timelines"]):
                # Create timeline line
                line = TimelineLine(timelineLine["name"], self.timelineWidget)

                # Add the timeline line to the TimeLineWidget
                self.timelineWidget.add_timeline_line(line)

                # Loop through groups of timeline lines
                groups = timelineLine["events"]
                for i, group in enumerate(groups):
                    line.groups.append(
                        AnnotationGroup(
                            i, str(group["name"]), QColor(group["color"]), line
                        )
                    )

        if "csv-delimiter" in config:
            self.csv_delimiter = config["csv-delimiter"]

        if "coders" in config:
            self.coders = Coders(config["coders"])

    def load_csv_file(self, filename=None):
        """load csv file"""
        if os.path.isfile(filename):
            with open(filename, newline="") as csv_file:
                dialect = csv.Sniffer().sniff(csv_file.read())
                csv_file.seek(0)
                csv_reader = csv.DictReader(csv_file, dialect=dialect)
                for row in csv_reader:
                    # Search for timeline
                    timeline_line = (
                        self.timelineWidget.get_timeline_line_by_name(
                            row["timeline"]
                        )
                    )

                    # If timeline from csv doesn't exist in TimelineWidget,
                    # escape row
                    if not timeline_line:
                        continue

                    # Search for group
                    group = timeline_line.get_group_by_name(row["label"])

                    # If group from csv doesn't exist in timeline_line,
                    # then add it
                    if not group:
                        continue

                    annotation = Annotation(
                        self.timelineWidget,
                        timeline_line,
                        int(row["begin"]),
                        int(row["end"]),
                    )

                    group.add_annotation(annotation)
                    annotation.ends_creation()
        else:
            QMessageBox.critical(
                self,
                "Error",
                "The file you tried to load does not exist.",
            )

        self.csv_to_load = None

    def save_project(self) -> bool:
        """Save project file"""
        temp_dir = tempfile.TemporaryDirectory()

        # Construct the default file name from the QUrl of the video file
        target_directory = self.media.path()
        target_file_name = os.path.splitext(
            os.path.basename(self.media.path())
        )[0]
        csv_file_name = target_file_name + ".csv"
        if self.project_file_path:
            target_directory = self.project_file_path
            target_file_name = os.path.splitext(
                os.path.basename(self.project_file_path)
            )[0]

        target_directory = (
            os.path.dirname(target_directory) + "/" + target_file_name + ".zip"
        )

        # 1. Create config file from information of timelineWidget in
        # tmp directory
        if self.coders:
            if not self.coders.current:
                self.coders.set_current()
        else:
            self.coders = Coders({})
            self.coders.set_current()
        self.coders.current.set_date_now()

        config_file_path = os.path.join(temp_dir.name, self.config_file_name)
        self.export_config_file(config_file_path)

        # 2. Create CSV file "data.csv" from information of timelineWidget in
        # tmp directory
        csv_file_path = os.path.join(temp_dir.name, csv_file_name)
        self.export_csv_file(csv_file_path)

        data_file_path = os.path.join(temp_dir.name, self.data_file_name)
        with open(data_file_path, "w") as f:
            yaml.safe_dump(
                {
                    "video": os.path.basename(self.media.path()),
                    "format": FORMAT,
                },
                f,
            )

        # Open FileDialog
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Save project",
            target_directory,
            "Zip Files (*.zip);;All Files (*)",
        )
        if path:
            with zipfile.ZipFile(path, "w") as zip_file:
                zip_file.write(data_file_path, self.data_file_name)
                zip_file.write(config_file_path, self.config_file_name)
                zip_file.write(csv_file_path, csv_file_name)
                zip_file.write(
                    self.media.toLocalFile(),
                    os.path.basename(self.media.path()),
                )
            self.timelineWidget.csv_needs_save = False
            return True
        return False

    def set_volume(self, volume):
        """Set the volume"""
        self.audiooutput.setVolume(volume / 100)

    def playback_state_changed(self, state):
        """Set the button icon when media changes state"""
        if state == QMediaPlayer.PlaybackState.PlayingState:
            self.timer.start()
            self.playbutton.setIcon(
                self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause)
            )
        else:
            self.timer.stop()
            self.playbutton.setIcon(
                self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay)
            )
            # Fix : stop to the write frame
            self.set_position(self.mediaplayer.position())

        self.stopbutton.setEnabled(
            state != QMediaPlayer.PlaybackState.StoppedState
        )
        self.stop_action.setEnabled(
            state != QMediaPlayer.PlaybackState.StoppedState
        )
        for ui in [
            self.minus10frame,
            self.minus5frame,
            self.previousframe,
            self.nextframe,
            self.plus5frame,
            self.plus10frame,
        ]:
            ui.setEnabled(state == QMediaPlayer.PlaybackState.PausedState)
        self.previous_frame_action.setEnabled(
            state == QMediaPlayer.PlaybackState.PausedState
        )
        self.fifth_previous_frame_action.setEnabled(
            state == QMediaPlayer.PlaybackState.PausedState
        )
        self.tenth_previous_frame_action.setEnabled(
            state == QMediaPlayer.PlaybackState.PausedState
        )
        self.nextframe.setEnabled(
            state == QMediaPlayer.PlaybackState.PausedState
        )
        self.next_frame_action.setEnabled(
            state == QMediaPlayer.PlaybackState.PausedState
        )
        self.fifth_next_frame_action.setEnabled(
            state == QMediaPlayer.PlaybackState.PausedState
        )
        self.tenth_next_frame_action.setEnabled(
            state == QMediaPlayer.PlaybackState.PausedState
        )
        self.add_timeline_line_action.setEnabled(
            state == QMediaPlayer.PlaybackState.PausedState
        )
        self.add_annotation_action.setEnabled(
            state == QMediaPlayer.PlaybackState.PausedState
        )

    def media_status_changed(self, state):
        if state == QMediaPlayer.MediaStatus.LoadedMedia:
            # Enable play button
            self.play_action.setEnabled(True)
            # Enable save project button
            self.save_project_action.setEnabled(True)
            # Check if metadata is available
            metadata = self.mediaplayer.metaData()
            if metadata:
                # If metadata is available, set the frame rate
                fps = metadata.value(QMediaMetaData.Key.VideoFrameRate)
                self.mfps = int(1000 / fps)
            else:
                self.mfps = None

        if state == QMediaPlayer.MediaStatus.BufferedMedia:
            if self.csv_to_load:
                self.load_csv_file(self.csv_to_load)
                self.timelineWidget.changed = False

    def position_changed(self, position):
        """Update the position slider"""
        self.positionslider.setValue(position)
        self.timelineWidget.value = position
        self.timeLabel.setText(milliseconds_to_formatted_string(position))
        self.timelineWidget.update()

    def duration_changed(self, duration):
        """Update the duration slider"""
        self.positionslider.setRange(0, duration)
        self.timelineWidget.duration = duration
        self.durationLabel.setText(milliseconds_to_formatted_string(duration))
        self.timelineWidget.update()

    def set_position(self, position):
        """Set the position"""
        position = int(self.mfps * floor(position / self.mfps) + self.mfps / 2)
        if position < 0:
            position = int(self.mfps / 2)
        self.timelineWidget.view.set_position(position)

    def move_to_ten_previous_frame(self):
        self.move_to_previous_X_frame(10)

    def move_to_five_previous_frame(self):
        self.move_to_previous_X_frame(5)

    def move_to_one_previous_frame(self):
        self.move_to_previous_X_frame(1)

    def move_to_previous_X_frame(self, nb_frame):
        state = self.mediaplayer.playbackState()
        if self.mfps is None or state != QMediaPlayer.PlaybackState.PausedState:
            return
        self.set_position(self.mediaplayer.position() - (self.mfps * nb_frame))

    def move_to_ten_next_frame(self):
        self.move_to_next_X_frame(10)

    def move_to_five_next_frame(self):
        self.move_to_next_X_frame(5)

    def move_to_one_next_frame(self):
        self.move_to_next_X_frame(1)

    def move_to_next_X_frame(self, nb_frame):
        """Set the position to the next frame"""
        state = self.mediaplayer.playbackState()
        if self.mfps is None or state != QMediaPlayer.PlaybackState.PausedState:
            return
        self.set_position(self.mediaplayer.position() + (self.mfps * nb_frame))

    def export_csv_file(self, target_path=None) -> bool:
        """Export data in CSV file"""
        if not target_path:
            if not self.isExportable():
                QMessageBox.warning(
                    self, "No Data", "There is no data to save to CSV."
                )
                return False

            # Construct the default file name from the QUrl of the video file
            default_target_path = (
                os.path.dirname(self.media.path())
                + "/"
                + os.path.splitext(os.path.basename(self.media.path()))[0]
                + ".csv"
            )

            target_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save CSV",
                default_target_path,
                "CSV Files (*.csv);;All Files (*)",
            )
        if target_path:
            with open(target_path, "w", newline="") as f:
                writer = csv.writer(f, delimiter=self.csv_delimiter)
                # Write headers
                writer.writerow(header for header in TimeLineWidget.CSV_HEADERS)

                # Write data
                for timeline_line in sorted(
                    self.timelineWidget.timeline_lines, key=lambda x: x.name
                ):
                    for annotation in timeline_line.annotations:
                        comment = annotation.comment.replace('"', '\\"')
                        row = [
                            timeline_line.name,
                            annotation.group.name,
                            annotation.startTime,
                            annotation.endTime,
                            annotation.endTime - annotation.startTime,
                            comment,
                        ]
                        writer.writerow(row)
            self.timelineWidget.csv_needs_save = False
            return True
        return False

    def isExportable(self) -> bool:
        """Return true if the media file is exportable"""
        return (
            self.mediaplayer is not None
            and self.timelineWidget is not None
            and self.timelineWidget.timeline_lines
            and self.hasAnnotations()
        )

    def export_config_file(self, target_path=None):
        config = Config(target_path)

        config["timelines"] = [
            {
                "name": timeline_line.name,
                "events": [
                    {"name": group.name, "color": group.color.name()}
                    for group in timeline_line.groups
                ],
            }
            for timeline_line in self.timelineWidget.timeline_lines
        ]

        if self.coders:
            config["coders"] = self.coders.to_list()

        # Write data
        config.save()

    def hasAnnotations(self) -> bool:
        """Return true if at least one annotation exists"""
        for timeline_line in self.timelineWidget.timeline_lines:
            if bool(timeline_line.annotations):
                return True
        return False

    def update_time_label(self):
        """Update the time label"""
        self.timeLabel.setText(
            milliseconds_to_formatted_string(self.mediaplayer.position())
        )

    def get_asset(self, filename):
        return str(Path(__file__).parent.joinpath("assets").joinpath(filename))

    def add_player_button(self, icon, tooltip, cbfunc, hbox):
        ui = QPushButton()
        ui.setEnabled(False)
        ui.setFixedHeight(24)
        ui.setIconSize(QSize(16, 16))
        ui.setIcon(icon)
        ui.setToolTip(tooltip)
        ui.clicked.connect(cbfunc)
        hbox.addWidget(ui)
        return ui

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.KeyRelease:
            if event.key() == Qt.Key.Key_Right:
                if event.isAutoRepeat():
                    if (
                        self.mediaplayer.playbackState()
                        != QMediaPlayer.PlaybackState.PlayingState
                    ):
                        self.mediaplayer.play()
                else:
                    self.mediaplayer.pause()
                return True
        return False
