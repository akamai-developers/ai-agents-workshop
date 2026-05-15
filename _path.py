"""Put the workshop directory on sys.path so `from src...` works.

Each section does `import _path` first so it can be run from any cwd.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
