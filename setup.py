""" Multimedia Extensible Git package setup script """

import os
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

runtime_pkg_version = '0.0.0'
if 'MEG_RUNTIME_PKG_VERSION' in os.environ:
    runtime_pkg_version = os.environ['MEG_RUNTIME_PKG_VERSION']

setuptools.setup(
    name="meg_runtime",
    version=runtime_pkg_version,
    author="Multimedia Extensible Git",
    author_email="kyletpugh@users.noreply.github.com",
    description="Multimedia Extensible Git Runtime Library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MultimediaExtensibleGit",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)
