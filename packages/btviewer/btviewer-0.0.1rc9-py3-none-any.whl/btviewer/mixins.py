import pathlib


class StructureMixin:
    """
    These behaviours are common to every part of the file structure
    """

    # defines the default string representation of an object of a class inheriting from StructureMixin. It simply returns the object's id
    def __str__(self):
        return self.id

    # defines the "official" string representation, used when you print the object or use repr()
    def __repr__(self):
        return f"{self.__class__.__name__}('{self.id}')"

    
    @property
    def path(self) -> pathlib.Path:
        raise NotImplementedError

    @property
    def uri(self) -> str:
        return self.path.as_uri()
