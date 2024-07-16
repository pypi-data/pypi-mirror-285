import os
import subprocess
from setuptools import setup, find_packages
from setuptools.command.install import install


class PostInstallCommand(install):
    """Post-installation for installation mode."""

    def run(self):
        install.run(self)
        self._install_mongodb()

    def _install_mongodb(self):
        path = os.path.expanduser("~/.aimmocore/mongodb_installation/mongodb/bin/bin")

        # Check if the path exists and remove it if it does
        # Remove the directory if it exists
        if os.path.exists(path):
            subprocess.run(["rm", "-rf", path], check=True)
        subprocess.run(["python", "-m", "aimmocore_db.install_mongodb"], check=True)


setup(
    name="aimmocore-db",
    version="0.1.17",
    packages=find_packages(),
    cmdclass={
        "install": PostInstallCommand,
    },
)
