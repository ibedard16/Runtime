""" Multimedia Extensible Git package setup script """

import os
import setuptools

# TODO: Replace README.md with Runtime.md for package information
with open("README.md", "r") as fh:
    long_description = fh.read()

runtime_pkg_version = '0.0.0' if 'MEG_RUNTIME_PKG_VERSION' not in os.environ else os.environ['MEG_RUNTIME_PKG_VERSION']

required_packages = [
    'kivy>=2.0rc',
    'kivy-deps.glew',
    'kivy-deps.sdl2',
    'pillow',
    'pygit2',
    'python-dateutil',
    'requests',
    'pypiwin32'
]

setuptools.setup(
    name="meg_runtime",
    version=runtime_pkg_version,
    author="Multimedia Extensible Git",
    author_email="kyletpugh@users.noreply.github.com",
    description="Multimedia Extensible Git Runtime Library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MultimediaExtensibleGit/Runtime",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=required_packages,
    platforms=['any'],
    license='MIT'
)
