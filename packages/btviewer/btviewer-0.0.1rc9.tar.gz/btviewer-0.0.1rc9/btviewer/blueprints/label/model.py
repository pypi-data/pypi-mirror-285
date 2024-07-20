from pathlib import Path
from collections.abc import Mapping

import json


class Label:
    """
    A class to represent a label
    """

    def __init__(self):
        raise NotImplementedError

    @classmethod
    def list(cls, directory_path: Path):
        """
        List all the labels in a directory
        """
        raise NotImplementedError

    @property
    def path(self) -> Path:
        """
        The file path of the label file.
        :return:
        """
        raise NotImplementedError

    def save(self):
        """
        Store the label to disk
        """
        raise NotImplementedError

    def to_dict(self) -> Mapping:
        """
        Convert the label to a dictionary
        """
        raise NotImplementedError

    def to_json(self) -> str:
        return json.dumps(self.to_dict())
