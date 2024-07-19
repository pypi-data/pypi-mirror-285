from importlib_metadata import version

try:
    __version__ = version("truefoundry")
except Exception:
    __version__ = "NA"
