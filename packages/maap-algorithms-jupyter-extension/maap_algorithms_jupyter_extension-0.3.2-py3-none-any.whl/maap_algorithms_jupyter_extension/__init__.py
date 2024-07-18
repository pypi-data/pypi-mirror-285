from ._version import __version__


def _jupyter_labextension_paths():
    return [{
        "src": "labextension",
        "dest": "maap_algorithms_jupyter_extension"
    }]

