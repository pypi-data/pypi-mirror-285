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

import yaml
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

_log = logging.getLogger(__name__)


class SpinnerParameters(yaml.YAMLObject):
    yaml_tag: str = "!SpinnerParameters"
    _TRAIL_FADE_LIMIT: float = 1000.0
    _NUMBER_OF_LINES_MAX: int = 500
    _NUMBER_OF_LINES_MIN: int = 2

    def __init__(
        self,
        roundness: float = 100.0,
        trail_fade_percentage: float = 80.0,
        number_of_lines: int = 20,
        line_length: int = 10,
        line_width: int = 2,
        inner_radius: int = 10,
        revolutions_per_second: float = math.pi / 2,
        color: QColor = None,
        minimum_trail_opacity: float = math.pi,
        window_modality: Qt.WindowModality = Qt.WindowModality.NonModal,
        *,
        center_on_parent: bool = True,
        disable_parent_when_spinning: bool = False,
    ) -> None:
        self._limit_trail_fade_percentage: bool = True
        self._limit_number_of_lines: bool = True

        self._center_on_parent: bool = center_on_parent
        self._disable_parent_when_spinning: bool = disable_parent_when_spinning
        self._window_modality: Qt.WindowModality = window_modality
        self._color: QColor = color
        self._roundness: float = roundness
        self._minimum_trail_opacity: float = minimum_trail_opacity
        self._trail_fade_percentage: float = trail_fade_percentage
        self._revolutions_per_second: float = revolutions_per_second
        self._number_of_lines: int = number_of_lines
        self._line_length: int = line_length
        self._line_width: int = line_width
        self._inner_radius: int = inner_radius

        if self._color is None:
            self._color = QColor(0, 0, 0)

        ### Callback Holders

        self.revolutions_per_second_callback: object = None
        self.number_of_lines_callback: object = None
        self.line_length_callback: object = None
        self.line_width_callback: object = None
        self.inner_radius_callback: object = None

    # region Dunders

    # TODO: Test if PyYAML still works if this is written as a literal
    def __getstate__(self) -> dict:
        return dict(  # noqa: C408
            center_on_parent=self._center_on_parent,
            disable_parent_when_spinning=self._disable_parent_when_spinning,
            window_modality=self._window_modality,
            roundness=self._roundness,
            trail_fade_percentage=self._trail_fade_percentage,
            number_of_lines=self._number_of_lines,
            line_length=self._line_length,
            line_width=self._line_width,
            inner_radius=self._inner_radius,
            revolutions_per_second=self._revolutions_per_second,
            color=self._color,
            minimum_trail_opacity=self._minimum_trail_opacity,
            # modality=self.windowModality(),
        )

    # endregion

    # region Properties

    @property
    def center_on_parent(self) -> bool:
        return self._center_on_parent

    @center_on_parent.setter
    def center_on_parent(self, center: bool) -> None:
        self._center_on_parent = center

    @property
    def disable_parent_when_spinning(self) -> bool:
        return self._disable_parent_when_spinning

    @disable_parent_when_spinning.setter
    def disable_parent_when_spinning(self, disable_parent: bool) -> None:
        self._disable_parent_when_spinning = disable_parent

    @property
    def window_modality(self) -> Qt.WindowModality:
        return self._window_modality

    @window_modality.setter
    def window_modality(self, window_modality: Qt.WindowModality) -> None:
        self._window_modality = window_modality

    @property
    def color(self) -> QColor:
        """Return color of WaitingSpinner."""
        return self._color

    @color.setter
    def color(self, color: Qt.GlobalColor = Qt.GlobalColor.black) -> None:
        """Set color of WaitingSpinner."""
        self._color = QColor(color)

    @property
    def roundness(self) -> float:
        """Return roundness of WaitingSpinner."""
        return self._roundness

    @roundness.setter
    def roundness(self, roundness: float) -> None:
        """Set color of WaitingSpinner."""
        self._roundness = max(0.0, min(100.0, roundness))

    @property
    def minimum_trail_opacity(self) -> float:
        """Return minimum trail opacity of WaitingSpinner."""
        return self._minimum_trail_opacity

    @minimum_trail_opacity.setter
    def minimum_trail_opacity(self, minimum_trail_opacity: float) -> None:
        """Set minimum trail opacity of WaitingSpinner."""
        self._minimum_trail_opacity = minimum_trail_opacity

    @property
    def trail_fade_percentage(self) -> float:
        """Return trail fade percentage of WaitingSpinner."""
        return self._trail_fade_percentage

    @trail_fade_percentage.setter
    def trail_fade_percentage(self, trail: float) -> None:
        """Set trail fade percentage of WaitingSpinner."""
        if (
            self._limit_trail_fade_percentage
            and trail > self._TRAIL_FADE_LIMIT
        ):
            trail = 1000
        self._trail_fade_percentage = trail

    @property
    def revolutions_per_second(self) -> float:
        """Return revolutions per second of WaitingSpinner."""
        return self._revolutions_per_second

    @revolutions_per_second.setter
    def revolutions_per_second(self, revolutions_per_second: float) -> None:
        """Set revolutions per second of WaitingSpinner."""
        self._revolutions_per_second = revolutions_per_second

        if self.revolutions_per_second_callback is not None:
            self.revolutions_per_second_callback()

    @property
    def number_of_lines(self) -> int:
        """Return number of lines of WaitingSpinner."""
        return self._number_of_lines

    @number_of_lines.setter
    def number_of_lines(self, lines: int) -> None:
        """Set number of lines of WaitingSpinner."""
        if self._limit_number_of_lines and lines > self._NUMBER_OF_LINES_MAX:
            lines = 500

        if lines < self._NUMBER_OF_LINES_MIN:
            lines = 2

        self._number_of_lines = lines

        if self.number_of_lines_callback is not None:
            self.number_of_lines_callback()

    @property
    def line_length(self) -> int:
        """Return line length of WaitingSpinner."""
        return self._line_length

    @line_length.setter
    def line_length(self, length: int) -> None:
        """Set line length of WaitingSpinner."""
        self._line_length = length

        if self.line_length_callback is not None:
            self.line_length_callback()

    @property
    def line_width(self) -> int:
        """Return line width of WaitingSpinner."""
        return self._line_width

    @line_width.setter
    def line_width(self, width: int) -> None:
        """Set line width of WaitingSpinner."""
        self._line_width = width

        if self.line_width_callback is not None:
            self.line_width_callback()

    @property
    def inner_radius(self) -> int:
        """Return inner radius size of WaitingSpinner."""
        return self._inner_radius

    @inner_radius.setter
    def inner_radius(self, radius: int) -> None:
        """Set inner radius size of WaitingSpinner."""
        self._inner_radius = radius

        if self.inner_radius_callback is not None:
            self.inner_radius_callback()

    # endregion

    # region Methods

    def save(self, file_path: Union[pathlib.Path, str]) -> None:
        conf_path: pathlib.Path

        if isinstance(file_path, str):
            conf_path = pathlib.Path(file_path)
        else:
            conf_path = file_path

        try:
            with conf_path.open("w+") as f:
                yaml.dump(self, f)
        except FileNotFoundError as fnferr:
            _log.exception(fnferr, exc_info=True)
            raise
        except PermissionError as permerr:
            _log.exception(permerr, exc_info=True)
            raise
        except yaml.YAMLError as yamlerr:
            _log.exception(yamlerr, exc_info=True)
            raise

    # endregion


# region Module-Level Functions


def from_file(
    yaml_file: Union[pathlib.Path, str],
) -> Union[SpinnerParameters, None]:
    yaml_path: pathlib.Path

    if isinstance(yaml_file, str):
        yaml_path = pathlib.Path(yaml_file)
    else:
        yaml_path = yaml_file

    try:
        with yaml_path.open("rb") as f:
            # if errors show up, revert this to yaml.load(f,.......)
            return yaml.safe_load(f, Loader=parameters_loader(yaml.SafeLoader))
    except FileNotFoundError as nofilerr:
        _log.exception(nofilerr, exc_info=True)
        return None
    except PermissionError as permerr:
        _log.exception(permerr, exc_info=True)
        return None


# endregion

# region PyYAML


def window_modality_constructor(
    loader: yaml.Loader, node: yaml.nodes.Node
) -> Qt.WindowModality:
    try:
        return Qt.WindowModality[str(loader.construct_scalar(node))]
    except yaml.YAMLError as yamlerr:
        _log.exception(yamlerr, exc_info=True)
        return None
    except TypeError as typerr:
        _log.exception(typerr, exc_info=True)
        return None


def qcolor_constructor(loader: yaml.BaseLoader, node: yaml.Node) -> QColor:
    try:
        return QColor(int(loader.construct_scalar(node)))
    except TypeError as typerr:
        _log.exception(typerr, exc_info=True)
        return None
    except yaml.YAMLError as yamlerr:
        _log.exception(yamlerr, exc_info=True)
        return None


def spinner_constructor(
    loader: yaml.Loader, node: yaml.nodes.MappingNode
) -> SpinnerParameters:
    try:
        return SpinnerParameters(**loader.construct_mapping(node))
    except TypeError as typerr:
        _log.exception(typerr, exc_info=True)
        return None
    except yaml.YAMLError as yamlerr:
        _log.exception(yamlerr, exc_info=True)
        return None


def window_modality_representer(
    dumper: yaml.Dumper, modality: Qt.WindowModality
) -> yaml.Node:
    try:
        return dumper.represent_scalar("!window_modality", modality.name)
    except yaml.YAMLError as yamlerr:
        _log.exception(yamlerr, exc_info=True)
        return
    except TypeError as typerr:
        _log.exception(typerr, exc_info=True)
        return


def qcolor_representer(dumper: yaml.BaseDumper, color: QColor) -> yaml.Node:
    try:
        return dumper.represent_scalar("!qcolor", str(color.rgb()))
    except yaml.YAMLError as yamlerr:
        _log.exception(yamlerr, exc_info=True)
        return None
    except Exception as ex:
        _log.exception(ex, exc_info=True)
        return None


def parameters_loader(loader: yaml.Loader = None) -> None:
    if loader is None:
        loader = yaml.SafeLoader()

    loader.add_constructor("!SpinnerParameters", spinner_constructor)
    loader.add_constructor("!window_modality", window_modality_constructor)
    loader.add_constructor("!qcolor", qcolor_constructor)

    return loader


yaml.add_representer(Qt.WindowModality, window_modality_representer)
yaml.add_representer(QColor, qcolor_representer)


# endregion
