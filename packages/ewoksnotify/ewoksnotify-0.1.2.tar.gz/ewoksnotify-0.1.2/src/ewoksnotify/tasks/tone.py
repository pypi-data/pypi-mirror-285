import sys

try:
    import chime
except ImportError:
    has_chime = False
else:
    has_chime = True
from ewokscore.task import Task


class ToneTask(
    Task,
    input_names=("object",),  # type: ignore
    optional_input_names=("tone_type", "theme", "muted", "with_text_message"),  # type: ignore
    output_names=("object",),  # type: ignore
):
    """publish a folder containing 'processed data' to icat for the provided beamline && dataset && proposal"""

    def run(self):
        muted = self.get_input_value("muted", False)
        tone_theme = self.get_input_value("theme", "zelda")
        if tone_theme not in chime.themes():
            raise ValueError(f"invalid theme requested: {tone_theme}")

        chime.theme(tone_theme)

        if not muted:
            tone_type = self.get_input_value("tone_type", "success")
            if tone_type == "success":
                chime.success()
            elif tone_type == "warning":
                chime.warning()
            elif tone_type == "error":
                chime.error()
            elif tone_type == "info":
                chime.info()
            else:
                raise ValueError(f"tone type ({tone_type}) is not handled")

        if self.get_input_value("with_text_message", False):
            sys.stdout.write(f"{object} received")
        # providing an output is discussable. But user are not force to connect it to anything
        self.outputs.object = self.inputs.object
