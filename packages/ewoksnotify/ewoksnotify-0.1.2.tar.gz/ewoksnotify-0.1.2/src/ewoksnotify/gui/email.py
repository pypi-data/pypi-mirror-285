from typing import Optional
from silx.gui import qt
from silx.gui import icons


class EmailComposition(qt.QWidget):
    """
    Widget used to compose an email

    Please see https://confluence.esrf.fr/display/SCKB/Rules+about+email for email rules at esrf
    """

    sigChanged = qt.Signal()
    """emit when the composition changed"""

    def __init__(self, parent: Optional[qt.QWidget]) -> None:
        super().__init__(parent)
        self.setLayout(qt.QFormLayout())
        # from
        self._fromAddressesQLE = qt.QLineEdit(self)
        singleEmailValidator = qt.QRegularExpressionValidator(
            qt.QRegularExpression(
                r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
            ),
            self._fromAddressesQLE,
        )
        self._fromAddressesQLE.setValidator(singleEmailValidator)
        self.layout().addRow("from", self._fromAddressesQLE)
        # to
        self._toAdressesQLE = qt.QLineEdit(self)
        severalEmailValidator = qt.QRegularExpressionValidator(
            qt.QRegularExpression(
                r"(([a-zA-Z0-9_\-\.]+)@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.)|(([a-zA-Z0-9\-]+\.)+))([a-zA-Z]{2,4}|[0-9]{1,3})(\]?)(\s*;\s*|\s*$))*"
            ),
            self,
        )
        self._toAdressesQLE.setValidator(severalEmailValidator)
        self.layout().addRow("to", self._toAdressesQLE)
        # subject
        self._subjectQLE = qt.QLineEdit("ewoks notification", self)
        self.layout().addRow("subject", self._subjectQLE)
        # text
        self._textQLE = qt.QPlainTextEdit("")
        self._textQLE.setPlaceholderText("message")
        self.layout().addRow(self._textQLE)

        # connect signal / slot
        self._fromAddressesQLE.editingFinished.connect(self.sigChanged)
        self._toAdressesQLE.editingFinished.connect(self.sigChanged)
        self._subjectQLE.editingFinished.connect(self.sigChanged)
        self._textQLE.textChanged.connect(self.sigChanged)

    def getFromAddr(self) -> str:
        return self._fromAddressesQLE.text()

    def setFromAddr(self, from_addr: str):
        self._fromAddressesQLE.setText(str(from_addr))

    def getToAddrs(self) -> tuple:
        adresses = self._toAdressesQLE.text().replace(" ", "")
        adresses.replace(",", ";")
        return tuple(set(adresses.split(";")))

    def setToAddrs(self, to_addrs) -> None:
        if not isinstance(to_addrs, str):
            to_addrs = ";".join(to_addrs)
        self._toAdressesQLE.setText(str(to_addrs))

    def getText(self) -> str:
        return self._textQLE.toPlainText()

    def setText(self, text: str) -> None:
        self._textQLE.setPlainText(text)

    def getSubject(self) -> str:
        return self._subjectQLE.text()

    def setSubject(self, subject: str):
        self._subjectQLE.setText(str(subject))

    def getConfiguration(self) -> dict:
        return {
            "subject": self.getSubject(),
            "from_addr": self.getFromAddr(),
            "to_addrs": self.getToAddrs(),
            "text": self.getText(),
        }

    def setConfiguration(self, config: dict):
        if not isinstance(config, dict):
            raise TypeError
        subject = config.get("subject", None)
        if subject is not None:
            self.setSubject(str(subject))
        from_addr = config.get("from_addr", None)
        if from_addr is not None:
            self.setFromAddr(from_addr=str(from_addr))
        to_addrs = config.get("to_addrs", None)
        if to_addrs is not None:
            self.setToAddrs(to_addrs=to_addrs)
        text = config.get("text", None)
        if text is not None:
            self.setText(str(text))


class EmailSettings(qt.QWidget):
    """
    Widget to set up mail server
    """

    sigChanged = qt.Signal()
    """emit when the settings changed"""

    def __init__(self, parent: Optional[qt.QWidget]) -> None:
        super().__init__(parent)
        self.setLayout(qt.QFormLayout(self))
        # server
        self._hostQLE = qt.QLineEdit("smtps.esrf.fr", self)
        self.layout().addRow("host", self._hostQLE)
        # port
        self._portQLE = qt.QLineEdit("0", self)
        self._portQLE.setValidator(qt.QIntValidator(self._portQLE))
        self.layout().addRow("port", self._portQLE)

        # connect signal / slot
        self._hostQLE.editingFinished.connect(self.sigChanged)
        self._portQLE.editingFinished.connect(self.sigChanged)

    def getConfiguration(self) -> dict:
        return {"host": self._hostQLE.text(), "port": int(self._portQLE.text())}

    def setConfiguration(self, config: dict):
        server = config.get("host", None)
        if server is not None:
            self._hostQLE.setText(str(server))
        port = config.get("port", None)
        if port is not None:
            self._portQLE.setText(str(port))


class EmailWidget(qt.QTabWidget):
    """
    Main widget to send email
    """

    sigChanged = qt.Signal()
    """emit when the email settings or composition changed"""

    def __init__(self, parent: Optional[qt.QWidget] = None) -> None:
        super().__init__(parent)

        self.setTabPosition(qt.QTabWidget.East)

        self._compositionWidget = EmailComposition(self)
        composeIcon = icons.getQIcon("ewoksnotify:gui/icons/compose")
        self.addTab(
            self._compositionWidget,
            composeIcon,
            "",
        )

        self._serverSettingsWidget = EmailSettings(self)
        settingsIcon = icons.getQIcon("ewoksnotify:gui/icons/parameters")
        self.addTab(
            self._serverSettingsWidget,
            settingsIcon,
            "",
        )

        # connect signal / slot
        self._compositionWidget.sigChanged.connect(self.sigChanged)
        self._serverSettingsWidget.sigChanged.connect(self.sigChanged)

    def getConfiguration(self) -> dict:
        config = self._serverSettingsWidget.getConfiguration()
        config.update(self._compositionWidget.getConfiguration())
        return config

    def setConfiguration(self, config: dict):
        self._serverSettingsWidget.setConfiguration(config)
        self._compositionWidget.setConfiguration(config)
