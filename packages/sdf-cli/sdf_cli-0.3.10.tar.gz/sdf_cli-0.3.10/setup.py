from os.path import abspath, dirname, join
from pathlib import Path
import platform
import shutil
from setuptools import setup
from setuptools.command.install import install
from sys import executable
from tarfile import open as taropen
from tempfile import TemporaryDirectory
from urllib.request import Request, urlopen

version = {}
with open(Path(__file__).parent / "sdf_cli/version.py", encoding="utf8") as fp:
    exec(fp.read(), version)

SDF_CLI_VERSION = version['SDF_CLI_VERSION']

constants = {}
with open(Path(__file__).parent / "sdf_cli/constants.py", encoding="utf8") as fp:
    exec(fp.read(), constants)

SDF_BINARY = constants['SDF_BINARY']

def download_binary(url) -> bytes:
    """Downloads and return binary bytes."""
    req = Request(url)
    with urlopen(req) as resp:
        return resp.read()


class PostInstallCommand(install):
    """Post-installation for installation mode."""

    def run(self):
        install.run(self)
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
        install_dir = Path(executable).parent
        binary_path = join(install_dir, SDF_BINARY)
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

desc = "The sdf command line interface (CLI) - For info on how to get started, visit: docs.sdf.com"

this_directory = abspath(dirname(__file__))
with open(join(this_directory, "README.md")) as f:
    long_desc = f.read()

setup(
    name="sdf-cli",
    platforms="any",
    version=SDF_CLI_VERSION,
    description=desc,
    long_description=long_desc,
    long_description_content_type="text/markdown",
    author="sdf Labs",
    author_email="info@sdf.com",
    url="https://www.sdf.com/",
    zip_safe=False,
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    license='Proprietary - See Terms of Service: https://www.sdf.com/terms-of-service',
    cmdclass={
        "install": PostInstallCommand,
    },
    install_requires=["setuptools>=61.2"],
)
