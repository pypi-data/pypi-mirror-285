from silx.gui import qt
from silx.gui import icons


class PadlockButton(qt.QPushButton):
    """Simple button to define a button with PadLock icons"""

    sigLockChanged = qt.Signal(bool)
    """signal emitted when the lock status change"""

    def __init__(self, parent):
        qt.QPushButton.__init__(self, parent)
        self._lockIcon = icons.getQIcon("ewoksnotify:gui/icons/locked")
        self._unlockIcon = icons.getQIcon("ewoksnotify:gui/icons/unlocked")
        self.setIcon(self._unlockIcon)
        self.setCheckable(True)

        # connect signals
        self.toggled.connect(self._updateDisplay)

    def setLock(self, lock: bool):
        self.setChecked(lock)
        self._updateDisplay(lock)

    def _updateDisplay(self, checked):
        _icon = self._lockIcon if checked else self._unlockIcon
        self.setIcon(_icon)
        self.sigLockChanged.emit(checked)

    def isLocked(self) -> bool:
        return self.isChecked()
