import datetime
import io
import json
from pathlib import Path
from typing import Iterable, Mapping, Union, Generator

import PIL.Image
import flask
import numpy

app: flask.Flask = flask.current_app

Coordinate = tuple[int, int]
"x, y position in a 2D image pixel grid"


class Photo:
    """
    An image taken by a camera.
    """

    def __init__(self, path: Union[Path, str]):
        self.path = Path(app.config['ROOT_DIRECTORY']).joinpath(path).absolute()

    @classmethod  # not used, to be deleted
    def validate_filename(cls, filename: str):
        """
        Validate a filename <timestamp>_<photo_id>.np
        https://github.com/SheffieldMLtracking#file-structures
        where timestamp is YYYMMDD_HHMMSS.UUUUUU
        where photo_id is a zero-padded integer
        """
        filename = Path(filename)
        if filename.suffix != ".np":
            raise ValueError(filename)
        timestamp, _, photo_id = filename.stem.rpartition("_")
        photo_id = int(photo_id)
        cls.parse_timestamp(timestamp)

    @classmethod  # only used in validate_filename, to be deleted.
    def parse_timestamp(cls, timestamp: str) -> datetime.datetime:
        """
        Parse the `timestamp` part of a photo filename.
        https://github.com/SheffieldMLtracking#file-structures
        "YYYMMDD_HHMMSS.UUUUUU" -> datetime.datetime()
        """
        # https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior
        dt = datetime.datetime.strptime(timestamp, "%Y%m%d_%H%M%S.%f")
        # Use UTC timestamp
        dt.replace(tzinfo=datetime.timezone.utc)
        return dt

    @classmethod
    def root_directory(cls) -> Path:
        return Path(app.config['ROOT_DIRECTORY']).absolute()

    @property  # not used
    def timestamp_string(self) -> str:
        raise NotImplementedError

    @property  # not used
    def filename(self) -> str:
        return f"{self.timestamp_string}_{self.photo_id}.np"

    def load(self) -> dict:
        """
        Get the image data from the storage disk.
        :returns:
        {
          "record": {...},
          "image": array(...)
        }
        """
        # https://numpy.org/doc/stable/reference/generated/numpy.load.html
        data = numpy.load(self.path, allow_pickle=True)
        app.logger.info("Loaded '%s'", self.path)
        return data

    def add_label(self, label: dict, **kwargs):  # Not used
        """
        Add a label to the image.

        :param label: The tag info
        :param kwargs: Label parameters
        :return:
        """
        return self.add_labels([label], **kwargs)

    def add_labels(self, labels: list[dict], source: str, version: str, indent: int = 2) -> Path:
        label_path = self.make_label_path(source=source)

        # Build a list of labels, starting with an empty list
        document: list[dict] = []

        # Open existing labels file
        try:
            with label_path.open('r') as file:
                document.extend(json.load(file))
        except FileNotFoundError:
            pass

        # Append the metadata to each new label
        metadata = {
            "source": source,
            "version": version,
            "mode": "manual",
            "annotation": ""
        }
        for label in labels:
            label.update(metadata)

        # Include the newly-added labels
        document.extend(labels)

        # Save labels to disk
        with label_path.open('w') as file:
            json.dump(document, file)

        app.logger.info("Labels saved to '%s'", label_path)
        return label_path

    @property
    def label_filename(self) -> str:
        """
        The filename of each label file

        e.g. "2020-01-01T09+40+43_00123.json"
        """
        return self.path.with_suffix('.json').name

    def make_label_path(self, source: str) -> Path:
        """
        The path of the file containing all the label files for this photo for this source.
        """
        # If the photo path is
        # ~/photos/2020-01-01T09+40+43_00123.np
        # the label directory for btviewer is
        # ~/photos/btviewer/2020-01-01T09+40+43_00123.json

        # Make a subdirectory for this source
        label_dir = self.path.parent.joinpath(source)
        label_dir.mkdir(exist_ok=True)

        # Build the label path
        label_path = label_dir.joinpath(self.label_filename)

        return label_path

    @property
    def metadata(self) -> dict:
        """
        Get all the image information, except the 2D image data array.
        """
        return {key: value for key, value in self.data.items() if key != 'img'}

    @property
    def dimension(self) -> dict:
        """
        Get all the image dimension
        """
        image = self.data['img']
        width = len(image[0])
        height = len(image)
        return {'width': width, 'height': height}

    def to_tiff(self):
        """
        Convert image data to TIFF format
        """
        return self.to_bytes(format='TIFF')

    def to_jpeg(self):
        return self.to_bytes(format='JPEG')

    @property
    def data(self) -> Mapping:
        """
        Image data and metadata
        """
        return self.load()

    @property
    def array(self):
        return self.get_array()

    def get_array(self, scale_factor: float = None, dtype=numpy.dtype('uint8'),
                  mean_exposure: float = 0.18) -> numpy.array:
        """
        2D image data array of pixel values.

        By default, this produces a normalised 2D grid of unsigned 8-bit integers (0 to 255).

        :param scale_factor: Multiplication factor for the pixel brightness values
        :param dtype: Data type https://numpy.org/doc/stable/reference/generated/numpy.ndarray.astype.html
        :param mean_exposure: The target average brightness (default 1to 18% grey)
        """
        # Set data type for array values
        dtype = numpy.dtype(dtype)
        maximum_value = numpy.iinfo(dtype).max  # machine limits for integer type

        # Load image data
        array: numpy.ndarray = self.data['img']

        if scale_factor is None:
            # Adjust brightness to target average exposure
            scale_factor = maximum_value * mean_exposure / array.mean()

        numpy.multiply(array, scale_factor, out=array, casting='unsafe')

        return array.astype(dtype=dtype)

    @property
    def image(self) -> PIL.Image:
        """
        A PIL image object for the photo data.
        """
        return PIL.Image.fromarray(self.array)

    def to_bytes(self, **kwargs) -> io.BytesIO:
        """
        Convert the 2D image data to an image file format.

        :param kwargs: Keyword arguments for PIL Image.save()
        :returns: Image data buffer
        """
        # Use BytesIO to store the image in memory
        buffer = io.BytesIO()
        self.image.save(buffer, **kwargs)
        buffer.seek(0)

        return buffer

    def to_png(self):
        """
        Convert image data to PNG format
        """
        return self.to_bytes(format='PNG')

    def iter_labels(self) -> Generator[Mapping, None, None]:
        """
        Iterate over label documents for this image.
        """
        # Iterate over subdirectories 
        path: Path
        for path in self.path.parent.iterdir():
            # Subdirectories only, for example btviewer folder and retrodetect
            if path.is_dir():
                label_path = path.joinpath(self.label_filename)  # btviewer/photofilename.json
                try:
                    # Load JSON data
                    with label_path.open() as file:
                        doc = json.load(file)
                        app.logger.info("Loaded '%s'", file.name)
                    # Get list of tags
                    yield from doc  # https://www.geeksforgeeks.org/use-yield-keyword-instead-return-keyword-python/
                except FileNotFoundError:
                    continue

    @property
    def labels(self) -> Iterable[Mapping]:
        """
        The tags applied to this image.
        """
        return list(dict(label) for label in self.iter_labels())

    def next(self, skip: int = 1) -> Path:
        """
        Get the path of the next file in this directory.

        :param skip: The number of photo files to navigate through.
        """

        # Get the list of photo filenames in the current directory
        camera_dir = self.path.parent
        photos = sorted(camera_dir.glob('*.np'))

        # Figure out the current position in that list
        current_index = photos.index(self.path)

        # Go to the previous/next file
        # Skip x photos (skip may be negative or positive)
        try:
            return photos[current_index + skip]
        except IndexError:
            # If there are no more,. just go the first one
            return photos[0]

    def delete_labels(self, source: str, x: int = None, y: int = None, indent: int = 2):
        """
        Delete some labels associated with this photo.

        :param source: The app that created the label e.g. "btviewer"
        :param x: The horizontal pixel coordinate
        :param y: The vertical pixel coordinate
        :param indent: JSON formatting option
        """

        # Get the label file
        label_path = self.make_label_path(source=source)

        # Delete all labels from that source when no specific label specified
        if not x:

            label_path.unlink(missing_ok=True)
            app.logger.info("Deleted '%s'", label_path)

        # Delete a specific label
        else:
            with label_path.open() as file:
                labels = json.load(file)

            # Exclude the coordinates to be deleted
            labels = [label for label in labels if int(label['x']) != int(x) and int(label['y']) != int(y)]

            # Save changes to disk
            with label_path.open('w') as file:
                json.dump(labels, file, indent=indent)
                app.logger.info("Deleted label at %s, %s from '%s'", x, y, file.name)

    def annotate_labels(self, source: str, annotation_text: str, x: int, y: int, indent: int = 2, ):
        """
        Add annotation to existing labels associated with this photo.

        :param source: The app that created the label e.g. "btviewer"
        :param x: The horizontal pixel coordinate
        :param y: The vertical pixel coordinate
        :param indent: JSON formatting option
        :param annotation_text: annotation text
        """
        # Get the label file
        label_path = self.make_label_path(source=source)
        with label_path.open() as file:
            labels = json.load(file)

        # find the label corresponding to the clicked point to add the annotation
        # Note it will replace existing annotation
        for label in labels:
            if int(label['x']) == int(x) and int(label['y']) == int(y):
                label.update({"annotation": annotation_text})

        # Save changes to disk
        with label_path.open('w') as file:
            json.dump(labels, file, indent=indent)
            app.logger.info("annotate label at %s, %s from '%s'", x, y, file.name)

    def select_region_of_interest(self, box: tuple[Coordinate, Coordinate]) -> numpy.ndarray:
        """
        Select an area within the 2D pixel array of the photo image.

        :param box: The coordinates of the top-left and bottom-right pixel of the selected 2D region of interest.

        top_left, ...
        ..., bottom_right
        """

        # Load the image data
        array = self.array

        # Get the two corner coordinates
        top_left, bottom_right = box

        # Get the pixel values inside the bounding box only
        region_of_interest = array[top_left[0]: bottom_right[0], top_left[1]: bottom_right[1]]

        return region_of_interest

    def find_brightest_pixel(self, box: tuple[Coordinate, Coordinate]) -> Coordinate:
        """
        Get the coordinate of the brightest pixel in the specified bounding area.

        :param box: The coordinates of the top-left and bottom-right pixel of the selected 2D region of interest.
        """

        region_of_interest = self.select_region_of_interest(box=box)

        # Get the position of the  brightest pixel (using a flat index)
        flat_max_index = numpy.argmax(region_of_interest)

        # Get the relative coordinates of that brightest pixel (inside the ROI)
        x, y = numpy.unravel_index(flat_max_index, region_of_interest.shape)

        # Get the absolute coordinates (relative to the entire image)
        top_left_coordinate = box[0]
        x += top_left_coordinate[0]
        y += top_left_coordinate[1]

        # Cast from numpy.int64 to integer
        return int(x), int(y)
