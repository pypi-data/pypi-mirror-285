import collections.abc
import dataclasses
from pathlib import Path
from typing import Generator, Tuple, TypeVar, Union

import flask

from btviewer.mixins import StructureMixin

app = flask.current_app

#Declare a generic type variable
Session = TypeVar('Session')


class Session(StructureMixin):
    """
    A photo data gathering session.
    """

    def __init__(self, session_id: Union[str, Path]):
        if session_id is None:
            raise ValueError(session_id)
        if isinstance(session_id, Path):
            self.path_to_session_id(session_id)
        self.id = str(session_id)

    @classmethod
    def path_to_session_id(cls, path: Path) -> str:
        """
        If a path is passed in, then use the directory name
        """
        if not path.exists():
            raise FileNotFoundError(path)
        if not path.is_dir():
            raise NotADirectoryError(path)
        return path.name

    @classmethod
    def root_directory(cls) -> Path:
        return Path(app.config['ROOT_DIRECTORY']).absolute()

    @property
    def path(self) -> Path:
        """
        The path of this session's directory.
        e.g. ~/my_data/my_session_1
        """
        return self.root_directory().joinpath(self.id)

    def iter_set_paths(self) -> Generator[Path, None, None]:
        """
        Get all the photo sets in this session by iterating over
        all the files in this directory.
        """
        for path in self.path.iterdir():
            if path.is_dir():
                yield path

    @classmethod
    def iter_session_paths(cls) -> Generator[Path, None, None]:
        """
        Iterate over all the paths of the available session directories.

        Usage:
        for path in Session.iter_session_paths():
            print(path)
        """
        for path in cls.root_directory().iterdir():
            if path.is_dir():
                yield path

    @classmethod
    def iter_sessions(cls) -> Generator[Session, None, None]:
        """
        Iterate over all the available sessions

        Usage:
        for session in Session.iter_sessions():
            print(session)
        """
        for path in cls.iter_session_paths():
            yield cls(path.name)
