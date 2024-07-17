import platform
import shutil
from os.path import join
from sdf_cli.version import SDF_CLI_VERSION
from sdf_cli.constants import SDF_BINARY
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.request import Request, urlopen
from tarfile import open as taropen

def download_binary(url) -> bytes:
    """Downloads and return binary bytes."""
    req = Request(url)
    with urlopen(req) as resp:
        return resp.read()

def install_binary(target_dir: str) -> str:
    system = platform.system().lower()
    arch = platform.machine().lower()

    if system == 'darwin':
        if arch == 'arm64':
            target = 'aarch64-apple-darwin'
        elif arch == 'x86_64':
            target = 'x86_64-apple-darwin'
    elif system == 'linux':
        if arch == 'x86_64':
            target = 'x86_64-unknown-linux-musl'
        elif arch == 'aarch64':
            target = 'aarch64-unknown-linux-gnu'
    else:
        raise RuntimeError(f'Unsupported platform: {system} {arch}')
    sdf_target = f'sdf-v{SDF_CLI_VERSION}-{target}'
    sdf_target_archive = f'{sdf_target}.tar.gz'
    # Download the binary to memory, untar it, and place contents to the target path
    install_dir = Path(target_dir)
    binary_path = join(install_dir, SDF_BINARY)
    if not install_dir.exists():
        install_dir.mkdir(parents=True)
    url = f'https://cdn.sdf.com/releases/download/{sdf_target_archive}'
    # Ensure the target directory exists
    with TemporaryDirectory() as temp_dir:
        temp_file = join(temp_dir, "temp.tar.gz")
        with open(temp_file, "wb") as file:
            file.write(download_binary(url))
        # Extract to temporary directory
        with taropen(temp_file) as tar:
            tar.extract(f"{sdf_target}/{SDF_BINARY}", temp_dir)
        # Move the binary to the target directory
        shutil.move(join(temp_dir, f"{sdf_target}/{SDF_BINARY}"), binary_path)
    return binary_path