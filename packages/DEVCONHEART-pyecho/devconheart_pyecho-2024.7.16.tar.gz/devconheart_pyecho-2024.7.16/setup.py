from pathlib import Path
from setuptools import setup, find_packages
import re
import os


this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

DESCRIPTION = "Py-Echo is a Python package providing tools for easy handling of echo images in DICOM format built on top of pydicom, NumPy, MatPlotLib and Open-CV."
PACKAGE_NAME = "pyecho"
AUTHOR = "Alejandro Alcaine, PhD"
EMAIL = "lalcaine@usj.es"
GITHUB_URL = "https://github.com/aalcaineo/pyecho"

with open(os.path.join(this_directory,PACKAGE_NAME,"__init__.py"), "r") as f:
    version = ""
    while not version:
        version = re.findall('\t*\s*^__version__\s*=\s*"(\d*\.\d*\.\d*)"\n+', f.readline())

setup(
    name="DEVCONHEART_" + PACKAGE_NAME,
    packages=find_packages(exclude=['*tests*']),
    version=version[0],
    license="GNU General Public License v2.0",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    author=AUTHOR,
    author_email=EMAIL,
    url=GITHUB_URL,
    keywords=["Ultrasounds", "Biomedical Image Analysis"],
    install_requires=["pydicom>=2.3.0","matplotlib>=3.7.0","numpy>=1.23.5","opencv-python>=4.5.5.62","GDCM>=1.1","pylibjpeg>=2.0.0","pylibjpeg-libjpeg>=2.1.0"],
    python_requires=">=3.10",
    extras_require={"dev":["twine>=5.0.0"]},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "Programming Language :: Python :: 3",
    ],
    zip_safe=False,
)
