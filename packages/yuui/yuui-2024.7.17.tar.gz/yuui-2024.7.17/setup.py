import codecs
import os

from setuptools import find_packages, setup

# these things are needed for the README.md show on pypi
here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()


VERSION = '2024.7.17'
DESCRIPTION = 'A program based on pygame.You can use it made GUI program easily.'
LONG_DESCRIPTION = 'A program based on pygame.You can use it made GUI program easily.Support Windows,Macos and Linux'

# Setting up
setup(
    name="yuui",
    version=VERSION,
    author="yuzijiang",
    author_email="Toy142hjkl@hotmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=[],
    keywords=['python', 'menu', 'yuui','pygame','gui','yuzijiang','windows','macos','linux'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
