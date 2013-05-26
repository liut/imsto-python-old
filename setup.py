import os
from setuptools import setup
from imsto import __version__, __author__, __author_email__

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
	return open(os.path.join(os.path.dirname(__file__), fname)).read()

CLASSIFIERS = [
    "Development Status :: 3 - Alpha",
    "Environment :: Console",
    "Environment :: Web Environment",
    "Intended Audience :: Customer Service",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: BSD License",
    "Operating System :: MacOS :: MacOS X",
    "Operating System :: POSIX :: Linux",
    "Programming Language :: JavaScript",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2.7",
    "Topic :: Communications :: File Sharing",
    "Topic :: Internet",
    "Topic :: Multimedia :: Graphics",
    "Topic :: Utilities",
]

setup(
	name = "imsto",
	version = __version__,
	author = __author__,
	author_email = __author_email__,
	description = ("a little image storage"),
	license = "BSD",
	keywords = "imsto image storage",
	url = "http://github.com/liut/imsto",
	packages=['imsto'],
	install_requires = ['pymongo>=2.5'],
	long_description = read('README.md'),
    classifiers = CLASSIFIERS,
)

