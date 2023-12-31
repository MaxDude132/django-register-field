#!/usr/bin/env python
# Standard libraries
import os
import sys

# Django
from django.core.management import execute_from_command_line


def runtests():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.settings")
    argv = sys.argv[:1] + ["makemigrations"] + sys.argv[1:]
    execute_from_command_line(argv)
    argv = sys.argv[:1] + ["migrate"] + sys.argv[1:]
    execute_from_command_line(argv)


if __name__ == "__main__":
    runtests()
