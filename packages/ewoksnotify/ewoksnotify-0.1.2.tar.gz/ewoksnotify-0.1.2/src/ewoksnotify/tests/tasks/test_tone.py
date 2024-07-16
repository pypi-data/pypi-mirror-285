import pytest
from ewoksnotify.tasks.tone import ToneTask


def test_ToneTask(tmp_path):
    """test ToneTask function"""
    task = ToneTask(
        inputs={
            "object": 12,
        },
    )
    task.run()
    assert task.outputs.object == 12

    task = ToneTask(
        inputs={
            "object": "toto",
            "tone_type": "info",
            "theme": "chime",
        }
    )
    task.run()
    assert task.outputs.object == "toto"

    with pytest.raises(ValueError):
        # check raise an error if path not part of PROCESSED_DATA
        ToneTask(
            inputs={
                "object": "toto",
                "tone_type": "test",
            }
        ).run()

    with pytest.raises(ValueError):
        # check raise an error if path not part of PROCESSED_DATA
        ToneTask(
            inputs={
                "object": "toto",
                "theme": "test",
            }
        ).run()
