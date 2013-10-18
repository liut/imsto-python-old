import os
import itertools
from django.core.files.storage import Storage
from django.conf import settings
from imsto import load_imsto
from urlparse import urljoin

MIN_PATH_LEN = 28

class ImageStorage(Storage):
	"""A custom storage backend to store files in GridFS

		to use this backend, change your settings.py:

			DEFAULT_FILE_STORAGE = 'imsto.django.ImageStorage'

	"""

	def __init__(self, base_url=None):

		if base_url is None:
			base_url = settings.MEDIA_URL
		self.base_url = base_url
		self.imsto = load_imsto()
		self.field = 'image_path'

	def delete(self, name):
		"""Deletes the specified file from the storage system.
		TODO:
		"""
		pass

	def exists(self, name):
		"""Returns True if a file referened by the given name already exists in the
		storage system, or False if the name is available for a new file.
		"""
		image = self.imsto.exists(filename=name)
		return bool(image.name)

	def listdir(self, path=None):
		"""Lists the contents of the specified path, returning a 2-tuple of lists;
		the first item being directories, the second item being files.
		"""
		return self.imsto.browse(limit=20,start=0)

	def size(self, name):
		"""Returns the total size, in bytes, of the file specified by name.
		"""
		img = self.imsto.get(filename=name)
		if img:
			return img.length
		else:
			raise ValueError("No such file or directory: '%s'" % name)

	def url(self, name, size='orig'):
		"""Returns an absolute URL where the file's contents can be accessed
		directly by a web browser.
		"""
		if len(name) > MIN_PATH_LEN and name[2] == name[5] == '/':
			return self.imsto.url(name, size)
		return urljoin(self.base_url, name).replace('\\', '/')

	def _open(self, name, mode='rb'):
		img = self.imsto.get(filename=name)
		if img:
			return img
		else:
			raise ValueError("No file found with the name '%s'." % name)

	def get_available_name(self, name):
		"""Returns a filename that's free on the target storage system, and
		available for new content to be written to.
		"""
		print 'src name: %s' % name
		return os.path.basename(name)


	def _save(self, name, content):
		print 'available name: %s' % name
		print 'type of content: %s' % type(content)
		if hasattr(content, 'temporary_file_path'):
			file = content.temporary_file_path()
			print 'temp file: %s' % file
		r, id, filename = self.imsto.store(content.file,name=name)

		print 'stored {}, {}, {}'.format(r, id, filename)
		if r:
			return filename
		return None
