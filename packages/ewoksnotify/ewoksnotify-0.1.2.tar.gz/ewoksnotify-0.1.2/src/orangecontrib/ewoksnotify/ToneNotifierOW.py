from orangewidget import gui
from silx.gui import qt
from ewoksnotify.gui.tone import ToneWindow
from ewoksorange.bindings.owwidgets import OWEwoksWidgetNoThread
from ewoksnotify.tasks.tone import ToneTask


class ToneNotifierOW(
    OWEwoksWidgetNoThread,
    ewokstaskclass=ToneTask,  # type: ignore
):
    """
    simple widget which pop up, ring and closes when recive a new object
    """

    name = "tone notifier"
    id = "orangecontrib.ewoksnotify.ToneNotifierOW"
    description = "Simple widget which pop up for 2 second when recives a new object and emit a tone"
    icon = "icons/notification.png"
    priority = 145
    keywords = ["notifier", "notification", "ewoks", "ewoksnotify"]

    _ewoks_inputs_to_hide_from_orange = (
        "tone_type",
        "theme",
        "muted",
        "with_text_message",
    )

    want_main_area = True
    want_control_area = False
    resizing_enabled = False

    def __init__(self, parent=None):
        super().__init__(parent)
        self.pop_up = None
        layout = gui.vBox(self.mainArea, self.name).layout()
        # define tone
        self._toneWidget = ToneWindow(parent=self)
        self._toneWidget.setWindowFlag(qt.Qt.Widget)
        layout.addWidget(self._toneWidget)
        # define pop up
        self._popUpCheckBox = qt.QCheckBox("trigger pop up", self)
        layout.addWidget(self._popUpCheckBox)

    def handleNewSignals(self) -> None:
        """Invoked by the workflow signal propagation manager after all
        signals handlers have been called.
        """
        my_object = super().get_task_inputs().get("object", None)
        if my_object is not None and self._popUpCheckBox.isChecked():
            self._activePopUp(my_object=my_object)
        super().handleNewSignals()

    def get_task_inputs(self):
        task_inputs = super().get_task_inputs()
        # when we are with the gui we go for the Qt pop up instead of the message to stdout
        task_inputs["with_text_message"] = False
        task_inputs.update(self._toneWidget.getConfiguration())
        return task_inputs

    def _activePopUp(self, my_object):
        if self.pop_up is not None:
            self.pop_up.close()

        self.pop_up = NotificationMessage()
        text = f"{my_object} received."
        self.pop_up.setText(text)
        self.pop_up.show()


class NotificationMessage(qt.QMessageBox):
    EXPOSITION_TIME = 3000  # in ms

    def __init__(self) -> None:
        super().__init__()
        self.setModal(False)
        self.setIcon(qt.QMessageBox.Information)
        self.addButton(
            f"Ok - will close automatically after {self.EXPOSITION_TIME / 1000}s",
            qt.QMessageBox.YesRole,
        )

    def show(self):
        super().show()
        timer = qt.QTimer(self)
        timer.singleShot(
            self.EXPOSITION_TIME,
            self.close,
        )
