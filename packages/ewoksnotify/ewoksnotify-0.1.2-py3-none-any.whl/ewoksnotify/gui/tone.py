from silx.gui import qt
from ewoksnotify.tasks.tone import has_chime
from ewoksnotify.gui.actions import ParametersAction

if has_chime:
    import chime


class ToneSelection(qt.QWidget):
    """
    Widget to select tone type and theme
    """

    sigConfigChanged = qt.Signal()
    """emit when the configuration is changed"""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        if not has_chime:
            raise ImportError("chime not available")
        self.setLayout(qt.QFormLayout())

        # define theme
        self._theme = qt.QComboBox(self)
        self._theme.addItems(chime.themes())
        self.layout().addRow("Theme", self._theme)

        # define type
        self._toneType = qt.QComboBox(self)
        self._toneType.addItems(("success", "warning", "error", "info"))
        self.layout().addRow("Tome type", self._toneType)

        # set up
        self.setTheme("zelda")
        self.setToneType("success")

        # connect signal / slot
        self._theme.currentIndexChanged.connect(self._changed)
        self._toneType.currentIndexChanged.connect(self._changed)

    def _changed(self):
        self.sigConfigChanged.emit()

    def getToneType(self) -> str:
        return self._toneType.currentText()

    def setToneType(self, tone_type: str) -> None:
        self._toneType.setCurrentText(tone_type)

    def getTheme(self) -> str:
        return self._theme.currentText()

    def setTheme(self, theme: str) -> None:
        self._theme.setCurrentText(theme)

    def getConfiguration(self):
        return {
            "tone_type": self.getToneType(),
            "theme": self.getTheme(),
        }

    def setConfiguration(self, config: dict):
        tone_type = config.get("tone_type", None)
        if tone_type is not None:
            self.setToneType(tone_type)
        tone_theme = config.get("theme", None)
        if tone_theme is not None:
            self.setTheme(tone_theme)


class ToneSelectionDialog(qt.QDialog):
    """
    Dialog dedicated to tone selection
    """

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setLayout(qt.QVBoxLayout())
        self._mainWidget = ToneSelection()
        self.layout().addWidget(self._mainWidget)

        types = qt.QDialogButtonBox.Ok | qt.QDialogButtonBox.Cancel
        self._buttons = qt.QDialogButtonBox(parent=self)
        self._buttons.setStandardButtons(types)
        self.layout().addWidget(self._buttons)

        # connect signal / slot
        self._buttons.accepted.connect(self.accept)
        self._buttons.rejected.connect(self.reject)

    # expose API
    def getToneType(self):
        return self._mainWidget.getToneType()

    def setToneType(self, *args, **kwargs):
        self._mainWidget.setToneType(*args, **kwargs)

    def getTheme(self):
        return self._mainWidget.getTheme()

    def setTheme(self, *args, **kwargs):
        self._mainWidget.setTheme(*args, **kwargs)


class ToneWindow(qt.QMainWindow):
    """Main window use to define tune and turn on / off the sound"""

    DEFAULT_CONFIGURATION = {
        "tone_type": "success",
        "theme": "zelda",
        "muted": False,
    }

    def __init__(self, parent=None):
        super().__init__(parent)
        self._configuration = self.DEFAULT_CONFIGURATION
        self._soundButton = qt.QPushButton(parent=self)
        self._soundButton.setMinimumSize(150, 100)
        self._soundButton.setCheckable(True)
        self.setCentralWidget(self._soundButton)

        # add toolbar
        toolbar = qt.QToolBar(self)
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        self.addToolBar(qt.Qt.TopToolBarArea, toolbar)

        # add Parameters Action
        self._parametersAction = ParametersAction(toolbar)
        toolbar.addAction(self._parametersAction)
        # set up
        self._updateButtonIcon()

        # connect signal / slot
        self._soundButton.toggled.connect(self._switchMute)
        self._parametersAction.triggered.connect(self._parametersTriggered)

    def _parametersTriggered(self):
        dialog = ToneSelectionDialog()
        dialog.setToneType(self.getConfiguration()["tone_type"])
        dialog.setTheme(self.getConfiguration()["theme"])
        if dialog.exec_():
            self._configuration["tone_type"] = dialog.getToneType()
            self._configuration["theme"] = dialog.getTheme()

    def _switchMute(self):
        self._configuration["muted"] = not self._configuration["muted"]
        self._updateButtonIcon()

    def _updateButtonIcon(self):
        style = qt.QApplication.style()
        if self._configuration["muted"]:
            icon = style.standardIcon(qt.QStyle.SP_MediaVolumeMuted)
        else:
            icon = style.standardIcon(qt.QStyle.SP_MediaVolume)
        self._soundButton.setIcon(icon)

    def getConfiguration(self) -> dict:
        return self._configuration

    def setConfiguration(self, config: dict):
        self._configuration = config
