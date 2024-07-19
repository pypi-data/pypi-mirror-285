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
import sys
import webbrowser
from random import random

from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QColor, QIcon
from PyQt6.QtWidgets import (
    QApplication,
    QCheckBox,
    QColorDialog,
    QDialog,
    QDoubleSpinBox,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from pyqtwaitingspinner import _creds

# from PyQt6.QtGui import QClipboard
from pyqtwaitingspinner.parameters import SpinnerParameters
from pyqtwaitingspinner.spinner import WaitingSpinner

_log: logging.Logger = logging.getLogger(__name__)


# pylint: disable=too-many-instance-attributes,too-many-statements
class SpinnerConfigurator(QWidget):
    sb_roundness = None
    sb_opacity = None
    sb_fadeperc = None
    sb_lines = None
    sb_line_length = None
    sb_line_width = None
    sb_inner_radius = None
    sb_rev_s = None

    btn_start = None
    btn_stop = None
    btn_pick_color = None

    spinner = None
    # spinner_container_size_policy: QSizePolicy = None

    default_bg_color = QColor("#f0f0f0")

    _img_dir = pathlib.Path(__file__).parent / pathlib.Path("img/")

    ICON_COLOR_PICKER: str = "color-picker-transparent.16.png"
    ICON_ABOUT: str = "question.16.png"
    ICON_DEFAULT_COLOR: str = "color-picker-default.16.png"

    __the_missing_spinner: str = """Yeah, you're editing the spinner, supposedly, otherwise why
        would you be trying to pick a color, right? And yet, I'm
        told that there is no spinner.
        Hmm... Strange indeed."""  # noqa: E501

    def __init__(self) -> None:
        super().__init__()
        self.init_ui()

    def init_ui(self) -> None:
        """Initialize ui."""
        grid = QGridLayout()
        groupbox1 = QGroupBox()
        groupbox1_layout = QHBoxLayout()
        groupbox2 = QGroupBox()
        groupbox2_layout = QGridLayout()
        button_hbox = QHBoxLayout()
        fadeperc_max = 9999
        lines_max = 9999

        groupbox1_layout.setContentsMargins(0, 0, 0, 5)

        _color_picker_icon_path = str(
            self._img_dir / pathlib.Path(self.ICON_COLOR_PICKER)
        )
        _question_icon_path = str(
            self._img_dir / pathlib.Path(self.ICON_ABOUT)
        )
        _default_color_icon_path = str(
            self._img_dir / pathlib.Path(self.ICON_DEFAULT_COLOR)
        )
        self._icon_color_picker = QIcon(_color_picker_icon_path)
        self._icon_about = QIcon(_question_icon_path)
        self._icon_default_color = QIcon(_default_color_icon_path)

        self.setLayout(grid)
        self.setWindowTitle("PyQtWaitingSpinner Configurator")
        self.setWindowFlags(Qt.WindowType.Dialog)

        # SPINNER
        self.spinner_container = QWidget(self)
        # self.spinner_container.setSizePolicy(
        #     QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum
        # )
        self.tool_layout = QVBoxLayout(self.spinner_container)
        self.spinner = WaitingSpinner(
            self.spinner_container, SpinnerParameters()
        )
        self.spinner_container.setStyleSheet(
            f"background-color:{self._get_color_str()};"
        )

        if self.spinner.parameters._limit_trail_fade_percentage:
            fadeperc_max = self.spinner.parameters._TRAIL_FADE_LIMIT
        if self.spinner.parameters._limit_number_of_lines:
            lines_max = self.spinner.parameters._NUMBER_OF_LINES_MAX

        # QFileDialog
        self.file_dialog: QFileDialog = QFileDialog(self, Qt.WindowType.Dialog)

        # Spinboxes
        self.sb_roundness = QDoubleSpinBox()
        self.sb_opacity = QDoubleSpinBox()
        self.sb_fadeperc = QDoubleSpinBox()
        self.sb_lines = QSpinBox()
        self.sb_line_length = QSpinBox()
        self.sb_line_width = QSpinBox()
        self.sb_inner_radius = QSpinBox()
        self.sb_rev_s = QDoubleSpinBox()

        # set spinbox default values
        # values moved to _set_widget_values. Only ranges here!
        ## self.sb_roundness.setRange(0, 9999)
        self.sb_roundness.setRange(0, 100)
        self.sb_opacity.setRange(0, 100)
        # self.sb_fadeperc.setRange(0, 9999)
        self.sb_fadeperc.setRange(0, fadeperc_max)
        self.sb_lines.setRange(1, lines_max)
        self.sb_line_length.setRange(0, 9999)
        self.sb_line_width.setRange(0, 9999)
        self.sb_inner_radius.setRange(0, 9999)
        self.sb_rev_s.setRange(0.1, 9999)

        # Buttons
        self.btn_start = QPushButton("Start")
        self.btn_stop = QPushButton("Stop")
        self.btn_pick_color = QPushButton("Pick Color")
        self.btn_randomize = QPushButton("Randomize")
        self.btn_show_init = QPushButton("Show Init Args")
        self.btn_load: QPushButton = QPushButton("Load")
        self.btn_save: QPushButton = QPushButton("Save")
        self.tbtn_bg_color: QToolButton = QToolButton(self.spinner_container)
        self.tbtn_bg_default: QToolButton = QToolButton(self.spinner_container)
        self.tbtn_about: QToolButton = QToolButton()

        # CheckBoxes
        self.chk_center_parent: QCheckBox = QCheckBox()
        self.chk_disable_parent: QCheckBox = QCheckBox()

        # CheckBox Properties
        self.chk_center_parent.setText("Center On Parent")
        self.chk_center_parent.setText("center_parent")
        self.chk_disable_parent.setText("Disable Parent")
        self.chk_disable_parent.setToolTip("disable_parent_when_spinning")

        self._set_widget_values()

        # Connects
        self.sb_roundness.valueChanged.connect(
            lambda x: setattr(self.spinner.parameters, "roundness", x)
        )
        self.sb_opacity.valueChanged.connect(
            lambda x: setattr(
                self.spinner.parameters, "minimum_trail_opacity", x
            )
        )
        self.sb_fadeperc.valueChanged.connect(
            lambda x: setattr(
                self.spinner.parameters, "trail_fade_percentage", x
            )
        )
        self.sb_lines.valueChanged.connect(
            lambda x: setattr(self.spinner.parameters, "number_of_lines", x)
        )
        self.sb_line_length.valueChanged.connect(
            lambda x: setattr(self.spinner.parameters, "line_length", x)
        )
        self.sb_line_width.valueChanged.connect(
            lambda x: setattr(self.spinner.parameters, "line_width", x)
        )
        self.sb_inner_radius.valueChanged.connect(
            lambda x: setattr(self.spinner.parameters, "inner_radius", x)
        )
        self.sb_rev_s.valueChanged.connect(
            lambda x: setattr(
                self.spinner.parameters, "revolutions_per_second", x
            )
        )

        self.btn_start.clicked.connect(self.spinner.start)
        self.btn_stop.clicked.connect(self.spinner.stop)
        self.btn_pick_color.clicked.connect(self.show_color_picker)
        self.btn_randomize.clicked.connect(self._randomize)
        self.btn_show_init.clicked.connect(self.show_init_args)
        self.btn_load.clicked.connect(self.btn_load_clicked)
        self.btn_save.clicked.connect(self.btn_save_clicked)
        self.tbtn_bg_color.clicked.connect(self.tbtn_bg_color_clicked)
        self.tbtn_bg_default.clicked.connect(self.tbtn_bg_default_clicked)
        self.tbtn_about.clicked.connect(self.tbtn_about_clicked)

        self.tbtn_bg_color.setStyleSheet(
            f"background-color: {self._get_color_str()};"
        )
        self.tbtn_bg_color.setIcon(self._icon_color_picker)
        self.tbtn_bg_color.setToolTip("Change Background Color")
        self.tbtn_bg_color.setSizePolicy(
            QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum
        )
        self.tbtn_bg_default.setStyleSheet(
            f"background-color: {self._get_color_str()}"
        )
        self.tbtn_bg_default.setIcon(self._icon_default_color)
        self.tbtn_bg_default.setToolTip("Default Background Color")
        self.tbtn_bg_default.setSizePolicy(
            QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum
        )
        self.tbtn_about.setIcon(self._icon_about)
        self.tbtn_about.setToolTip("About")
        self.tbtn_about.setSizePolicy(
            QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum
        )
        self.tbtn_about.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        self.tool_layout.setContentsMargins(0, 2, 2, 0)
        self.tool_layout.addWidget(self.tbtn_bg_color)
        self.tool_layout.addWidget(self.tbtn_bg_default)
        self.tool_layout.addStretch(10)
        self.tool_layout.setAlignment(
            self.tbtn_bg_color,
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop,
        )
        self.tool_layout.setAlignment(
            self.tbtn_bg_default,
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop,
        )

        self.chk_center_parent.checkStateChanged.connect(
            lambda x: setattr(
                self.spinner.parameters,
                "center_on_parent",
                x == Qt.CheckState.Checked,
            )
        )
        self.chk_disable_parent.checkStateChanged.connect(
            lambda x: setattr(
                self.spinner.parameters,
                "disable_parent_when_spinning",
                x == Qt.CheckState.Checked,
            )
        )

        # QLabels
        lbl_roundness: QLabel = QLabel("Roundness:")
        lbl_opacity: QLabel = QLabel("Opacity:")
        lbl_fadeperc: QLabel = QLabel("Fade Perc:")
        lbl_lines: QLabel = QLabel("Lines:")
        lbl_line_length: QLabel = QLabel("Line Length:")
        lbl_line_width: QLabel = QLabel("Line Width:")
        lbl_inner_radius: QLabel = QLabel("Inner Radius:")
        lbl_rev_s: QLabel = QLabel("Rev/s:")

        lbl_roundness.setToolTip("roundess")
        lbl_opacity.setToolTip("minimum_trail_opacity")
        lbl_fadeperc.setToolTip("trail_fade_percentage")
        lbl_lines.setToolTip("number_of_lines")
        lbl_line_length.setToolTip("line_length")
        lbl_line_width.setToolTip("line_width")
        lbl_inner_radius.setToolTip("inner_radius")
        lbl_rev_s.setToolTip("revolutions_per_second")

        # Layout adds
        groupbox1_layout.addWidget(self.spinner_container)
        groupbox1.setLayout(groupbox1_layout)

        # groupbox2_layout.addWidget(QLabel("Roundness:"), *(1, 1))
        groupbox2_layout.addWidget(lbl_roundness, *(1, 1))
        groupbox2_layout.addWidget(self.sb_roundness, *(1, 2))
        groupbox2_layout.addWidget(lbl_opacity, *(2, 1))
        groupbox2_layout.addWidget(self.sb_opacity, *(2, 2))
        groupbox2_layout.addWidget(lbl_fadeperc, *(3, 1))
        groupbox2_layout.addWidget(self.sb_fadeperc, *(3, 2))
        groupbox2_layout.addWidget(lbl_lines, *(4, 1))
        groupbox2_layout.addWidget(self.sb_lines, *(4, 2))
        groupbox2_layout.addWidget(lbl_line_length, *(5, 1))
        groupbox2_layout.addWidget(self.sb_line_length, *(5, 2))
        groupbox2_layout.addWidget(lbl_line_width, *(6, 1))
        groupbox2_layout.addWidget(self.sb_line_width, *(6, 2))
        groupbox2_layout.addWidget(lbl_inner_radius, *(7, 1))
        groupbox2_layout.addWidget(self.sb_inner_radius, *(7, 2))
        groupbox2_layout.addWidget(lbl_rev_s, *(8, 1))
        groupbox2_layout.addWidget(self.sb_rev_s, *(8, 2))
        groupbox2_layout.addWidget(self.chk_center_parent, *(9, 1))
        groupbox2_layout.addWidget(self.chk_disable_parent, *(10, 1))

        groupbox2.setLayout(groupbox2_layout)

        button_hbox.addWidget(self.btn_start)
        button_hbox.addWidget(self.btn_stop)
        button_hbox.addWidget(self.btn_pick_color)
        button_hbox.addWidget(self.btn_randomize)
        button_hbox.addWidget(self.btn_show_init)
        button_hbox.addWidget(self.btn_load)
        button_hbox.addWidget(self.btn_save)

        grid.addWidget(groupbox1, *(1, 1))
        grid.addWidget(groupbox2, *(1, 2))
        grid.addLayout(button_hbox, *(2, 1))
        grid.addWidget(self.tbtn_about, *(2, 2))

        self.spinner.start()

    @pyqtSlot(name="randomize")
    def _randomize(self) -> None:
        self.sb_roundness.setValue(random() * 1000)  # noqa: S311
        self.sb_opacity.setValue(random() * 50)  # noqa: S311
        self.sb_fadeperc.setValue(random() * 100)  # noqa: S311
        self.sb_lines.setValue(math.floor(random() * 150))  # noqa: S311
        self.sb_line_length.setValue(math.floor(10 + random() * 20))  # noqa: S311
        self.sb_line_width.setValue(math.floor(random() * 30))  # noqa: S311
        self.sb_inner_radius.setValue(math.floor(random() * 30))  # noqa: S311
        self.sb_rev_s.setValue(random())  # noqa: S311

    @pyqtSlot(name="show_color_picker")
    def show_color_picker(self) -> None:
        """Set the color for the spinner."""
        if self.spinner is None:
            show_message_box(
                "Where'd dat spinner get to?",
                self.__the_missing_spinner,
                QMessageBox.StandardButton.No,
            )
        self.spinner.parameters.color = QColorDialog.getColor()

    @pyqtSlot(name="show_init_args")
    def show_init_args(self) -> None:
        """Display used arguments."""
        if self.spinner is None:
            show_message_box(
                "Where'd dat spinner get to?",
                self.__the_missing_spinner,
                QMessageBox.StandardButton.No,
            )
        text = (
            f"SpinnerParameters(\n    "
            f"roundness={self.spinner.parameters.roundness},\n    "
            "trail_fade_percentage="
            f"{self.spinner.parameters.trail_fade_percentage},\n    "
            f"number_of_lines={self.spinner.parameters.number_of_lines},\n    "
            f"line_length={self.spinner.parameters.line_length},\n    "
            f"line_width={self.spinner.parameters.line_width},\n    "
            f"inner_radius={self.spinner.parameters.inner_radius},\n    "
            "revolutions_per_second="
            f"{round(self.spinner.parameters.revolutions_per_second, 2)}"
            ",\n    "
            f"color=QColor{self.spinner.parameters.color.getRgb()[:3]},\n    "
            "minimum_trail_opacity="
            f"{round(self.spinner.parameters.minimum_trail_opacity, 2)},\n    "
            "center_on_parent="
            f"{self.spinner.parameters.center_on_parent},\n    "
            "disable_parent_when_spinning="
            f"{self.spinner.parameters.disable_parent_when_spinning},\n)"
        )
        msg_box = QMessageBox()
        msg_box.setText(text)
        msg_box.setWindowTitle("Text was copied to clipboard")
        clipboard = QApplication.clipboard()
        clipboard.clear(mode=clipboard.Mode.Clipboard)
        clipboard.setText(text, mode=clipboard.Mode.Clipboard)
        print(text)  # noqa: T201
        msg_box.exec()

    @pyqtSlot(name="_icobtn_clicked")
    def _icobtn_clicked(self, checked: bool, icobtn: str) -> None:  # noqa: FBT001, ARG002
        url: str = ""

        if icobtn == "about":
            url = _creds.url_ico_about
        elif icobtn == "picker":
            url = _creds.url_ico_picker
        elif icobtn == "default":
            url = _creds.url_ico_default
        else:
            return

        webbrowser.open(url)

    @pyqtSlot(name="btn_load_clicked")
    def btn_load_clicked(self) -> None:
        self.file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
        self.file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        self.file_dialog.setDirectory(str(pathlib.Path("~").expanduser()))
        self.file_dialog.setViewMode(QFileDialog.ViewMode.List)
        # self.file_dialog.setDirectory(str(pathlib.Path(__file__).parent))
        # self.file_dialog.setDirectory(str(pathlib.Path.cwd()))
        self.file_dialog.setNameFilters(["*.yaml", "*.yml"])

        if self.file_dialog.exec() == QFileDialog.DialogCode.Accepted:
            # print(f"Selected File: {self.file_dialog.selectedFiles()[0]}")
            errmsg: str = ""
            file: str = self.file_dialog.selectedFiles()[0]
            fail: bool = False

            try:
                self.spinner.load(file)
            except FileNotFoundError:
                errmsg = "File Not Found"
                fail = True
            except Exception as ex:
                errmsg = "An Exception Occurred!"
                fail = True
                _log.exception(ex, exc_info=True)

            if fail:
                msg_box: QMessageBox = QMessageBox(text=errmsg)
                msg_box.exec()

            self._set_widget_values()

    @pyqtSlot(name="tbtn_about_clicked")
    def tbtn_about_clicked(self) -> None:
        # about_dialog: QWidget = QWidget(None, Qt.WindowType.Dialog)
        about_dialog: QDialog = QDialog(None, Qt.WindowType.Dialog)
        about_layout: QVBoxLayout = QVBoxLayout(about_dialog)
        lbl_credits: QLabel = QLabel()
        lbl_icons: QLabel = QLabel()
        lbl_credits_msg: QLabel = QLabel()
        lbl_icons_msg: QLabel = QLabel()
        hlay_ico_btn: QHBoxLayout = QHBoxLayout()
        icobtn_about: QPushButton = QPushButton()
        icobtn_picker: QPushButton = QPushButton()
        icobtn_default: QPushButton = QPushButton()

        lbl_credits.setText("Credits")
        lbl_icons.setText("Icons")

        lbl_credits.setSizePolicy(
            QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum
        )
        lbl_icons.setSizePolicy(
            QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum
        )

        lbl_credits.setAlignment(
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter
        )
        lbl_icons.setAlignment(
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter
        )

        lbl_credits_msg.setTextFormat(Qt.TextFormat.RichText)
        lbl_icons_msg.setTextFormat(Qt.TextFormat.RichText)

        lbl_credits_msg.setText(_creds.msg_credits)
        lbl_icons_msg.setText(_creds.msg_icons)

        icobtn_about.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )
        icobtn_picker.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )
        icobtn_default.setSizePolicy(
            QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed
        )

        icobtn_about.setFixedSize(16, 16)
        icobtn_picker.setFixedSize(16, 16)
        icobtn_default.setFixedSize(16, 16)

        icobtn_about.setFlat(True)
        icobtn_picker.setFlat(True)
        icobtn_default.setFlat(True)

        icobtn_about.setIcon(self._icon_about)
        icobtn_picker.setIcon(self._icon_color_picker)
        icobtn_default.setIcon(self._icon_default_color)

        icobtn_about.setToolTip("Yusuke-Kamiyamane-Fugue-Question.16.png")
        icobtn_picker.setToolTip(
            "Yusuke-Kamiyamane-Fugue-Ui-color-picker-transparent.16.png"
        )
        icobtn_default.setToolTip(
            "Yusuke-Kamiyamane-Fugue-Ui-color-picker-default.16.png"
        )

        icobtn_about.clicked.connect(
            lambda checked="", icobtn="about": self._icobtn_clicked(
                checked, icobtn
            )
        )
        icobtn_picker.clicked.connect(
            lambda checked="", icobtn="picker": self._icobtn_clicked(
                checked, icobtn
            )
        )
        icobtn_default.clicked.connect(
            lambda checked="", icobtn="default": self._icobtn_clicked(
                checked, icobtn
            )
        )

        hlay_ico_btn.addWidget(icobtn_about)
        hlay_ico_btn.addWidget(icobtn_picker)
        hlay_ico_btn.addWidget(icobtn_default)
        hlay_ico_btn.setAlignment(Qt.AlignmentFlag.AlignCenter)

        about_dialog.setLayout(about_layout)
        about_layout.addWidget(lbl_credits)
        about_layout.addWidget(lbl_credits_msg)
        about_layout.addWidget(lbl_icons)
        about_layout.addLayout(hlay_ico_btn)
        about_layout.addWidget(lbl_icons_msg)
        about_dialog.setWindowTitle("About")
        about_dialog.setWindowModality(Qt.WindowModality.ApplicationModal)

        about_dialog.exec()

    @pyqtSlot(name="btn_save_clicked")
    def btn_save_clicked(self) -> None:
        self.file_dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        # self.file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)  # ?
        self.file_dialog.setViewMode(QFileDialog.ViewMode.List)
        self.file_dialog.setDirectory(str(pathlib.Path("~").expanduser()))
        self.file_dialog.setNameFilter("*.yaml")

        if self.file_dialog.exec() == QFileDialog.DialogCode.Accepted:
            file: str = self.file_dialog.selectedFiles()[0]
            errmsg: str = ""
            fail: bool = False

            try:
                self.spinner.parameters.save(file)
            except Exception as ex:
                errmsg = "An Exeption Occurred"
                fail = True
                _log.exception(ex, exc_info=True)

            if fail:
                msg_box: QMessageBox = QMessageBox(text=errmsg)
                msg_box.exec()

    @pyqtSlot(name="tbtn_bg_color_clicked")
    def tbtn_bg_color_clicked(self) -> None:
        color = QColorDialog.getColor()

        if QColor.isValid(color):
            self._set_spinner_background(color)

    @pyqtSlot(name="tbtn_bg_default_clicked")
    def tbtn_bg_default_clicked(self) -> None:
        self._set_spinner_background()

    def _get_color_str(self, color: QColor = None) -> str:
        if color is None:
            color = self.default_bg_color

        return f"#{color.rgb():x}"

    def _set_spinner_background(self, color: QColor = None) -> None:
        if color is None:
            color = QColor(self.default_bg_color)

        self.spinner_container.setStyleSheet(
            f"background-color:{self._get_color_str(color)}"
        )
        self.tbtn_bg_color.setStyleSheet(
            f"background-color:{self._get_color_str()}"
        )

    def _set_widget_values(self) -> None:
        self.sb_roundness.setValue(self.spinner.parameters.roundness)
        self.sb_opacity.setValue(self.spinner.parameters.minimum_trail_opacity)
        self.sb_fadeperc.setValue(
            self.spinner.parameters.trail_fade_percentage
        )
        self.sb_lines.setValue(self.spinner.parameters.number_of_lines)
        self.sb_line_length.setValue(self.spinner.parameters.line_length)
        self.sb_line_width.setValue(self.spinner.parameters.line_width)
        self.sb_inner_radius.setValue(self.spinner.parameters.inner_radius)
        self.sb_rev_s.setValue(self.spinner.parameters.revolutions_per_second)
        self.chk_center_parent.setChecked(
            self.spinner.parameters.center_on_parent
        )
        self.chk_disable_parent.setChecked(
            self.spinner.parameters.disable_parent_when_spinning
        )


def show_message_box(
    title: str,
    msg: str,
    std_btn: QMessageBox.StandardButton = QMessageBox.StandardButton.Ok,
) -> int | QMessageBox.StandardButton:
    qmsg_box: QMessageBox = QMessageBox()
    qmsg_box.setWindowTitle(title)
    qmsg_box.setText(msg)
    qmsg_box.setStandardButtons(std_btn)

    return qmsg_box.exec()


def main():
    app = QApplication(sys.argv)
    configurator = SpinnerConfigurator()
    # sys.exit(app.exec())
    configurator.show()
    app.exec()


if __name__ == "__main__":
    main()
