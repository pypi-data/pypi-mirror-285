import os
import sys
from typing import Optional
from .version import SDF_CLI_VERSION
from .constants import SDF_BINARY
from pathlib import Path
from sys import executable

def get_binary_path() -> str:
    """Return the path of the installed binary."""
    return Path(executable).parent.join(SDF_BINARY)

def run_binary(binary_path: Optional[str] = None, *args):
    """Run the installed binary."""
    if binary_path is None:
        binary_path = get_binary_path()
    os.execvp(binary_path, [*args] + sys.argv[1:])

def get_binary_version():
    """Return the version of the installed binary."""
    return SDF_CLI_VERSION