import os
import shutil
import subprocess
from setuptools import setup, find_packages
from setuptools.command.install import install


class PostInstallCommand(install):
    """Post-installation for installation mode."""

    def run(self):
        install.run(self)
        self._install_mongodb()

    def _clean_previous_installation(self):
        previous_path = os.path.expanduser("~/.aimmocore/mongodb_installation/mongodb/bin/bin")
        if os.path.exists(previous_path):
            shutil.rmtree(previous_path)

    def _install_mongodb(self):
        self._clean_previous_installation()
        subprocess.run(["python", "-m", "aimmocore_db.install_mongodb"], check=True)


setup(
    name="aimmocore-db",
    version="0.1.17",
    packages=find_packages(),
    cmdclass={
        "install": PostInstallCommand,
    },
)
