# Standard libraries
from pathlib import Path

# django_register
from setuptools import find_packages, setup

VERSION = "1.0.8"
DESCRIPTION = "A field that returns a python object."
this_directory = Path(__file__).parent
LONG_DESCRIPTION = (this_directory / "README.md").read_text()

setup(
    name="django-register-field",
    version=VERSION,
    author="Maxime Toussaint",
    author_email="m.toussaint@mail.com",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=("django>=3.2.0",),
    url="https://github.com/MaxDude132/django-register-field",
)
