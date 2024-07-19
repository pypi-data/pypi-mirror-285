"""
SimBA (Simple Behavioral Analysis)
https://github.com/sgoldenlab/simba
Contributors.
https://github.com/sgoldenlab/simba#contributors-
Licensed under GNU Lesser General Public License v3.0
"""

import setuptools
import platform
from setuptools.command.install import install
from setuptools.command.egg_info import egg_info
import logging


M_CHIP = 'arm'
DARWIN = 'darwin'
M_CHIP_INCOMPATIBLE_PKG = ['cefpython3 == 66.0']

with open("docs/project_description.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as f:
    requirements = f.read().splitlines()

processor = platform.processor()
system = platform.system()
machine = platform.machine()
python_version = platform.python_version()

pre_install_statement = f'Installing SimBA. \n ' \
                        f'CPU: {processor} \n ' \
                        f'System: {system} \n' \
                        f'Machine: {machine} \n' \
                        f'Python version: {python_version} \n'

class PreInstallCommand(setuptools.Command):
    """Pre-installation command."""
    description = 'Run pre-installation tasks'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        logging.basicConfig(level=logging.INFO)
        logging.info(pre_install_statement)

class CustomInstallCommand(install):
    """Customized setuptools install command - prints a pre-install statement."""
    def run(self):
        self.run_command('pre_install')
        install.run(self)

class CustomEggInfoCommand(egg_info):
    """Customized setuptools egg_info command - prints a pre-install statement."""
    def run(self):
        self.run_command('pre_install')
        egg_info.run(self)

if M_CHIP in processor.lower() and DARWIN in system.lower():
    requirements = [x for x in requirements if x not in M_CHIP_INCOMPATIBLE_PKG]

exclusion_patterns = ["pose_configurations_archive"]

setuptools.setup(
    name="Simba-UW-tf-dev",
    version="1.97.2",
    author="Simon Nilsson, Jia Jie Choong, Sophia Hwang",
    author_email="sronilsson@gmail.com",
    description="Toolkit for computer classification of behaviors in experimental animals",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sgoldenlab/simba",
    install_requires=requirements,
    license='GNU General Public License v3 (GPLv3)',
    packages=setuptools.find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests", "__pycache__", "pose_configurations_archive"]),
    include_package_data=True,
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: OS Independent",
    ),
    entry_points={'console_scripts':['simba=simba.SimBA:main'],},
    cmdclass={'pre_install': PreInstallCommand,
              'install': CustomInstallCommand,
              'egg_info': CustomEggInfoCommand,}
)