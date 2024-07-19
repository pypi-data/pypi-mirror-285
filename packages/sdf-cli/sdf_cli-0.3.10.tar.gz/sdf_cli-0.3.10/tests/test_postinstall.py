import os
import pytest
import tempfile
import subprocess
from sdf_cli.install import install_binary
from sdf_cli import SDF_CLI_VERSION
import shutil

@pytest.fixture
def install_dir():
    """Create a temporary directory for installation."""
    dirpath = tempfile.mkdtemp()
    yield dirpath
    shutil.rmtree(dirpath)

def test_download_binary(install_dir):
    """Test the download_binary function."""
    package_dir = os.path.join(install_dir, "binaries")
    binary_path = install_binary(package_dir)
    # Check that the binary exists
    assert os.path.isfile(binary_path), f"Binary not found at {binary_path}"
    
    # Validate binary execution (assuming the binary has a --version option)
    result = subprocess.run([binary_path, '--version'], capture_output=True, text=True, check=True)
    assert SDF_CLI_VERSION in result.stdout, f"Unexpected version output: {result.stdout}"
