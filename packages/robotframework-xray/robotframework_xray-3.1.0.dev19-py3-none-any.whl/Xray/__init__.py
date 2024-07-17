import sys
from .Listener import Listener


class Xray():
    print("RUNNING PYTHON VERSION = " + sys.version)
    print("SYSTEM PATH = " + sys.path)
    ROBOT_LIBRARY_LISTENER = Listener()
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
