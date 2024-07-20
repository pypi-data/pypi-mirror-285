from pathlib import Path

from setuptools import setup

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

root_dir = Path(__file__).parent
long_description = root_dir.joinpath("README.md").read_text()

setup(
    name="pinkboto",
    version="0.0.50",
    description="A Colorful AWS SDK wrapper for Python",
    long_description_content_type="text/markdown",
    long_description=long_description,
    url="https://github.com/Hotmart-Org/pinkboto",
    author="Jônatas Renan Camilo Alves",
    author_email="jonatas.alves@hotmart.com",
    license_file="LICENSE.txt",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
    keywords="aws sdk api pinkboto boto",
    packages=["pinkboto"],
    install_requires=requirements,
    include_package_data=True,
    package_data={"pinkboto": ["*.yml"]},
)
