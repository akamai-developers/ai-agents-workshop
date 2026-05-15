"""Put the workshop directory on sys.path so `from src...` works.

We're one level deeper (`solutions/_path.py`), so go up two parents to
land in the workshop root.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
