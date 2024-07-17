from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "DESCRIPTION.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.0.4'
DESCRIPTION = 'Schedule tasks troughout the day.'
LONG_DESCRIPTION = 'A package that allows you to schedule tasks throughout the day.'

# Setting up
setup(
    name="dailyscheduler",
    version=VERSION,
    author="NumenMirus",
    author_email="<numenmirus@proton.me>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=[],
    keywords=['day', 'scheduler', 'tasks', 'schedule', 'time'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)