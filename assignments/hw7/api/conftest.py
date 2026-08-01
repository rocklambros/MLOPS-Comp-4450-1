"""Put the api app directory on sys.path so tests import `main` directly.

Explicit rather than relying on pytest's implicit rootdir insertion, so `make test`
works from the hw7 root, from inside api/, and under `python -m pytest` alike.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
