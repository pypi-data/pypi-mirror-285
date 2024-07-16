"""Dinkin Flicka."""

# read version from installed package
from importlib.metadata import version
__version__ = version("cookiecutter_dinkin_flicka")

# populate package namespace
from cookiecutter_dinkin_flicka.cookiecutter_dinkin_flicka import *