from orangewidget import gui
from silx.gui import qt
from ewoksorange.bindings.owwidgets import OWEwoksWidgetOneThreadPerRun
from ewoksnotify.tasks.waiter import WaiterTask


class WaiterOW(
    OWEwoksWidgetOneThreadPerRun,
    ewokstaskclass=WaiterTask,  # type: ignore
):
    """
    simple widget that sleeps for n seconds when received an object then release it
    """

    name = "waiter"
    id = "orangecontrib.ewoksnotify.WaiterOW"
    description = "simple widget that sleeps for n seconds when received an object then release it"
    icon = "icons/waiter.png"
    priority = 160
    keywords = ["waiter", "ewoks", "ewoksnotify"]

    _ewoks_inputs_to_hide_from_orange = ("seconds",)

    want_main_area = True
    want_control_area = False
    resizing_enabled = False

    def __init__(self, parent=None):
        super().__init__(parent)
        self.pop_up = None
        layout = gui.hBox(self.mainArea, self.name).layout()
        # sleeping time
        layout.addWidget(qt.QLabel("waiting time", self))
        self._secondQSB = qt.QSpinBox(self)
        self._secondQSB.setValue(3)
        self._secondQSB.setRange(1, 2147483647)
        self._secondQSB.setSuffix(" seconds")
        layout.addWidget(self._secondQSB)

    def get_task_inputs(self):
        task_inputs = super().get_task_inputs()
        # when we are with the gui we go for the Qt pop up instead of the message to stdout
        task_inputs.update(
            {
                "seconds": float(self._secondQSB.value()),
            }
        )
        return task_inputs
