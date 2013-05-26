import os
from setuptools import setup
from imsto import __version__, __author__, __author_email__

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
	return open(os.path.join(os.path.dirname(__file__), fname)).read()

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
	install_requires=['pymongo>=2.5'],
	long_description=read('README.md'),
)

