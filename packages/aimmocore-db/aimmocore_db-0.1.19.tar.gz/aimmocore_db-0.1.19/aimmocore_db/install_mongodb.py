import os
import pathlib
import csv
import platform
import urllib.request
import tarfile
import zipfile
import shutil
from loguru import logger


def get_download_info():
    """Return a dictionary mapping platform and architecture to download details."""
    return {
        "windows": {
            "x86_64": ("https://fastdl.mongodb.org/windows/mongodb-windows-x86_64-5.0.5.zip", "mongodb-windows.zip"),
            "amd64": ("https://fastdl.mongodb.org/windows/mongodb-windows-x86_64-5.0.5.zip", "mongodb-windows.zip"),
        },
        "linux": {
            "aarch64": {
                "22": (
                    "https://fastdl.mongodb.org/linux/mongodb-linux-aarch64-ubuntu2204-6.0.5.tgz",
                    "mongodb-linux.tgz",
                ),
                "20": (
                    "https://fastdl.mongodb.org/linux/mongodb-linux-aarch64-ubuntu2004-5.0.5.tgz",
                    "mongodb-linux.tgz",
                ),
                "18": {
                    "https://fastdl.mongodb.org/linux/mongodb-linux-aarch64-ubuntu1804-5.0.5.tgz",
                    "mongodb-linux.tgz",
                },
            },
            "x86_64": {
                "22": (
                    "https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-ubuntu2204-6.0.5.tgz",
                    "mongodb-linux.tgz",
                ),
                "20": (
                    "https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-ubuntu2004-5.0.5.tgz",
                    "mongodb-linux.tgz",
                ),
                "18": {
                    "https://fastdl.mongodb.org/linux/mongodb-linux-x86_64-ubuntu1804-5.0.5.tgz",
                    "mongodb-linux.tgz",
                },
            },
        },
        "darwin": {
            "arm64": ("https://fastdl.mongodb.org/osx/mongodb-macos-x86_64-6.0.2.tgz", "mongodb-macos.tgz"),
            "x86_64": ("https://fastdl.mongodb.org/osx/mongodb-macos-x86_64-5.0.5.tgz", "mongodb-macos.tgz"),
        },
    }


def get_linux_version() -> str:
    """Get linux version from /etc/os-release file.

    Returns:
        str: major version of the linux distribution
    """
    path = pathlib.Path("/etc/os-release")
    with open(path, encoding="utf8") as stream:
        reader = csv.reader(stream, delimiter="=")
        # filter empty lines
        d = dict(line for line in reader if line)
        return d["VERSION_ID"].split(".")[0]


def download_file(url: str, destination: str, filename: str):
    """Download file from URL to the destination if it does not already exist."""
    filepath = os.path.join(destination, filename)
    if not os.path.exists(filepath):
        logger.debug(f"Downloading MongoDB from {url}...")
        urllib.request.urlretrieve(url, filepath)
        logger.debug("Download complete.")
    else:
        logger.debug("MongoDB archive already downloaded.")
    return filepath


def download_mongodb(destination):
    """Download MongoDB based on the operating system and architecture."""
    system = platform.system().lower()
    arch = platform.machine().lower()
    download_info = get_download_info()

    url, filename = get_download_url_and_filename(system, arch, download_info)
    return download_file(url, destination, filename)


def get_download_url_and_filename(system: str, arch: str, download_info: dict):
    """Get the download URL and filename based on the system and architecture.

    Args:
        system (str): system name, e.g. Windows, Linux, Darwin
        arch (str): architecture, e.g. x86_64, amd64, aarch64
        download_info (dict): download information

    Returns:
        tuple[str, str]: downloadable URL and filename
    """
    if system not in download_info:
        raise_unsupported_exception(system, arch)

    if system == "Linux":
        version = get_linux_version()
        if arch not in download_info[system] or version not in download_info[system][arch]:
            raise_unsupported_exception(system, arch, version)
        return download_info[system][arch][version]
    else:
        if arch not in download_info[system]:
            raise_unsupported_exception(system, arch)
        return download_info[system][arch]


def raise_unsupported_exception(system: str, arch: str, version=None):
    """Raise an exception for unsupported operating system, architecture, or version.

    Args:
        system (str): system name, e.g. Windows, Linux, Darwin
        arch (str): architecture, e.g. x86_64, amd64, aarch64
        version (_type_, optional): version of the system. Defaults to None.

    Raises:
        Exception: Version not supported
        Exception: Unsupported operating system or architecture
    """

    if version:
        raise Exception(f"Unsupported {system} version: {version} for architecture: {arch}")
    raise Exception(f"Unsupported operating system or architecture: {system}, {arch}")


def extract_mongodb(filepath, destination):
    temp_extract_path = os.path.join(destination, "temp_mongodb")
    if not os.path.exists(temp_extract_path):
        os.makedirs(temp_extract_path)

    if filepath.endswith(".zip"):
        with zipfile.ZipFile(filepath, "r") as zip_ref:
            zip_ref.extractall(temp_extract_path)
    elif filepath.endswith(".tgz") or filepath.endswith(".tar.gz"):
        with tarfile.open(filepath, "r:gz") as tar_ref:
            tar_ref.extractall(temp_extract_path)
    else:
        raise Exception("Unsupported archive format")

    # Find the extracted directory
    extracted_dir = None
    for item in os.listdir(temp_extract_path):
        item_path = os.path.join(temp_extract_path, item)
        if os.path.isdir(item_path):
            extracted_dir = item_path
            break

    if extracted_dir is None:
        raise Exception("Failed to find the extracted MongoDB directory")

    # Move files from extracted directory to the final destination
    for item in os.listdir(extracted_dir):
        s = os.path.join(extracted_dir, item)
        d = os.path.join(destination, item)
        if os.path.isdir(s):
            shutil.move(s, d)
        else:
            shutil.move(s, d)

    shutil.rmtree(temp_extract_path)

    print("Extraction complete.")


def install_mongodb(destination):
    mongodb_path = os.path.join(destination, "mongodb")
    archive_path = download_mongodb(destination)
    extract_mongodb(archive_path, mongodb_path)
    print(f"MongoDB installed to {mongodb_path}")


def main():
    install_dir = os.path.join(os.path.expanduser("~"), ".aimmocore", "mongodb_installation")
    if not os.path.exists(install_dir):
        os.makedirs(install_dir)

    install_mongodb(install_dir)

    # Optionally, add MongoDB to the PATH
    mongodb_bin = os.path.join(install_dir, "mongodb")
    os.environ["PATH"] += os.pathsep + mongodb_bin
    logger.debug(f"MongoDB bin added to PATH: {mongodb_bin}")


if __name__ == "__main__":
    main()
