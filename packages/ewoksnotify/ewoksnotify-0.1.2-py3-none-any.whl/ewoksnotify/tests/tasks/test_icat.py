import os
import pytest
from ewoksnotify.tasks.icat import PublishProcessedDataFolderTask


def test_PublishProcessedDataFolderTask(tmp_path):
    """test PublishProcessedDataFolderTask function"""
    inputs = {
        "beamline": "my_beamline",
        "proposal": "my_proposal",
        "dataset": "my_dataset",
        "path": tmp_path,
        "raw": "/path/to/raw/dataset",
        "dry_run": True,
    }
    task = PublishProcessedDataFolderTask(
        inputs=inputs,
    )

    # check raise an error if path doesn't exists
    inputs["path"] = os.path.join(tmp_path, "PROCESSED_DATA", "dataset")
    task = PublishProcessedDataFolderTask(
        inputs=inputs,
    )
    with pytest.raises(ValueError):
        task.run()
    os.makedirs(inputs["path"])
    task.run()
