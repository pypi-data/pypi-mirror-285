import subprocess
import sys
from setuptools import setup, find_packages
from setuptools.command.install import install as _install
from setuptools.command.develop import develop as _develop
from setuptools.command.egg_info import egg_info as _egg_info

setup(
    name='behavior-eval',
    version='1.0.6',
    author='stanford',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url="https://github.com/embodied-agent-eval/behavior-eval",
    packages=find_packages(),
    python_requires='>=3.8',
    install_requires=[
        "fire",
        "lark",
        "bddl-eval",
        "pyquaternion",
    ],
    include_package_data=True,
    package_data={
        '': ['*.json', '*.xml', '*.md', '*.yaml'],
    },
)
