from silx.gui import qt
from silx.gui.icons import getQIcon


class ParametersAction(qt.QAction):
    """
    Action to display a window with nxtomomill configuration
    """

    def __init__(self, parent):
        icon = getQIcon("ewoksnotify:gui/icons/parameters")

        qt.QAction.__init__(self, icon, "filter configuration", parent)
        self.setToolTip("Open dialog to configure nxtomomill parameters")
        self.setCheckable(False)
