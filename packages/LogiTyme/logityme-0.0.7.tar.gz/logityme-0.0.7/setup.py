from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.0.7'
DESCRIPTION = 'LogiTyme is a Python package used to track the time spent on each function, custom functions, and the entire Python Program.'

# Setting up
setup(
    name="LogiTyme",
    version=VERSION,
    author="Aravind Kumar Vemula",
    author_email="30lmas09@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    python_requires='>=3.8',
    url="https://github.com/lmas3009/LogiTyme",
    install_requires=['terminaltables'],
    keywords=['logging', 'analyzing'],
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
