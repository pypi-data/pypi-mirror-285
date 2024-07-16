import time
from ewokscore.task import Task


class WaiterTask(
    Task,
    input_names=("object", "seconds"),  # type: ignore
    output_names=("object",),  # type: ignore
):
    """
    Simple task which waits for n seconds and release the object
    """

    def run(self):
        time.sleep(self.inputs.seconds)
        self.outputs.object = self.inputs.object
