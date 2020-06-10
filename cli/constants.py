import os
from pathlib import Path


CONFIGURATION_FILE = os.path.join(Path.home(), ".tcmanger", "config.json")
ALLOWED_CHARACTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890-_()"
