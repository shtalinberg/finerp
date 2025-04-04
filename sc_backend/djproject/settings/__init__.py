import sys

try:
    from .base_final import *
except ImportError:
    sys.stderr.write("Unable to read djproject.settings.base_final.py\n")
    DEBUG = False
