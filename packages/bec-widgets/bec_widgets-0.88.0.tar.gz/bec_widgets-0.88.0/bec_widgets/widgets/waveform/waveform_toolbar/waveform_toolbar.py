import os

from qtpy.QtCore import QSize
from qtpy.QtGui import QAction, QIcon

import bec_widgets
from bec_widgets.qt_utils.toolbar import ToolBarAction

MODULE_PATH = os.path.dirname(bec_widgets.__file__)


class SaveAction(ToolBarAction):
    def add_to_toolbar(self, toolbar, target):
        icon = QIcon()
        icon.addFile(
            os.path.join(MODULE_PATH, "assets", "toolbar_icons", "save.svg"), size=QSize(20, 20)
        )
        self.action = QAction(icon, "Open Export Dialog", target)
        toolbar.addAction(self.action)


class MatplotlibAction(ToolBarAction):
    def add_to_toolbar(self, toolbar, target):
        icon = QIcon()
        icon.addFile(
            os.path.join(MODULE_PATH, "assets", "toolbar_icons", "photo_library.svg"),
            size=QSize(20, 20),
        )
        self.action = QAction(icon, "Open Matplotlib Plot", target)
        toolbar.addAction(self.action)


class DragModeAction(ToolBarAction):
    def add_to_toolbar(self, toolbar, target):
        icon = QIcon()
        icon.addFile(
            os.path.join(MODULE_PATH, "assets", "toolbar_icons", "drag_pan_mode.svg"),
            size=QSize(20, 20),
        )
        self.action = QAction(icon, "Drag Mouse Mode", target)
        self.action.setCheckable(True)
        toolbar.addAction(self.action)


class RectangeModeAction(ToolBarAction):
    def add_to_toolbar(self, toolbar, target):
        icon = QIcon()
        icon.addFile(
            os.path.join(MODULE_PATH, "assets", "toolbar_icons", "rectangle_mode.svg"),
            size=QSize(20, 20),
        )
        self.action = QAction(icon, "Rectangle Zoom Mode", target)
        self.action.setCheckable(True)
        toolbar.addAction(self.action)


class AutoRangeAction(ToolBarAction):
    def add_to_toolbar(self, toolbar, target):
        icon = QIcon()
        icon.addFile(
            os.path.join(MODULE_PATH, "assets", "toolbar_icons", "auto_range.svg"),
            size=QSize(20, 20),
        )
        self.action = QAction(icon, "Autorange Plot", target)
        toolbar.addAction(self.action)


class CurveAction(ToolBarAction):
    def add_to_toolbar(self, toolbar, target):
        icon = QIcon()
        icon.addFile(
            os.path.join(MODULE_PATH, "assets", "toolbar_icons", "line_axis.svg"),
            size=QSize(20, 20),
        )
        self.action = QAction(icon, "Open Curves Configuration", target)
        toolbar.addAction(self.action)


class FitParamsAction(ToolBarAction):
    def add_to_toolbar(self, toolbar, target):
        icon = QIcon()
        icon.addFile(
            os.path.join(MODULE_PATH, "assets", "toolbar_icons", "fitting_parameters.svg"),
            size=QSize(20, 20),
        )
        self.action = QAction(icon, "Open Fitting Parameters", target)
        toolbar.addAction(self.action)


class SettingsAction(ToolBarAction):
    def add_to_toolbar(self, toolbar, target):
        icon = QIcon()
        icon.addFile(
            os.path.join(MODULE_PATH, "assets", "toolbar_icons", "settings.svg"), size=QSize(20, 20)
        )
        self.action = QAction(icon, "Open Configuration Dialog", target)
        toolbar.addAction(self.action)


class ImportAction(ToolBarAction):
    def add_to_toolbar(self, toolbar, target):
        icon = QIcon()
        icon.addFile(
            os.path.join(MODULE_PATH, "assets", "toolbar_icons", "import.svg"), size=QSize(20, 20)
        )
        self.action = QAction(icon, "Import Configuration from YAML", target)
        toolbar.addAction(self.action)


class ExportAction(ToolBarAction):
    def add_to_toolbar(self, toolbar, target):
        icon = QIcon()
        icon.addFile(
            os.path.join(MODULE_PATH, "assets", "toolbar_icons", "export.svg"), size=QSize(20, 20)
        )
        self.action = QAction(icon, "Export Current Configuration to YAML", target)
        toolbar.addAction(self.action)
