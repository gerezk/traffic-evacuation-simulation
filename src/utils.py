from pathlib import Path

def a(path):
    """Return absolute path given a relative path"""
    return str((Path(__file__).parent / path).resolve())