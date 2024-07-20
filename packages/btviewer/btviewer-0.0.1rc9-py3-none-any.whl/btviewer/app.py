"""
Flask app to run in development mode
"""

import os
from pathlib import Path

from .app_factory import create_app

# Use test data
ROOT_DIRECTORY = os.getenv('ROOT_DIRECTORY', Path(__file__).parent.parent.joinpath('tests/data'))

app = create_app(root_directory=ROOT_DIRECTORY)
