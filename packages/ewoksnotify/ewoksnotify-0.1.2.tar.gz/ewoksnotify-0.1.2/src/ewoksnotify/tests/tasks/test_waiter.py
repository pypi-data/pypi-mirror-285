from ewoksnotify.tasks.waiter import WaiterTask


def test_WaiterTask():
    task = WaiterTask(
        inputs={
            "object": "toto",
            "seconds": 0.2,
        }
    )
    task.run()
    assert task.outputs.object == "toto"
