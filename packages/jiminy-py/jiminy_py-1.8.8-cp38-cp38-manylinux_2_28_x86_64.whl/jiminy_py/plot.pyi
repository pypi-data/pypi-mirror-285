import jiminy_py.core as jiminy
import numpy as np
from .core import ContactSensor as ContactSensor, EffortSensor as EffortSensor, EncoderSensor as EncoderSensor, ForceSensor as ForceSensor, ImuSensor as ImuSensor
from .log import build_robot_from_log as build_robot_from_log, extract_variables_from_log as extract_variables_from_log, read_log as read_log
from .viewer import interactive_mode as interactive_mode
from _typeshed import Incomplete
from dataclasses import dataclass
from matplotlib.artist import Artist as Artist
from matplotlib.axes import Axes
from matplotlib.backend_bases import Event as Event
from matplotlib.legend import Legend as Legend
from matplotlib.widgets import Button
from typing import Any, Callable
from weakref import WeakKeyDictionary

SENSORS_FIELDS: dict[type[jiminy.AbstractSensor], list[str] | dict[str, list[str]]]

class _ButtonBlit(Button): ...

@dataclass
class TabData:
    axes: list[Axes]
    legend_data: tuple[list[Artist], list[str]]
    button: _ButtonBlit
    button_axcut: Axes
    nav_stack: list[WeakKeyDictionary]
    nav_pos: int
    def __init__(self, axes, legend_data, button, button_axcut, nav_stack, nav_pos) -> None: ...

class TabbedFigure:
    sync_tabs: Incomplete
    offscreen: Incomplete
    figure: Incomplete
    legend: Incomplete
    ref_ax: Incomplete
    tabs_data: Incomplete
    tab_active: Incomplete
    bbox_inches: Incomplete
    subfigs: Incomplete
    def __init__(self, sync_tabs: bool = False, window_title: str = 'jiminy', offscreen: bool = False, **kwargs: Any) -> None: ...
    def close(self) -> None: ...
    def __del__(self) -> None: ...
    def adjust_layout(self, event: Event | None = None, *, refresh_canvas: bool = False) -> None: ...
    def refresh(self) -> None: ...
    def add_tab(self, tab_name: str, time: np.ndarray, data: np.ndarray | dict[str, dict[str, np.ndarray] | np.ndarray], plot_method: Callable[..., Any] | str | None = None, *, refresh_canvas: bool = True, **kwargs: Any) -> None: ...
    def select_active_tab(self, tab_name: str) -> None: ...
    def remove_tab(self, tab_name: str, *, refresh_canvas: bool = True) -> None: ...
    def clear(self) -> None: ...
    def save_tab(self, pdf_path: str) -> None: ...
    def save_all_tabs(self, pdf_path: str) -> None: ...
    @classmethod
    def plot(cls, time: np.ndarray, tabs_data: dict[str, np.ndarray | dict[str, dict[str, np.ndarray] | np.ndarray]], pdf_path: str | None = None, **kwargs: Any) -> TabbedFigure: ...

def plot_log(log_data: dict[str, Any], robot: jiminy.Robot | None = None, enable_flexiblity_data: bool = False, block: bool | None = None, **kwargs: Any) -> TabbedFigure: ...
def plot_log_interactive() -> None: ...
