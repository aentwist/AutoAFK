import os
import sys


SRC_DIR = os.path.dirname(os.path.abspath(__file__))
project_dir = getattr(sys, "_MEIPASS", os.path.split(SRC_DIR)[0])
