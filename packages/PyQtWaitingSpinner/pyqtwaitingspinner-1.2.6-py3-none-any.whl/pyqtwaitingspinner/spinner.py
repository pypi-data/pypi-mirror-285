"""
The MIT License (MIT)

Copyright (c) 2012-2014 Alexander Turkin
Copyright (c) 2014 William Hallatt
Copyright (c) 2015 Jacob Dawid
Copyright (c) 2016 Luca Weiss
Copyright (c) 2017 fbjorn
Copyright (c) 2024 Matthew Van Wyk

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import logging
import math
import pathlib
from typing import Union

from PyQt6 import QtGui
from PyQt6.QtCore import QRect, Qt, QTimer
from PyQt6.QtGui import QColor, QPainter, QPaintEvent
from PyQt6.QtWidgets import QWidget

from pyqtwaitingspinner.parameters import SpinnerParameters, from_file

_log = logging.getLogger(__name__)


# pylint: disable=too-many-instance-attributes,too-many-arguments
class WaitingSpinner(QWidget):
    """WaitingSpinner is a highly configurable, custom spinner widget."""

    def __init__(
        self,
        parent: QWidget = None,
        spinner_parameters: SpinnerParameters = None,
    ) -> None:
        self.parameters: SpinnerParameters = None

        self.initialize(parent, spinner_parameters)

    def paintEvent(self, _: QPaintEvent) -> None:  # noqa: N802
        """Paint the WaitingSpinner."""
        self._update_position()
        painter = QPainter(self)
        painter.setBrush(QtGui.QColorConstants.Transparent)
        painter.fillRect(self.rect(), QtGui.QColorConstants.Transparent)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        if self._current_counter >= self.parameters.number_of_lines:
            self._current_counter = 0

        painter.setPen(Qt.PenStyle.NoPen)
        for i in range(self.parameters.number_of_lines):
            painter.save()
            painter.translate(
                self.parameters.inner_radius + self.parameters.line_length,
                self.parameters.inner_radius + self.parameters.line_length,
            )
            rotate_angle = 360 * i / self.parameters.number_of_lines
            painter.rotate(rotate_angle)
            painter.translate(self.parameters.inner_radius, 0)
            distance = self._line_count_distance_from_primary(
                i, self._current_counter, self.parameters.number_of_lines
            )
            color = self._current_line_color(
                distance,
                self.parameters.number_of_lines,
                self.parameters.trail_fade_percentage,
                self.parameters.minimum_trail_opacity,
                self.parameters.color,
            )
            painter.setBrush(color)
            painter.drawRoundedRect(
                QRect(
                    0,
                    -self.parameters.line_width // 2,
                    self.parameters.line_length,
                    self.parameters.line_width,
                ),
                self.parameters.roundness,
                self.parameters.roundness,
                Qt.SizeMode.RelativeSize,
            )
            painter.restore()

    def initialize(
        self,
        parent: QWidget,
        spinner_parameters: SpinnerParameters = None,
    ) -> None:
        super().__init__(parent)

        self.parameters = spinner_parameters

        if self.parameters is None:
            self.parameters = SpinnerParameters()

        self.parameters.revolutions_per_second_callback = (
            self._revolutions_per_second_changed
        )
        self.parameters.number_of_lines_callback = (
            self._number_of_lines_changed
        )
        self.parameters.line_length_callback = self._line_length_changed
        self.parameters.line_width_callback = self._line_width_changed
        self.parameters.inner_radius_callback = self._inner_radius_changed

        self._current_counter: int = 0
        self._is_spinning: bool = False

        self._timer: QTimer = QTimer(self)
        self._timer.timeout.connect(self._rotate)
        self._update_size()
        self._update_timer()
        self.hide()

        self.setWindowModality(self.parameters.window_modality)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def load(self, conf_file: Union[pathlib.Path, str]) -> None:
        self.parameters = from_file(conf_file)

        self._update_size()
        self._update_position()
        self._update_timer()

    def save(self, conf_file: Union[pathlib.Path, str]) -> None:
        self.parameters.save(conf_file)

    def start(self) -> None:
        """Show and start spinning the WaitingSpinner."""
        self._update_position()
        self._is_spinning = True
        self.show()

        if (
            self.parentWidget()
            and self.parameters.disable_parent_when_spinning
        ):
            self.parentWidget().setEnabled(False)

        if not self._timer.isActive():
            self._timer.start()
            self._current_counter = 0

    def stop(self) -> None:
        """Hide and stop spinning the WaitingSpinner."""
        self._is_spinning = False
        self.hide()

        if (
            self.parentWidget()
            and self.parameters.disable_parent_when_spinning
        ):
            self.parentWidget().setEnabled(True)

        if self._timer.isActive():
            self._timer.stop()
            self._current_counter = 0

    @property
    def is_spinning(self) -> bool:
        """Return actual spinning status of WaitingSpinner."""
        return self._is_spinning

    def _rotate(self) -> None:
        """Rotate the WaitingSpinner."""
        self._current_counter += 1
        if self._current_counter >= self.parameters.number_of_lines:
            self._current_counter = 0
        self.update()

    def _update_size(self) -> None:
        """Update the size of the WaitingSpinner."""
        size = (self.parameters.inner_radius + self.parameters.line_length) * 2
        self.setFixedSize(size, size)

    def _update_timer(self) -> None:
        """Update the spinning speed of the WaitingSpinner."""
        self._timer.setInterval(
            int(
                1000
                / (
                    self.parameters.number_of_lines
                    * self.parameters.revolutions_per_second
                )
            )
        )

    def _update_position(self) -> None:
        """Center WaitingSpinner on parent widget."""
        if self.parentWidget() and self.parameters.center_on_parent:
            self.move(
                (self.parentWidget().width() - self.width()) // 2,
                (self.parentWidget().height() - self.height()) // 2,
            )

    @staticmethod
    def _line_count_distance_from_primary(
        current: int, primary: int, total_nr_of_lines: int
    ) -> int:
        """Return the amount of lines from _current_counter."""
        distance = primary - current
        if distance < 0:
            distance += total_nr_of_lines
        return distance

    @staticmethod
    def _current_line_color(
        count_distance: int,
        total_nr_of_lines: int,
        trail_fade_perc: float,
        min_opacity: float,
        color_input: QColor,
    ) -> QColor:
        """Returns the current color for the WaitingSpinner."""
        color = QColor(color_input)
        if count_distance == 0:
            return color
        min_alpha_f = min_opacity / 100.0
        distance_threshold = int(
            math.ceil((total_nr_of_lines - 1) * trail_fade_perc / 100.0)
        )
        if count_distance > distance_threshold:
            color.setAlphaF(min_alpha_f)
        else:
            alpha_diff = color.alphaF() - min_alpha_f
            gradient = alpha_diff / float(distance_threshold + 1)
            result_alpha = color.alphaF() - gradient * count_distance
            # If alpha is out of bounds, clip it.
            result_alpha = min(1.0, max(0.0, result_alpha))
            color.setAlphaF(result_alpha)
        return color

    # region SpinnerParameters Callbacks

    def _revolutions_per_second_changed(self) -> None:
        self._update_timer()

    def _number_of_lines_changed(self) -> None:
        self._current_counter = 0
        self._update_timer()

    def _line_length_changed(self) -> None:
        self._update_size()

    def _line_width_changed(self) -> None:
        self._update_size()

    def _inner_radius_changed(self) -> None:
        self._update_size()

    # endregion
