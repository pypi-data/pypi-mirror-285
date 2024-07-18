from pathlib import Path
from setuptools import setup, find_packages
import re
import os


this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

DESCRIPTION = "A Python package to provide easy to use tools to learn and teach digital (biomedical) image processing with Python."
PACKAGE_NAME = "diptools"
AUTHOR = "Alejandro Alcaine, PhD"
EMAIL = "lalcaine@usj.es"
GITHUB_URL = "https://github.com/aalcaineo/diptools"

with open(os.path.join(this_directory,PACKAGE_NAME,"__init__.py"), "r") as f:
    version = ""
    while not version:
        version = re.findall('\t*\s*^__version__\s*=\s*"(\d*\.\d*\.\d*)"\n+', f.readline())

setup(
    name="USJ_" + PACKAGE_NAME,
    packages=find_packages(exclude=['*tests*']),
    version=version[0],
    license="GNU General Public License v2.0",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    author=AUTHOR,
    author_email=EMAIL,
    url=GITHUB_URL,
    keywords=["Digital Signal Processing"],
    install_requires=["matplotlib>=3.7.0","numpy>=1.23.5","opencv-python>=4.9.0"],
    python_requires=">=3.10",
    extras_require={"dev":["twine>=4.0.2"]},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "Programming Language :: Python :: 3",
    ],
    zip_safe=False,
)
