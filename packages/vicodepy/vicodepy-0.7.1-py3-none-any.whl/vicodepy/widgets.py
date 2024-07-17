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

from abc import abstractmethod
from enum import IntEnum

from PySide6.QtCore import (
    Qt,
    QRectF,
    QLine,
    QPointF,
    QSizeF,
    Signal,
)
from PySide6.QtGui import (
    QPainter,
    QColor,
    QPolygonF,
    QPen,
    QFontMetrics,
)
from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtWidgets import (
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QLabel,
    QDialog,
    QLineEdit,
    QColorDialog,
    QComboBox,
    QGraphicsScene,
    QGraphicsView,
    QGraphicsRectItem,
    QGraphicsItem,
    QMenu,
    QMessageBox,
    QScrollBar,
    QAbstractSlider,
)

from .dialog import TimelineLineDialog
from .ticklocator import TickLocator
from .utils import color_fg_from_bg
from .comment import AnnotationComment
from .events import ChooseEvent, ChangeEvent


class ZoomableGraphicsView(QGraphicsView):
    MARGIN_BOTTOM = 15.0

    def __init__(self, scene: QGraphicsScene, parent=None):
        super().__init__(scene, parent)
        self.zoomFactor = 1.0
        self.zoomStep = 1.2
        self.zoomShift = None
        self.minimum_zoomFactor = 1.0

        vertical_scrollbar = QScrollBar(Qt.Orientation.Vertical, self)
        vertical_scrollbar.valueChanged.connect(
            self.on_vertical_scroll_value_changed
        )
        self.setVerticalScrollBar(vertical_scrollbar)

    def wheelEvent(self, event):
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            if not self.parent().player.media:
                return
            mouse_pos = self.mapToScene(event.position().toPoint()).x()
            if event.angleDelta().y() > 0:
                self.zoomShift = mouse_pos * (1 - self.zoomStep)
                self.zoom_in()
            else:
                self.zoomShift = mouse_pos * (1 - 1 / self.zoomStep)
                self.zoom_out()
            self.zoomShift = None
        elif event.modifiers() == Qt.KeyboardModifier.ShiftModifier:
            if event.angleDelta().y() > 0:
                action = QAbstractSlider.SliderSingleStepAdd
            else:
                action = QAbstractSlider.SliderSingleStepSub
            self.horizontalScrollBar().triggerAction(action)
        else:
            super().wheelEvent(event)

    def on_vertical_scroll_value_changed(self, value):
        if self.parent().timelineScale:
            self.parent().timelineScale.setPos(0, value)

    def zoom_in(self):
        self.zoomFactor *= self.zoomStep
        self.update_scale()

    def zoom_out(self):
        if self.zoomFactor / self.zoomStep >= self.minimum_zoomFactor:
            self.zoomFactor /= self.zoomStep
            self.update_scale()

    def update_scale(self):
        # Update the size of the scene with zoomFactor
        self.scene().setSceneRect(
            0,
            0,
            self.width() * self.zoomFactor,
            self.scene().height(),
        )

        if self.zoomShift:
            previousAnchor = self.transformationAnchor()
            self.setTransformationAnchor(QGraphicsView.NoAnchor)
            self.translate(self.zoomShift, 0)
            self.setTransformationAnchor(previousAnchor)

    def mouseDoubleClickEvent(self, event):
        super().mouseDoubleClickEvent(event)

        # Get the position click from the scene
        map = self.mapToScene(self.scene().sceneRect().toRect())
        x = map.boundingRect().x()

        # Calculate the time of the position click
        time = int(
            (x + event.scenePosition().x())
            * self.parent().duration
            / self.scene().width()
        )

        self.parent().player.set_position(time)

    def set_position(self, time):
        # During the creation of a new annotation
        if self.parent().currentAnnotation:
            time = (
                self.parent().currentAnnotation.get_time_from_bounding_interval(
                    time
                )
            )

        # Cope with selected annotation
        for i in self.parent().scene.selectedItems():
            if isinstance(i, Annotation):
                time = i.get_time_from_bounding_interval(time)
                break

        # Set time to the video player
        self.parent().player.mediaplayer.setPosition(int(time))

    def keyPressEvent(self, event):
        pass


class TimeLineWidget(QWidget):
    CSV_HEADERS = ["timeline", "label", "begin", "end", "duration", "comment"]
    valueChanged = Signal(int)
    durationChanged = Signal(int)

    def __init__(self, player=None):
        """Initializes the timeline widget"""
        super().__init__(player)
        self._duration = 0
        self._value = 0

        self.selected_timelineLine = None
        self.currentAnnotation: Annotation = None
        self.player = player
        self.scene = QGraphicsScene()
        self.scene.sceneRectChanged.connect(self.on_scene_changed)
        self.scene.selectionChanged.connect(self.on_selection_changed)
        self.timeline_lines: list[TimelineLine] = []
        self.view = ZoomableGraphicsView(self.scene, self)
        self.indicator = None
        self.timelineScale = None

        self.view.setViewportUpdateMode(
            QGraphicsView.ViewportUpdateMode.FullViewportUpdate
        )
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setFrameShape(QGraphicsView.Shape.NoFrame)
        self.view.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
        )

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.view)
        self.setLayout(layout)
        self.setMouseTracking(True)
        self.scene.setSceneRect(0, 0, self.view.width(), self.view.height())

        self.valueChanged.connect(self.on_value_changed)
        self.durationChanged.connect(self.on_duration_changed)

        self.csv_needs_save = False

    def on_scene_changed(self, rect):
        # Update annotations
        for timeline_line in self.timeline_lines:
            timeline_line.update_rect_width(rect.width())
            for annotation in timeline_line.annotations:
                annotation.update_rect()

        if self.currentAnnotation:
            self.currentAnnotation.update_rect()

        # Update timelineScale display
        if self.timelineScale:
            # Update indicator
            if self.duration:
                self.timelineScale.indicator.setX(
                    self.value * rect.width() / self.duration
                )
            self.timelineScale.update_rect()

    def on_selection_changed(self):
        selected_items = self.scene.selectedItems()
        selected = None
        if len(selected_items) == 1:
            selected = selected_items[0]
            if isinstance(selected, TimelineLine):
                self.selected_timelineLine = selected
        for s in self.timeline_lines:
            s.select = s == selected

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        if value != self._value:
            self._value = value
            self.valueChanged.emit(value)

    def on_value_changed(self, new_value):
        # First, update the current annotation, if it exists. If the cursor
        # value goes beyond the allowed bounds, bring it back and do not update
        # the other widgets.
        if self.currentAnnotation:
            if (
                self.currentAnnotation.lower_bound
                and new_value < self.currentAnnotation.lower_bound
            ):
                new_value = self.currentAnnotation.lower_bound
            elif (
                self.currentAnnotation.upper_bound
                and new_value > self.currentAnnotation.upper_bound
            ):
                new_value = self.currentAnnotation.upper_bound
                if (
                    self.player.mediaplayer.playbackState()
                    == QMediaPlayer.PlaybackState.PlayingState
                ):
                    self.player.mediaplayer.pause()
            start_time = self.currentAnnotation.startTime
            end_time = self.currentAnnotation.endTime
            mfps = self.player.mfps
            if start_time < end_time:
                if new_value >= start_time:
                    self.currentAnnotation.update_end_time(
                        new_value + int(mfps / 2)
                    )
                else:
                    self.currentAnnotation.update_start_time(end_time)
                    self.currentAnnotation.update_end_time(start_time - mfps)
            else:
                if new_value <= start_time:
                    self.currentAnnotation.update_end_time(
                        new_value - int(mfps / 2)
                    )
                else:
                    self.currentAnnotation.update_start_time(end_time)
                    self.currentAnnotation.update_end_time(start_time + mfps)

        # Update indicator position
        if self.timelineScale and self.timelineScale.indicator:
            self.timelineScale.indicator.setX(
                new_value * self.scene.width() / self.duration
            )

        if isinstance(self.scene.focusItem(), AnnotationHandle):
            annotation_handle: AnnotationHandle = self.scene.focusItem()
            annotation_handle.change_time(new_value)

        # Change appearance of annotation under the cursor
        # (Brute force approach; this ought to be improved)
        if not self.currentAnnotation:
            for t in self.timeline_lines:
                for a in t.annotations:
                    a.penWidth = Annotation.PEN_WIDTH_OFF_CURSOR
            if self.selected_timelineLine:
                for a in self.selected_timelineLine.annotations:
                    if a.startTime <= new_value and a.endTime >= new_value:
                        a.penWidth = Annotation.PEN_WIDTH_ON_CURSOR
                        break

    @property
    def duration(self):
        return self._duration

    @duration.setter
    def duration(self, duration):
        if duration != self._duration:
            self._duration = duration
            self.durationChanged.emit(duration)

    def on_duration_changed(self, new_duration):
        # Update timeline Scale
        self.timelineScale = TimelineScale(self)
        self.update()

    def load_common(self):
        # Recreate timeline
        self.timelineScale = TimelineScale(self)

    def clear(self):
        # Clear timelineScene
        self.scene.clear()
        self.timeline_lines = []

    def handle_annotation(self):
        """Handles the annotation"""
        if not self.selected_timelineLine:
            QMessageBox.warning(self, "Warning", "No timeline selected")
            return
        else:
            if self.currentAnnotation is None:
                can_be_initiate, lower_bound, upper_bound = (
                    Annotation.annotationDrawCanBeInitiate(
                        self.selected_timelineLine.annotations, self.value
                    )
                )
                if can_be_initiate:
                    self.currentAnnotation = Annotation(
                        self,
                        self.selected_timelineLine,
                        None,
                        None,
                        lower_bound,
                        upper_bound,
                    )
                self.player.add_annotation_action.setText("Finish annotation")

            else:
                # End the current annotation
                agd = AnnotationGroupDialog(
                    self.currentAnnotation.timeline_line
                )
                agd.exec()

                if agd.result() == AnnotationDialogCode.Accepted:
                    if agd.state == "create":
                        # When creating a new group, create the group and add the
                        # current annotation to it
                        group = AnnotationGroup(
                            len(self.currentAnnotation.timeline_line.groups)
                            + 1,
                            agd.group_name_text.text(),
                            agd.color,
                            self,
                        )
                        group.add_annotation(self.currentAnnotation)
                        self.currentAnnotation.timeline_line.add_group(group)
                    else:
                        # Otherwise, we are selecting an existing group, and will
                        # retrieve the group and add the annotation to it
                        group = agd.combo_box.currentData()
                        group.add_annotation(self.currentAnnotation)
                    self.currentAnnotation.ends_creation()
                    self.currentAnnotation = None
                    self.player.add_annotation_action.setText(
                        "Start annotation"
                    )
                elif agd.result() == AnnotationDialogCode.Aborted:
                    self.currentAnnotation.remove()
                    self.currentAnnotation = None
                    self.player.add_annotation_action.setText(
                        "Start annotation"
                    )
                self.update()

    def handle_timeline_line(self):
        dialog = TimelineLineDialog(self)
        dialog.exec()
        if dialog.result() == AnnotationDialogCode.Accepted:
            self.add_timeline_line(TimelineLine(dialog.get_text(), self))

    def resizeEvent(self, a0):
        if self.timelineScale:
            origin = self.view.mapToScene(0, 0).x()
            width_before = self.scene.width() / self.view.zoomFactor
            width_after = self.view.width()
            shift = origin * (1 - width_after / width_before)
            self.view.update_scale()
            previousAnchor = self.view.transformationAnchor()
            self.view.setTransformationAnchor(QGraphicsView.NoAnchor)
            self.view.translate(shift, 0)
            self.view.setTransformationAnchor(previousAnchor)
        else:
            self.scene.setSceneRect(
                0,
                0,
                self.view.width(),
                TimelineScale.FIXED_HEIGHT + TimelineLine.FIXED_HEIGHT,
            )

        self.update()

    def keyPressEvent(self, event):
        # if key pressed is escape key
        if event.key() == Qt.Key.Key_Escape:
            # Delete annotation
            if self.currentAnnotation is not None:
                confirm_box = AnnotationConfirmMessageBox(self)
                if (
                    confirm_box.result()
                    == AnnotationConfirmMessageBox.DialogCode.Accepted
                ):
                    self.currentAnnotation.remove()
                    self.currentAnnotation = None
                    self.update()

    def add_timeline_line(self, line):
        self.timeline_lines.append(line)
        line.addToScene()

        # Calculate the new height of the scene
        new_height = (
            TimelineScale.FIXED_HEIGHT
            + len(self.timeline_lines) * TimelineLine.FIXED_HEIGHT
            + ZoomableGraphicsView.MARGIN_BOTTOM
        )
        scene_rect = self.scene.sceneRect()
        scene_rect.setHeight(new_height)
        self.scene.setSceneRect(scene_rect)

        # Set maximum height of the widget
        self.setMaximumHeight(int(new_height))

    def get_timeline_line_by_name(self, name):
        """Get the timeline line by name"""
        return next((x for x in self.timeline_lines if x.name == name), None)

    def hasAnnotations(self) -> bool:
        return any(len(line.annotations) for line in self.timeline_lines)


class TimelineLine(QGraphicsRectItem):
    FIXED_HEIGHT: float = 60.0

    def __init__(self, name: str, timeline_widget: TimeLineWidget = None):
        super().__init__()
        self.name = name
        self.timelineWidget = timeline_widget
        self.annotations: list[Annotation] = []
        self.groups: list[AnnotationGroup] = []
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable)
        self.setAcceptHoverEvents(True)
        self.textItem = TimelineLineLabel(self.name, self)
        self._select = False

    @property
    def select(self):
        return self._select

    @select.setter
    def select(self, select):
        if select != self._select:
            self._select = select

    def addToScene(self):
        """Add the timeline to the scene"""
        # Set Y of the timeline based on the timescale height and the timeline
        # lines heights present on the scene
        self.setPos(
            0,
            self.timelineWidget.timelineScale.rect().height()
            + (len(self.timelineWidget.timeline_lines) - 1) * self.FIXED_HEIGHT,
        )

        # Set the right rect based on the scene width and the height constant
        self.setRect(
            0,
            0,
            self.timelineWidget.scene.width(),
            self.FIXED_HEIGHT,
        )

        # Add line to the scene
        self.timelineWidget.scene.addItem(self)

    def add_group(self, group):
        """Add a group to the timeline line"""
        self.groups.append(group)
        self.groups.sort(key=lambda x: x.name)

    def remove_group(self, group):
        """Remove a group from the timeline line"""
        self.groups.remove(group)

    def get_group_by_name(self, name):
        return next((x for x in self.groups if x.name == name), None)

    def add_annotation(self, annotation):
        """Add an annotation to the timeline line"""
        self.annotations.append(annotation)
        self.annotations.sort(key=lambda x: x.startTime)
        self.timelineWidget.csv_needs_save = True

    def remove_annotation(self, annotation):
        """Remove an annotation from the timeline line"""
        self.annotations.remove(annotation)

    def update_rect_width(self, new_width: float):
        """Update the width of the timeline line"""
        rect = self.rect()
        rect.setWidth(new_width)
        rect_label = self.textItem.rect()
        rect_label.setWidth(new_width)
        self.textItem.setRect(rect_label)
        self.setRect(rect)

    def on_remove(self):
        if self.annotations:
            answer = QMessageBox.question(
                self.timelineWidget,
                "Confirmation",
                "There are annotations present. "
                "Do you want to remove this timeline?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if answer == QMessageBox.StandardButton.Yes:
                while self.annotations:
                    self.annotations[0].remove()
        # The following does not yet work, since there is no provision for
        # adjusting the positions of the timelines inside the time pane.
        # self.timelineWidget.scene.removeItem(self)
        # if self in self.timelineWidget.timeline_lines:
        #     self.timelineWidget.timeline_lines.remove(self)
        # del self

    def edit_label(self):
        dialog = QDialog()
        dialog.setWindowTitle("Timeline label")

        label = QLineEdit()
        label.setText(self.textItem.text)
        label.returnPressed.connect(dialog.accept)
        edit = QHBoxLayout()
        edit.addWidget(label)

        cancel = QPushButton("Cancel")
        cancel.clicked.connect(dialog.reject)
        save = QPushButton("Save")
        save.clicked.connect(dialog.accept)
        buttons = QHBoxLayout()
        buttons.addWidget(cancel)
        buttons.addWidget(save)

        layout = QVBoxLayout()
        layout.addLayout(edit)
        layout.addLayout(buttons)
        dialog.setLayout(layout)

        dialog.exec()
        if dialog.result() == dialog.DialogCode.Accepted:
            self.textItem.set_text(label.text())

    def edit_events(self):
        while True:
            events_dialog = ChooseEvent(
                self.groups, "Choose the event to be modified:"
            )
            events_dialog.exec()
            if events_dialog.result() == QMessageBox.DialogCode.Accepted:
                i = events_dialog.get_chosen()
                g = self.groups[i]
                ChangeEvent(g, self).exec()
            if events_dialog.result() == QMessageBox.DialogCode.Rejected:
                break

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            menu = QMenu()
            menu.addAction("Add new timeline").triggered.connect(
                self.timelineWidget.handle_timeline_line
            )
            menu.addAction(
                "Delete timeline (not yet fully implemented)"
            ).triggered.connect(self.on_remove)
            menu.addAction("Edit timeline label").triggered.connect(
                self.edit_label
            )
            menu.addAction("Edit events").triggered.connect(self.edit_events)
            menu.exec(event.screenPos())
        else:
            super().mousePressEvent(event)
        return


class TimelineLineLabel(QGraphicsRectItem):
    FIXED_HEIGHT = 20

    def __init__(self, text: str, parent: TimelineLine = None):
        super().__init__(parent)
        self.text = text
        rect = self.parentItem().rect()
        rect.setHeight(self.FIXED_HEIGHT)
        self.setRect(rect)
        self.parent = parent

    def paint(self, painter, option, widget=...):
        # Draw the rectangle
        self._draw_rect(painter)

        # Draw the text
        self._draw_text(painter)

    def _draw_rect(self, painter):
        """Draw the timeline line label rectangle"""
        # Set Pen and Brush for rectangle
        if self.parent.select:
            color = QColor(40, 40, 40)
        else:
            color = QColor(200, 200, 200)
        painter.setPen(color)
        painter.setBrush(color)
        painter.drawRect(self.rect())

    def _draw_text(self, painter):
        """Draw the timeline line label text"""
        if self.parent.select:
            color = QColor(200, 200, 200)
        else:
            color = QColor(150, 150, 150)
        painter.setPen(color)
        painter.setBrush(color)

        font = painter.font()
        fm = QFontMetrics(font)

        text_width = fm.boundingRect(self.text).width()
        text_height = fm.boundingRect(self.text).height()
        # Get timeline polygon based on the viewport
        timeline_line_in_viewport_pos = (
            self.parentItem().timelineWidget.view.mapToScene(
                self.rect().toRect()
            )
        )

        bounding_rect = timeline_line_in_viewport_pos.boundingRect()

        # Get the viewport rect
        viewport_rect = self.parentItem().timelineWidget.view.viewport().rect()

        # Calcul the x position for the text
        x_alignCenter = bounding_rect.x() + viewport_rect.width() / 2

        text_position = QPointF(x_alignCenter - text_width / 2, text_height - 3)

        painter.drawText(text_position, self.text)

    def set_text(self, text):
        self.text = text


class Indicator(QGraphicsItem):
    def __init__(self, parent):
        super().__init__(parent)
        if parent.timelineWidget:
            self.timelineWidget: TimeLineWidget = parent.timelineWidget
        self.pressed = False
        self.y = 15
        self.height = 10
        self.poly: QPolygonF = QPolygonF(
            [
                QPointF(-10, self.y),
                QPointF(10, self.y),
                QPointF(0, self.y + self.height),
            ]
        )
        self.line: QLine = QLine(0, self.y, 0, 10000)

        self.setAcceptHoverEvents(True)
        self.setAcceptDrops(True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)
        self.setZValue(101)

    def paint(self, painter, option, widget=...):
        painter.setPen(Qt.GlobalColor.black)
        painter.setBrush(Qt.GlobalColor.black)
        painter.drawLine(self.line)
        painter.drawPolygon(self.poly)

    def calculate_size(self):
        min_x: float = self.poly[0].x()
        max_x: float = self.poly[0].x()

        for i, point in enumerate(self.poly):
            if point.x() < min_x:
                min_x = point.x()
            if point.x() > max_x:
                max_x = point.x()

        return QSizeF(max_x - min_x, self.height)

    def boundingRect(self):
        size: QSizeF = self.calculate_size()
        return QRectF(-10, self.y, size.width(), size.height())

    def focusInEvent(self, event):
        self.pressed = True
        super().focusInEvent(event)
        self.update()

    def focusOutEvent(self, event):
        self.pressed = False
        super().focusOutEvent(event)
        self.update()

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        pos: QPointF = event.scenePos()
        if self.pressed:
            time = int(
                pos.x()
                * self.timelineWidget.duration
                / self.parentItem().rect().width()
            )

            # During creation of a new annotation
            if self.timelineWidget and self.timelineWidget.currentAnnotation:
                annotation = self.timelineWidget.currentAnnotation
                if time != annotation.get_time_from_bounding_interval(time):
                    # Stop player at the lower or upper bound when they
                    # are passed over
                    self.setPos(self.x(), 0)
                    return

            self.timelineWidget.player.set_position(time)

            if pos.x() < 0:
                self.setPos(0, 0)
            elif pos.x() > self.parentItem().rect().width():
                self.setPos(self.parentItem().rect().width(), 0)
            else:
                self.setPos(pos.x(), 0)

        self.update()


class TimelineScale(QGraphicsRectItem):

    FIXED_HEIGHT: float = 25.0

    def __init__(self, timeline_widget: TimeLineWidget):
        super().__init__()
        self.timelineWidget = timeline_widget
        self.timelineWidget.scene.addItem(self)
        self.indicator = Indicator(self)
        self.setRect(
            QRectF(0, 0, self.timelineWidget.scene.width(), self.FIXED_HEIGHT)
        )

    def paint(self, painter, option, widget=...):
        self._draw_rect(painter)

        if self.timelineWidget.duration != 0:
            self._draw_scale(painter)

    def update_rect(self):
        self.setRect(
            QRectF(0, 0, self.timelineWidget.scene.width(), self.FIXED_HEIGHT)
        )
        self.update()

    def _draw_rect(self, painter):
        """Draw the background rectangle of the timeline scale"""
        painter.setPen(Qt.GlobalColor.black)
        painter.setBrush(Qt.GlobalColor.lightGray)
        self.setRect(
            QRectF(0, 0, self.timelineWidget.scene.width(), self.FIXED_HEIGHT)
        )
        painter.drawRect(self.rect())

    def _draw_scale(self, painter):
        tl = TickLocator()
        min_gap = 0.05
        dur = self.timelineWidget.duration
        wid = self.timelineWidget.scene.width()
        font = painter.font()
        fm = QFontMetrics(font)
        loc = tl.find_locations(0, dur / 1000, wid, font, min_gap)
        # Calculate the height of the text
        font_height = painter.fontMetrics().height()
        line_height = 5
        y = self.rect().height()

        for p in loc:

            i = 1000 * (p[0] * wid / dur)

            # Calculate the position of the text
            text_width = fm.boundingRect(p[1]).width()
            text_position = QPointF(i - text_width / 2, font_height)

            # Draw the text
            painter.drawText(text_position, p[1])

            # Calculate the position of the line
            painter.drawLine(QPointF(i, y), QPointF(i, y - line_height))

    def mousePressEvent(self, event):
        return

    def mouseReleaseEvent(self, event):
        return


class Annotation(QGraphicsRectItem):
    DEFAULT_PEN_COLOR = QColor(0, 0, 0, 255)
    DEFAULT_BG_COLOR = QColor(255, 48, 48, 128)
    DEFAULT_FONT_COLOR = QColor(0, 0, 0, 255)
    PEN_WIDTH_ON_CURSOR = 3
    PEN_WIDTH_OFF_CURSOR = 1

    def __init__(
        self,
        timeline_widget: TimeLineWidget,
        timelineLine,
        startTime: int = None,
        endTime: int = None,
        lower_bound: int = None,
        upper_bound: int = None,
    ):
        """Initializes the Annotation widget"""
        super().__init__(timelineLine)
        self.brushColor = self.DEFAULT_BG_COLOR
        self.penColor = self.DEFAULT_PEN_COLOR
        self.penWidth = self.PEN_WIDTH_OFF_CURSOR
        self.fontColor = self.DEFAULT_FONT_COLOR
        self.group = None
        self.name = None
        self.timelineWidget = timeline_widget
        self.mfps = self.timelineWidget.player.mfps
        self.startTime = (
            startTime
            if startTime
            else timeline_widget.value - int(self.mfps / 2)
        )
        self.endTime = (
            endTime if endTime else timeline_widget.value + int(self.mfps / 2)
        )
        self.timeline_line: TimelineLine = timelineLine
        self.startXPosition = int(
            self.startTime
            * self.timelineWidget.scene.width()
            / self.timelineWidget.duration
        )
        self.endXPosition = int(
            self.endTime
            * self.timelineWidget.scene.width()
            / self.timelineWidget.duration
        )
        self.set_default_rect()
        self.selected = False
        self.startHandle: AnnotationHandle = None
        self.endHandle: AnnotationHandle = None

        self.setX(self.startXPosition)
        self.setY(TimelineLineLabel.FIXED_HEIGHT)
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.comment: str = ""

    @staticmethod
    def annotationDrawCanBeInitiate(annotations, value):
        """Check if the annotation can be initiated"""
        lower_bound = upper_bound = None
        valid = True

        # Loop through the annotations of the selected timeline line
        for a in annotations:
            if a.startTime <= value <= a.endTime:
                valid = False
                break
            if not lower_bound:
                if a.endTime < value:
                    lower_bound = a.endTime + int(a.mfps / 2)
            else:
                if a.endTime < value:
                    if lower_bound < a.endTime:
                        lower_bound = a.endTime + int(a.mfps / 2)
            if not upper_bound:
                if a.startTime > value:
                    upper_bound = a.startTime - int(a.mfps / 2)
            else:
                if a.startTime > value:
                    if upper_bound > a.startTime:
                        upper_bound = a.startTime - int(a.mfps / 2)
        return valid, lower_bound, upper_bound

    def set_default_rect(self):
        self.setRect(
            QRectF(
                0,
                0,
                self.endXPosition - self.startXPosition,
                TimelineLine.FIXED_HEIGHT - TimelineLineLabel.FIXED_HEIGHT,
            )
        )

    def mousePressEvent(self, event):
        return

    def mouseReleaseEvent(self, event):
        return

    def mouseDoubleClickEvent(self, event):
        if not self.timelineWidget.currentAnnotation:
            self.setSelected(True)
            self.calculateBounds()

    def focusOutEvent(self, event):
        self.setSelected(False)
        super().focusOutEvent(event)

    def contextMenuEvent(self, event):
        if not self.isSelected():
            super().contextMenuEvent(event)
            return
        can_merge_previous = False
        for annotation in self.timeline_line.annotations:
            if (
                annotation.endTime == self.startTime
                and self.name == annotation.name
            ):
                can_merge_previous = True
                break
        can_merge_next = False
        for annotation in self.timeline_line.annotations:
            if (
                self.endTime == annotation.startTime
                and self.name == annotation.name
            ):
                can_merge_next = True
                break
        menu = QMenu()
        menu.addAction("Delete annotation").triggered.connect(self.on_remove)
        menu.addAction("Change annotation label").triggered.connect(
            self.change_label
        )
        if can_merge_previous:
            menu.addAction("Merge with previous annotation").triggered.connect(
                self.merge_previous
            )
        if can_merge_next:
            menu.addAction("Merge with next annotation").triggered.connect(
                self.merge_next
            )
        menu.addAction("Comment annotation").triggered.connect(
            self.edit_comment
        )
        menu.exec(event.screenPos())

    def on_remove(self):
        answer = QMessageBox.question(
            self.timelineWidget,
            "Confirmation",
            "Do you want to remove the annotation?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if answer == QMessageBox.StandardButton.Yes:
            self.remove()

    def edit_comment(self):
        comment_dialog = AnnotationComment(self.comment)
        comment_dialog.exec()
        if comment_dialog.result() == QMessageBox.DialogCode.Accepted:
            self.comment = comment_dialog.get_text()

    def merge_previous(self):
        for annotation in self.timeline_line.annotations:
            if (
                self.startTime == annotation.endTime
                and self.name == annotation.name
            ):
                break
        self.startTime = annotation.startTime
        annotation.remove()
        self.update_rect()
        self.update()

    def merge_next(self):
        for annotation in self.timeline_line.annotations:
            if (
                self.endTime == annotation.startTime
                and self.name == annotation.name
            ):
                break
        self.endTime = annotation.endTime
        annotation.remove()
        self.update_rect()
        self.update()

    def change_label(self):
        events_dialog = ChooseEvent(
            self.timeline_line.groups,
            "Select an event for the current annotation:"
        )
        events_dialog.exec()
        if events_dialog.result() == QMessageBox.DialogCode.Accepted:
            i = events_dialog.get_chosen()
            g = self.timeline_line.groups[i]
            self.set_group(g)
            self.update()

    def remove(self):
        self.timelineWidget.scene.removeItem(self)
        if self in self.timeline_line.annotations:
            self.timeline_line.remove_annotation(self)
        if self.group:
            self.group.remove_annotation(self)
        del self

    def paint(self, painter, option, widget=...):
        # Draw the annotation rectangle
        self._draw_rect(painter)

        # Draw the name of the annotation in the annotation rectangle
        self._draw_name(painter)

        if self.isSelected():
            self.show_handles()
        else:
            self.hide_handles()

    def _draw_rect(self, painter):
        """Draw the annotation rectangle"""
        pen: QPen = QPen(self.penColor)
        pen.setWidth(self.penWidth)

        if self.isSelected():
            # Set border dotline if annotation is selected
            pen.setStyle(Qt.PenStyle.DotLine)
        painter.setPen(pen)
        painter.setBrush(self.brushColor)

        # Draw the rectangle
        painter.drawRect(self.rect())

    def _draw_name(self, painter):
        """Draws the name of the annotation"""
        if self.name:
            col = color_fg_from_bg(self.brushColor)
            painter.setPen(col)
            painter.setBrush(col)
            painter.drawText(
                self.rect(), Qt.AlignmentFlag.AlignCenter, self.name
            )

    def set_group(self, group=None):
        """Updates the group"""
        if group is None:
            self.group = None
            self.brushColor = self.DEFAULT_BG_COLOR
        else:
            self.group = group
            self.brushColor = group.color
            self.name = group.name
            self.setToolTip(self.name)
            if self.startHandle:
                self.startHandle.setBrush(group.color)
                self.endHandle.setBrush(group.color)

    def update_rect(self, new_rect: QRectF = None):
        new_rect = new_rect or self.timelineWidget.scene.sceneRect()
        # Calculate position to determine width
        self.startXPosition = (
            self.startTime * new_rect.width() / self.timelineWidget.duration
        )
        self.endXPosition = (
            self.endTime * new_rect.width() / self.timelineWidget.duration
        )
        self.setX(self.startXPosition)

        # Update the rectangle
        rect = self.rect()
        rect.setWidth(self.endXPosition - self.startXPosition)
        self.setRect(rect)

        if self.startHandle:
            self.startHandle.setX(self.rect().x())
            self.endHandle.setX(self.rect().width())

    def update_start_time(self, startTime: int):
        self.startTime = startTime
        self.update_rect()
        self.update()

    def update_end_time(self, endTime: int):
        """Updates the end time"""
        self.endTime = endTime
        self.update_rect()
        self.update()

    def update_selectable_flags(self):
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable)
        self.update()

    def create_handles(self):
        self.startHandle = AnnotationStartHandle(self)
        self.endHandle = AnnotationEndHandle(self)

    def ends_creation(self):
        """Ends the creation of the annotation"""
        self.update_selectable_flags()
        self.create_handles()

        # if startTime is greater than endTime then swap times
        if self.startTime > self.endTime:
            self.startTime, self.endTime = self.endTime, self.startTime
            self.update_rect()

        # Add this annotation to the annotation list of the timeline line
        self.timeline_line.add_annotation(self)

        self.update()

    def show_handles(self):
        if self.startHandle:
            self.startHandle.setVisible(True)
        if self.endHandle:
            self.endHandle.setVisible(True)

    def hide_handles(self):
        if self.startHandle:
            self.startHandle.setVisible(False)
        if self.endHandle:
            self.endHandle.setVisible(False)

    def calculateBounds(self):
        _, lower_bound, upper_bound = Annotation.annotationDrawCanBeInitiate(
            list(filter(lambda x: x != self, self.timeline_line.annotations)),
            self.startTime,
        )
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

    def get_time_from_bounding_interval(self, time) -> int:
        if self.lower_bound and time < self.lower_bound:
            time = self.lower_bound
        elif self.upper_bound and time > self.upper_bound:
            time = self.upper_bound
        return time


class AnnotationHandle(QGraphicsRectItem):
    def __init__(self, annotation: Annotation, value: int, x: float):
        super().__init__(annotation)
        self.annotation = annotation
        self.value = value

        self.setPen(self.annotation.penColor)
        self.setBrush(self.annotation.brushColor)
        self.setVisible(False)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsFocusable)
        self.setAcceptDrops(True)

        width = 9
        self._height = annotation.rect().height() / 2
        self.setRect(QRectF(-4.5, 0, width, self._height))

        self.setX(x)
        self.setY(self._height / 2)

    @abstractmethod
    def change_time(self, new_time):
        self.value = new_time

    def focusInEvent(self, event):
        self.annotation.setSelected(True)
        self.annotation.timelineWidget.player.set_position(self.value)
        super().focusInEvent(event)

    def focusOutEvent(self, event):
        self.annotation.setSelected(False)
        super().focusOutEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.setY(self._height / 2)

            # A la souris on déplace le X, il faut changer le temps
            time = int(
                event.scenePos().x()
                * self.annotation.timelineWidget.duration
                / self.annotation.timelineWidget.scene.width()
            )

            time = self.annotation.get_time_from_bounding_interval(time)

            self.annotation.timelineWidget.player.set_position(time)


class AnnotationStartHandle(AnnotationHandle):

    def __init__(self, annotation: Annotation):
        super().__init__(annotation, annotation.startTime, 0)

    def change_time(self, time):
        t = time - int(self.annotation.mfps / 2)
        super().change_time(t)
        self.annotation.update_start_time(t)


class AnnotationEndHandle(AnnotationHandle):
    def __init__(self, annotation: Annotation):
        super().__init__(
            annotation, annotation.endTime, annotation.rect().width()
        )

    def change_time(self, time):
        t = time + int(self.annotation.mfps / 2)
        super().change_time(t)
        self.annotation.update_end_time(t)


class AnnotationGroup:
    def __init__(
        self,
        id: int,
        name: str,
        color: QColor = None,
        timeline_line: TimelineLine = None,
    ):
        """Initializes the annotation group"""
        self.id = id
        self.name = name
        self.color = color
        self.timeline_line = timeline_line
        self.annotations = []

    def add_annotation(self, annotation: Annotation):
        annotation.name = self.name
        annotation.set_group(self)
        self.annotations.append(annotation)
        self.annotations.sort(key=lambda x: x.startTime)

    def remove_annotation(self, annotation: Annotation):
        annotation.name = None
        annotation.set_group(None)
        self.annotations.remove(annotation)


class AnnotationGroupDialog(QDialog):
    DEFAULT_COLOR = QColor(255, 255, 255)
    """Dialog to select or create a new annotation group"""

    def __init__(self, timeline_line: TimelineLine = None):
        super().__init__(timeline_line.timelineWidget)
        self.setWindowTitle("New annotation")

        self.color = self.DEFAULT_COLOR
        self.combo_box = QComboBox()
        self.labels = [x.name for x in timeline_line.groups]
        for group in timeline_line.groups:
            self.combo_box.addItem(group.name, group)
        self.combo_box.setEditable(True)

        self.label_2 = QLabel("New label")
        self.group_name_text = QLineEdit()

        self.button_color_2 = QPushButton("Color")
        self.button_color_2.clicked.connect(self.on_button_color_2_clicked)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)

        self.abort_button = QPushButton("Abort")
        self.abort_button.clicked.connect(self.abort)

        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.accept)

        # Create layout for contents
        layout = QHBoxLayout()
        layout.addWidget(self.combo_box)
        layout.addWidget(self.label_2)
        layout.addWidget(self.group_name_text)
        layout.addWidget(self.button_color_2)

        # Create layout for main buttons
        main_button_layout = QHBoxLayout()
        main_button_layout.addWidget(self.cancel_button)
        main_button_layout.addWidget(self.abort_button)
        main_button_layout.addWidget(self.save_button)

        main_layout = QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addLayout(main_button_layout)

        self.setLayout(main_layout)

        if timeline_line.groups:
            self.state = "choose"
        else:
            self.state = "create"

        self.set_visibility()

    def accept(self):
        if self.state == "choose" and (
            self.combo_box.currentText() not in self.labels
        ):
            self.state = "create"
            self.group_name_text.setText(self.combo_box.currentText())
            self.set_visibility()
            self.group_name_text.setFocus()
        else:
            super().accept()

    def abort(self):
        confirm_box = AnnotationConfirmMessageBox(self)
        if confirm_box.result() == QMessageBox.DialogCode.Accepted:
            self.done(AnnotationDialogCode.Aborted)

    def on_button_color_2_clicked(self):
        dialog = QColorDialog(self.color, self)
        dialog.exec()
        if dialog.result() == dialog.DialogCode.Accepted:
            self.color = dialog.currentColor()

    def set_visibility(self):
        if self.state == "choose":
            self.combo_box.setVisible(True)
            self.label_2.setVisible(False)
            self.group_name_text.setVisible(False)
            self.button_color_2.setVisible(False)
        else:
            self.combo_box.setVisible(False)
            self.label_2.setVisible(True)
            self.group_name_text.setVisible(True)
            self.button_color_2.setVisible(True)
        self.save_button.setDefault(True)


class AnnotationConfirmMessageBox(QMessageBox):
    def __init__(self, parent=None):
        super().__init__(
            QMessageBox.Icon.Warning,
            "Warning",
            "Are you sure to abort the creation of this annotation ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            parent,
        )

        self.button(QMessageBox.StandardButton.Yes).clicked.connect(self.accept)
        self.button(QMessageBox.StandardButton.No).clicked.connect(self.reject)
        self.exec()


class AnnotationDialogCode(IntEnum):
    Accepted: int = QDialog.DialogCode.Accepted  # 0
    Canceled: int = QDialog.DialogCode.Rejected  # 1
    Aborted: int = 2
