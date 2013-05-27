# encoding: utf-8
"""
store.py

imsto: core module

Created by liut on 2010-12-16.
Copyright (c) 2010 liut. All rights reserved.
"""

import os,re
from hashlib import md5
from numbers import Integral
from pymongo import ASCENDING, DESCENDING, MongoClient, MongoReplicaSetClient, ReadPreference
from _config import Config
from _base import base_convert
from _util import *

__all__ = ['ImSto', 'EngineError', 'UrlError', 'guessImageType']

class ImSto:
	engine = None
	_db = None
	_fs = None
	_coll = None

	def __init__(self, section='imsto'):
		"""engine: mongodb(default), s3"""
		self.section = section
		self._config = Config()

		self.engine = self.get_config('engine')
		self.fs_prefix = self.get_config('fs_prefix')
		print 'section: {self.section}, engine: {self.engine}, fs_prefix: {self.fs_prefix}'.format(self=self)

		if self.engine == 's3':
			self.bucket = self.get_config('bucket_name')
			self.AccessKey = self.get_config('s3_access_key')
			self.SecretKey = self.get_config('s3_secret_key')

	def get_config(self, key):
		return self._config.get(key, self.section)
		
	def browse(self, limit=20, start=0):
		"""retrieve files from mongodb for gallery"""
		#return fs().list()
		sort = [('updateDate',DESCENDING)]

		cursor = self.collection.find(limit=limit,skip=start,sort=sort)
		items = []
		for item in cursor:
			items.append(makeItem(item))
		return {'items':items,'total':cursor.count(),'url_prefix': self.get_config('url_prefix')}
		
	def store(self, file=None, ctype=None, content=None, name=None):
		"""save a file-like to mongodb"""
		if content is None and not hasattr(file, 'read'):
			raise TypeError('invalid file-like object')

		data = content if content is not None else file.read()
		if (len(data) > int(self.get_config('max_file_size'))):
			raise ValueError('file: {} too big'.format(name))
		ext = guessImageType(data[:32])
		if ext is None:
			raise ValueError('invalid image file')

		hashed = md5(data).hexdigest()
		print ('md5 hash: {}'.format(hashed))
		id = makeId(hashed)
		print ('id: {}'.format(id))

		# TODO: fix for support s3 front browse
		if self.fs.exists(id) or self.fs.exists(md5=hashed):
			print ('id {} or hash {} exists!!'.format(id, hashed))
			raise ValueError('already exists')
		match = re.match('([a-z0-9]{2})([a-z0-9]{2})([a-z0-9]{20,36})',id)
		filename = '{0[0]}/{0[1]}/{0[2]}.{1}'.format(match.groups(), ext)
		print ('new filename: %r' % filename)
		if ctype is None or ctype == '':
			from _util import guess_mimetype
			ctype = guess_mimetype(filename)
		spec = {'_id': id,'filename': filename, 'content_type': ctype}
		if name:
			spec['name'] = name
		return [True, self.fs.put(data, **spec), filename]
	
	def meta(self, id=None, filename=None):
		spec = None
		if id:
			spec = id
		elif filename:
			spec = {'filename': filename}
		if spec:
			print spec
			item = self.collection.find_one(spec)
			if item:
			 	return makeItem(item)
		

	def get(self, id=None, filename=None):
		"""retrieve a file by id"""
		if filename:
			item = self.meta(filename=filename)
			if item:
				id = item.id
		if id and self.exists(id):
			return self.fs.get(id)
		
	def delete(self, id):
		self.fs.delete(id)
		if self.fs.exists(id):
			return False
		return True

	def exists(self, id=None, hashed=None, filename=None):
		"""check special hash value TODO: more args"""
		if id:
			return self.fs.exists(id)
		if hashed:
			return self.collection.findOne([('md5', hashed)])
		if filename:
			return self.collection.findOne(filename=filename)

	@property
	def fs(self):
		if not self._fs:
			if self.engine == 's3':
				raise EngineError('s3 not need Fs')
			import gridfs
			self._fs = gridfs.GridFS(self.db,self.fs_prefix)

		return self._fs

	@property
	def db(self):
		if self._db is None:
			host_or_uri = self.get_config('servers')
			replica_set = self.get_config('replica_set')
			if replica_set:
				c = MongoReplicaSetClient(host_or_uri, replicaSet=replica_set,read_preference=ReadPreference.NEAREST)
			else:
				c = MongoClient(host_or_uri,read_preference=ReadPreference.NEAREST)
			self._db = c[self.get_config('db_name')]
		return self._db

	@property
	def collection(self):
		if self._coll is None:
			cn = '{0}.files'.format(self.fs_prefix)
			self._coll = self.db[cn]
		return self._coll

	def close(self):
		""" close db connection"""
		if self.db is not None:
			self.db.connection.disconnect()

	def load(self, url):
		""" load from url """
		image_url_regex = r'/(?P<size>[scwh]\d{2,4}(?P<x>x\d{2,4})?|orig)(?P<mop>[a-z])?/(?P<t1>[a-z0-9]{2})/(?P<t2>[a-z0-9]{2})/(?P<t3>[a-z0-9]{19,36})\.(?P<ext>gif|jpg|jpeg|png)$'
		match = re.search(image_url_regex, url)
		#print(image_url_regex, path, match)
		if match is None:
			raise UrlError('invalid path')

		ids = match.groupdict()
		print(ids)

		id = '{t1}{t2}{t3}'.format(**ids)
		#engine_code = config.get('engine', SECTION)
		#print('section: {}, engine: {}, path: {}, id: {}'.format(SECTION, engine_code, path, id))

		#THUMB_PATH = config.get('thumb_path', SECTION).rstrip('/')
		THUMB_ROOT = self.get_config('thumb_root').rstrip('/')
		SUPPORTED_SIZE = self.get_config('support_size').split(',')

		org_path = '{t1}/{t2}/{t3}.{ext}'.format(**ids)
		org_file = '{0}/orig/{1}'.format(THUMB_ROOT, org_path)

		if not os.path.exists(org_file):
			print('fetching file: {}'.format(org_path))
			ret = self.prepare(org_file, path=org_path, id=id)
			if ret is False:
				print('fetch failed')
				raise UrlError('id {} not found'.format(id))

		if not os.path.exists(org_file):
			raise UrlError('file not found')

		# start thumbnail image

		if ids['size'] == 'orig':
			dst_path = 'orig/{}'.format(org_path)
			dst_file = org_file
		else:
			dst_path = '{0}/{1}'.format(ids['size'], org_path)
			dst_file = '{0}/{1}'.format(THUMB_ROOT, dst_path)

			mode = ids['size'][0]
			dimension = ids['size'][1:]
			if dimension not in SUPPORTED_SIZE:
				#print('unsupported size: {} {}'.format(mode, dimension))
				raise UrlError('unsupported size')
			if ids['x'] is None:
				size = int(dimension)
				width, height = size, size
			else:
				width, height = map(int, dimension.split('x'))

			if not os.path.exists(dst_file):
				print('start thumbnail image {} {} => {}x{}'.format(mode, dimension, width, height))
				thumb_image(org_file, width, height, dst_file, mode)

			if ids['mop'] == 'w' and width < 100:
				raise UrlError('bad size')

		if ids['mop'] is not None:
			if ids['mop'] == 'w': # watermark modifier
				org_file = '{}/{}/{}'.format(THUMB_ROOT, ids['size'], org_path)
				dst_file = '{}/{}{}/{}'.format(THUMB_ROOT, ids['size'], ids['mop'], org_path)

				if watermark_image(org_file, dst_file):
					dst_path = '{}{}/{}'.format(ids['size'], ids['mop'], org_path)

			else:
				raise UrlError('bad modifier')

		#print('dst_path: {}'.format(dst_path))
		#print('dst_file: {}'.format(dst_file))

		return (dst_file, dst_path)

	def prepare(self, filename, path, id):
		if self.engine == 's3':
			from simples3 import S3Bucket, KeyNotFound
			s = S3Bucket(self.bucket, access_key=self.AccessKey, secret_key=self.SecretKey)
			key = path
			try:
				file = s.get(key)
			except KeyNotFound, e:
				print('s3: key {} not found'.format(key))
				return False
		else:
			file = self.get(id)
			if file is None:
				self.close()
				print('imsto: id {} not found'.format(id))
				return False
		save_file(file, filename)

	def url(self, path, size='orig'):
		url_prefix = self.get_config('url_prefix')
		thumb_path = self.get_config('thumb_path')
		return '{}/{}/{}/{}'.format(url_prefix.rstrip('/'), thumb_path.strip('/'), size, path)

class EngineError(Exception):
	""" Invalid Engine """
	pass

class UrlError(Exception):
	""" Invalid Url or path """
	pass


def makeId(hashed, size=None):
	"""make mongo item id by file hash value"""
	if size is None:
		return base_convert(hashed, 16, 36)
	if not isinstance(size, Integral):
		raise TypeError('expected a int, not ' + repr(size))
	if size > 255:
		size = size % 255
	return base_convert('{}{:02x}'.format(hashed, size), 16, 36)

def makeItem(item):
	newItem = item.copy()
	newItem['id'] = newItem.pop('_id')
	newItem['created'] = newItem.pop('uploadDate')
	newItem.pop('chunkSize', None)
	newItem.pop('app_id', None)
	return newItem


sig_gif = b'GIF'
sig_jpg = b'\xff\xd8\xff'
#sig_png = b'\x89\x50\x4e\x47\x0d\x0a\x1a\x0a'
sig_png = b"\211PNG\r\n\032\n"

def guessImageType(data):
	if data[:3] == sig_gif:
		return 'gif'
	elif data[:3] == sig_jpg:
		return 'jpg'
	elif data[:8] == sig_png:
		return 'png'
	else:
		return None

