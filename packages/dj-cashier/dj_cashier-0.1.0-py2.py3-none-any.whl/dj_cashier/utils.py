from datetime import datetime
import importlib


def timestamps_to_str(timestamps):
    if timestamps is None:
        return None
    try:
        return datetime.fromtimestamp(float(timestamps))
    except (TypeError, ValueError):
        return None