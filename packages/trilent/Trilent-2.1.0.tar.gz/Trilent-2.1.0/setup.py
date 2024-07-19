from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    readme = "\n" + fh.read()

VERSION = '2.1.0'
DESCRIPTION = 'Python GUI Framework.'

setup(
    name="Trilent",
    version=VERSION,
    author="Schkimansky",
    author_email="<ahmadchawla1432@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=readme,
    packages=find_packages(),
    install_requires=['PyQt6', 'conversa'],
    keywords=['python', 'gui', 'ui', 'framework', 'app', 'application', 'ui building', 'app development'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
