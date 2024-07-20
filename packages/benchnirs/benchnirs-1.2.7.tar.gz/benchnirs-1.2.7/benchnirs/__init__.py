"""
BenchNIRS
=========
Benchmarking framework for machine learning with fNIRS
"""

import lazy_loader as lazy

from importlib.metadata import version


try:
    __version__ = version("benchnirs")
except Exception:
    __version__ = "dev"

__getattr__, __dir__, __all__ = lazy.attach(
    __name__,
    submod_attrs={
        'load': ['load_dataset'],
        'viz': ['epochs_viz'],
        'process': ['process_epochs', 'extract_features'],
        'learn': ['machine_learn', 'deep_learn', 'deep_transfer_learn']
    }
)
