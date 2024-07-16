from ewoksnotify.gui.tone import ToneSelection, ToneWindow
from silx.gui.utils.testutils import SignalListener


def test_ToneSelection(qtapp):
    """test the ToneSelection widget"""
    widget = ToneSelection()
    listener = SignalListener()
    widget.sigConfigChanged.connect(listener)
    assert widget.getConfiguration() == {
        "theme": "zelda",
        "tone_type": "success",
    }

    assert listener.callCount() == 0

    new_config = {
        "theme": "chime",
        "tone_type": "error",
    }
    widget.setConfiguration(new_config)
    assert widget.getConfiguration() == new_config
    assert listener.callCount() == 2


def test_ToneWindow(qtapp):
    """test the ToneWindow"""
    widget = ToneWindow()
    assert widget.getConfiguration() == {
        "theme": "zelda",
        "tone_type": "success",
        "muted": False,
    }

    new_config = {
        "theme": "chime",
        "tone_type": "error",
        "muted": True,
    }
    widget.setConfiguration(new_config)
    assert widget.getConfiguration() == new_config
