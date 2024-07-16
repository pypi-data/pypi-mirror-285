import os
import logging
from ewokscore.task import Task

try:
    from pyicat_plus.client.main import IcatClient  # noqa F401
except ImportError:
    has_pyicat_plus = False
else:
    has_pyicat_plus = True

_logger = logging.getLogger(__name__)


class PublishProcessedDataFolderTask(
    Task,
    input_names=(  # type: ignore
        "beamline",
        "proposal",
        "dataset",
        "path",
        "raw",
    ),
    optional_input_names=(  # type: ignore
        "metadata",
        "dry_run",
    ),
):
    """publish a folder containing 'processed data' to icat for the provided beamline && dataset && proposal"""

    def run(self):
        beamline = self.inputs.beamline
        proposal = self.inputs.proposal
        dataset = self.inputs.dataset
        raw = self.inputs.raw
        metadata = self.get_input_value("metadata", {})
        path = self.inputs.path
        dry_run = self.get_input_value("dry_run", False)

        # checks (need because can be pass by a GUI and will set those values to empty string mostly)
        missing = []
        if beamline in (None, ""):
            missing.append("beamline")
        if proposal in (None, ""):
            missing.append("proposal")
        if dataset in (None, ""):
            missing.append("dataset")
        if raw is None or len(raw) == 0:
            missing.append("raw")

        if len(missing) > 0:
            mess = f"Missing information about {','.join(missing)}"
            _logger.error(mess)
            raise ValueError(mess)
        if not os.path.exists(path):
            raise ValueError(f"path: {path} doesn't exists")

        # publish
        if not has_pyicat_plus:
            raise ImportError("pyicat_plus not installed")

        if not dry_run:
            icat_client = IcatClient(
                metadata_urls=("bcu-mq-01.esrf.fr:61613", "bcu-mq-02.esrf.fr:61613")
            )

            icat_client.store_processed_data(
                beamline=beamline,
                proposal=proposal,
                dataset=dataset,
                path=path,
                metadata=metadata,
                raw=raw,
            )
