import importlib
from pathlib import Path
import sys

try:
    _tracker_module = importlib.import_module("economic_sdk.tracker")
except Exception:
    root = Path(__file__).resolve().parents[3]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    _tracker_module = importlib.import_module("economic_sdk.tracker")


EconomicTracker = _tracker_module.EconomicTracker
track_response_tokens = _tracker_module.track_response_tokens


__all__ = ["EconomicTracker", "track_response_tokens"]
