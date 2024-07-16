from ewoksnotify.gui.email import EmailWidget


def test_Emailwidget(qtapp):
    """test of Emailwidget"""
    widget = EmailWidget()
    widget.show()

    assert widget.getConfiguration() == {
        "from_addr": "",
        "to_addrs": ("",),
        "subject": "ewoks notification",
        "text": "",
        "port": 0,
        "host": "smtps.esrf.fr",
    }

    new_configuration = {
        "from_addr": "toto.esrf.fr",
        "to_addrs": "toto.esrf.fr;tata.esrf.fr",
        "subject": "new subject",
        "text": "my new text",
        "port": 445,
        "host": "smtps.esrf.en",
    }
    widget.setConfiguration(new_configuration)

    configuration = widget.getConfiguration()
    new_configuration.pop("to_addrs")
    assert configuration.pop("to_addrs") in (
        ("toto.esrf.fr", "tata.esrf.fr"),
        ("tata.esrf.fr", "toto.esrf.fr"),
    )
    assert configuration == new_configuration
