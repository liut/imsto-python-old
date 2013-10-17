# encoding: utf-8
"""
store.py

imsto: core module

Created by liut on 2010-12-16.
Copyright (c) 2010-2013 liut. All rights reserved.
"""

import os,re,datetime
from urlparse import urljoin
from hashlib import md5
from numbers import Integral
from pymongo import ASCENDING, DESCENDING, MongoClient, MongoReplicaSetClient, ReadPreference
from _config import Config
from _base import base_convert
from _util import *

__all__ = [
	'load_imsto',
	'EngineError', 'UrlError', 'HttpFound', 'DuplicateError', 
]

def load_imsto(section='imsto'):
	config = Config()
	engine = config.get('engine', section)
	print 'loading {} engine: {}'.format(section, engine)
	if engine == 'mongodb':
		return StoreEngineGridFs(section)
	if engine == 's3':
		return StoreEngineS3(section)
	if engine == 'weedfs':
		return StoreEngineWeedFs(section)
	raise ValueError('bad engine_code')

class StoreBase:
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
		print 'init section: {self.section}, engine: {self.engine}, fs_prefix: {self.fs_prefix}'.format(self=self)

	def get_config(self, key):
		return self._config.get(key, self.section)
		
	def browse(self, limit=20, start=0, sort=None, only_items = False):
		"""retrieve files from mongodb for gallery"""
		#return fs().list()
		if sort is None or not isinstance(sort, list):
			sort = [('uploadDate',DESCENDING)]

		cursor = self.collection.find(limit=limit,skip=start,sort=sort)
		items = [StoreItem(self, item) for item in cursor]
		if only_items:
			return items
		url_prefix = urljoin(self.get_config('url_prefix'), self.get_config('thumb_path'))
		return {'items':items,'total':cursor.count(),'url_prefix': url_prefix + '/'}

	def count(self):
		return self.collection.count();

	# def __iter__(self):
	# 	self.__cursor = self.collection.find(limit=0,skip=0,sort=[('uploadDate',DESCENDING)])
	# 	return self
	# def next(self):
	# 	if self.__cursor:
	# 		return StoreItem(self, self.__cursor.next())
	# 	raise StopIteration

	def store(self, file=None, content=None, ctype=None, **kwd):
		"""save a file-like item"""
		if content is None and not hasattr(file, 'read'):
			raise TypeError('invalid file-like object')

		data = content if content is not None else file.read()
		size = len(data)
		ext = guessImageType(data[:32])
		if ext is None:
			raise ValueError('invalid image file')

		hashes = [md5(data).hexdigest()]
		_exists_id = self.exists(hashed=hashes[0])
		if _exists_id:
			id = _exists_id
			filename = _make_filename(id, ext)
			print ('id {} or hash {} exists!!'.format(id, hashes[0]))
			#raise DuplicateError('already exists')
			return [True, id, filename, 0]
		ids = [_make_id(hashes[0])]
		if 'id' in kwd and kwd['id'] and kwd['id'] not in ids:
			ids += [kwd['id']]

		from image import SimpImage, MIN_QUALITY

		max_file_size = int(self.get_config('max_file_size'))
		max_jpeg_quality = int(self.get_config('max_jpeg_quality'))
		max_width = int(self.get_config('max_width'))
		max_height = int(self.get_config('max_height'))

		if size > max_file_size: max_jpeg_quality -= 1
		if max_jpeg_quality < MIN_QUALITY: max_jpeg_quality = MIN_QUALITY

		im = SimpImage(blob=data)
		meta = im.meta
		if meta['width'] > max_width or meta['height'] > max_height:
			if self.get_config('auto_scale') and im.thumbnail(max_width, max_height):
				if im.format == 'JPEG' and im.quality > max_jpeg_quality:
					im.quality = max_jpeg_quality
				data = im.get_blob()
				size = len(data)
				print im.meta
				print 'new scaled size {}'.format(size)
				hashes += [md5(data).hexdigest()]
			else:
				raise ValueError('file: {} dimension {}x{} is too big, max is {}x{}'.format(kwd['name'] if 'name' in kwd else '', meta['width'], meta['height'], max_width, max_height))

		if im.format == 'JPEG':
			if im.quality > max_jpeg_quality:
				print 'quality {} is too high, hash {}'.format(im.quality, hashes[0])
				from tempfile import NamedTemporaryFile
				_tmp = NamedTemporaryFile('w+b',dir=self.get_config('temp_root'),delete=False)
				_tmp.file.close()
				save_file(_tmp.name, blob=data)
				if jpegoptim(_tmp.name):
					fp = open(_tmp.name)
					data = fp.read()
					size = len(data)

					# print 'new optimized size {}'.format(size)
					fp.close()
					_tmp.unlink(_tmp.name)
					del im
					im = SimpImage(blob=data)
					meta = im.meta
					hashes += [md5(data).hexdigest()]
				else:
					raise EnvironmentError('jpeg qualty is too high, or need jpegoptim')
		elif im.format == 'PNG' and self.get_config('force_jpeg'):
			im.format = 'JPEG'
			im.quality = max_jpeg_quality
			data = im.get_blob()
			size = len(data)
			hashes += [md5(data).hexdigest()]
			ext = 'jpg'
			meta = im.meta
		del im

		if (size > max_file_size):
			raise ValueError('file: {} size {} is too big, max is {}'.format(kwd['name'] if 'name' in kwd else '', size, max_file_size))

		hashed = hashes[len(hashes)-1] #md5(data).hexdigest()
		# print ('md5 hash: {}'.format(hashed))

		# TODO: add for support (md5 + size) id
		id = _make_id(hashed)

		# print ('new filename: %r' % filename)

		# TODO: fix for support s3 front browse
		_exists_id = self.exists(id) or self.exists(hashed=hashed)
		if _exists_id:
			id = _exists_id
			filename = _make_filename(id, ext)
			print ('id {} or hash {} exists!!'.format(id, hashed))
			#raise DuplicateError('already exists')
			return [True, id, filename]
		filename = _make_filename(id, ext)
		# print ('id: {}'.format(id))

		# if ctype is None or ctype == '':
		from _util import guess_mimetype
		ctype = guess_mimetype(filename)

		# save to mongodb
		spec = {'_id': id,'filename': filename, 'hash': hashes, 'mime': ctype, 'size': size, 'meta': meta, 'ids': ids}

		if 'name' in kwd and isinstance(kwd['name'], (str, unicode)):
			spec['name'] = kwd['name']

		for k in ['created', 'app_id']:
			if k in kwd and kwd[k]:
				spec[k] = kwd[k]

		if self._store_exists(id, filename=filename):
			self._save_meta(id, spec)
			return [True, id, filename]

		rr = self._put(data, **spec)
		if rr:
			return [True, rr, filename]
	
	def get_meta(self, id=None, filename=None, ids=None):
		spec = None
		if id:
			spec = id
		elif filename:
			spec = {'filename': filename}
		elif ids and isinstance(ids, type([])):
			spec = {'ids': {'$in': ids}}

		if spec:
			print 'spec %s' % spec
			item = self.collection.find_one(spec)
			if item:
			 	return StoreItem(self, item)

	def _save_meta(self, id, spec):
		'''mongo special meta data'''
		#if not hasattr(spec, '_id'):
		#	spec['_id'] = id
		if 'created' not in spec:
			spec['created'] = datetime.datetime.utcnow()

		if 'filename' not in spec:
			print spec
			raise ValueError('need filename')

		return self.collection.update({'_id': id}, spec, upsert=True)

	def delete(self, id):
		raise NotImplemented()

	def _get(self, id):
		raise NotImplemented()

	def _put(self, data, **spec):
		raise NotImplemented()

	def _store_exists(self, id=None, *args, **kwargs):
		raise NotImplemented()

	def exists(self, id=None, hashed=None, filename=None, *args, **kwargs):
		"""check special hash value TODO: more args"""
		#print args
		#print kwargs
		if id and self.collection.find_one({"_id": id}):
			return id
		if hashed:
			doc = self.collection.find_one({'md5': hashed})
			if doc:
				return doc['_id']
			doc = self.collection.find_one({'hash': {'$in': [hashed]}})
			if doc:
				return doc['_id']

		if filename:
			doc = self.collection.find_one(filename=filename)
			if doc:
				return doc['_id']

		if self._store_exists(id, hashed=hashed, filename=filename, *args, **kwargs):
			return id

	@property
	def db(self):
		if self._db is None:
			self._db = get_mongo_db(self.get_config('servers'), self.get_config('db_name'), self.get_config('replica_set'))
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

	def load(self, path):
		""" load from url path """
		#print 'path: %s (%s)' % (path, type(path))
		image_url_regex = r'(?P<size>[scwh]\d{2,4}(?P<x>x\d{2,4})?|orig)(?P<mop>[a-z])?/(?P<t1>[a-z0-9]{2})/(?P<t2>[a-z0-9]{2})/(?P<t3>[a-z0-9]{19,36})\.(?P<ext>gif|jpg|jpeg|png)$'
		match = re.search(image_url_regex, path)
		#print(image_url_regex, path, match)
		if match is None:
			raise UrlError('invalid path')

		ids = match.groupdict()
		#print(ids)

		id = '{t1}{t2}{t3}'.format(**ids)

		THUMB_ROOT = self.get_config('thumb_root').rstrip('/')
		SUPPORTED_SIZE = self.get_config('support_size').split(',')

		org_path = '{t1}/{t2}/{t3}.{ext}'.format(**ids)
		org_file = '{0}/orig/{1}'.format(THUMB_ROOT, org_path)

		if not os.path.exists(org_file):

			# check old id for redirect
			doc = self.get_meta(ids=[id])
			if doc and doc['id'] != id and 'filename' in doc:
				print 'found %s' % doc['filename']
				thumb_path = self.get_config('thumb_path')
				new_path = '{}/{}/{}'.format(thumb_path, ids['size'], doc['filename'])
				raise HttpFound('found', path=new_path)

			print('fetching file: {}'.format(org_path))
			file = self.fetch(id, path=org_path)
			if file is None:
				print('fetch failed')
				raise UrlError('id {} not found'.format(id))
			save_file(org_file, file)

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

	def fetch(self, id, path):
		key = path if self.engine == 's3' else id

		return self._get(key)
		# try:
		# 	return self._get(key)
		# except Exception, e:
		# 	print('prepare: {} not found'.format(key))
		# 	print e
		# 	raise e
		


	def url(self, path, size='orig'):
		url_prefix = self.get_config('url_prefix')
		thumb_path = self.get_config('thumb_path')
		return '{}/{}/{}/{}'.format(url_prefix.rstrip('/'), thumb_path.strip('/'), size, path)

class StoreItem(dict):
	"""docstring for Item"""
	imsto = None
	id = None
	def __init__(self, imsto, meta):
		self.imsto = imsto
		if isinstance(meta, dict):
			item = self._fix_meta(meta)
			for key, value in item.iteritems():
				self[key.lower()] = value
				if key == 'id':
					self.id = value
			# if not self.has_key('name') or self['name'] is None:
			# 	self.name = self.id + guess_ext(self['mime'])

	def __getattr__(self, name):
		if name == 'dict':
			return self
		else:
			return self.get(name, None)

	def _fix_meta(self, item):
		'''convert mongo item to simple'''
		item['id'] = item.pop('_id')
		if item.has_key('length'):
			item['size'] = item.pop('length')
		elif item.has_key('content_length'):
			item['size'] = item.pop('content_length')
		if item.has_key('uploadDate'):
			item['created'] = item.pop('uploadDate')
		if item.has_key('contentType'):
			item['mime'] = item.pop('contentType')
		if item.has_key('content_type'):
			item['mime'] = item.pop('content_type')
		if not item.has_key('filename') and item.has_key('path'):
			item['filename'] = item.pop('path')
		item.pop('chunkSize', None)
		item.pop('app_id', None)
		if item.has_key('md5') and not item.has_key('hash'):
			item['hash'] = [item['md5']]
			# item.pop('md5', None)
		# print item
		return item

	@property
	def file(self):
		return self.imsto._get(self)


class EngineError(Exception):
	""" Invalid Engine """
	pass

class UrlError(Exception):
	""" Invalid Url or path """
	pass

class HttpFound(Exception):
	""" TODO: path has been changed """

	def __init__(self, message, path, **kwds):
		self.args = message, kwds.copy()
		self.msg, self.extra = self.args
		self.path = path


class DuplicateError(Exception):
	""" Entry Duplicated """
	pass

def get_mongo_db(host_or_uri, db_name, replica_set = None):
	if replica_set:
		c = MongoReplicaSetClient(host_or_uri, replicaSet=replica_set,read_preference=ReadPreference.NEAREST)
	else:
		c = MongoClient(host_or_uri,read_preference=ReadPreference.NEAREST)
	return c[db_name]

def _make_id(hashed, size=None):
	"""make mongo item id by file hash value"""
	if size is None or size < 1:
		return base_convert(hashed, 16, 36)
	if not isinstance(size, Integral):
		raise TypeError('expected a int, not ' + repr(size))
	return base_convert('{}{:02x}'.format(hashed, size % 255), 16, 36)

def _make_filename(id, ext):
	match = re.match('([a-z0-9]{2})([a-z0-9]{2})([a-z0-9]{16,36})',id)
	if match:
		return '{0[0]}/{0[1]}/{0[2]}.{1}'.format(match.groups(), ext)
	raise ValueError('invalid id %s' % id)
	# return id + '.' + ext


class StoreEngineGridFs(StoreBase):
	"""docstring for StoreEngineGridFs"""
	_db = None
	_fs = None
	def __init__(self, section):
		StoreBase.__init__(self, section)

	def _get(self, id):
		if isinstance(id, StoreItem):
			id = id.id
		if id and self.exists(id):
			return self.fs.get(id)
	
	def delete(self, id):
		self.fs.delete(id)
		if self.fs.exists(id):
			return False
		return True

	def _put(self, data, **spec):
		return self.fs.put(data, **spec)

	def _store_exists(self, id=None, *args, **kwargs):
		#print id
		return self.fs.exists(id)

	@property
	def fs(self):
		if not self._fs:
			import gridfs
			self._fs = gridfs.GridFS(self.db,self.fs_prefix)

		return self._fs

class StoreEngineS3(StoreBase):
	"""docstring for StoreEngineS3"""
	_bucket = None
	def __init__(self, section):
		StoreBase.__init__(self, section)

	def _get(self, id):
		if isinstance(id, str):
			if id.rfind('.') > 0:
				key = id
			else:
				item = self.get_meta(id)
				if item:
					key = item.filename
					# print 'found %s' % item
		elif isinstance(id, StoreItem):
			key = id.filename
		else:
			raise ValueError('invalid id or key')
		return self.bucket.get(key)

	def delete(self, id):
		key = None
		if isinstance(id, str):
			item = self.get_meta(id)
			if item:
				print 'found item id: %s' % id
				key = item.filename
		elif isinstance(id, StoreItem):
			key = id.filename
			id = id.id
		else:
			raise ValueError('invalid id or key')
		if key is not None and id and self.bucket.delete(key):
			print 'delete filename: %s ok' % key
		 	r = self.collection.remove(id,safe=True)
		 	return 'ok' in r and r['err'] is None
		return False

	def _put(self, data, **spec):

		metadata = {}
		for k in spec['meta']:
			metadata[k] = str(spec['meta'][k])

		if 'name' in spec and isinstance(spec['name'], (str, unicode)):
			from urllib import quote_plus
			metadata['name'] = quote_plus(spec['name'].encode('utf-8') if isinstance(spec['name'], unicode) else spec['name'])
			# print metadata['name']

		headers = {'Content-Length': spec['size']}
		try:
			filename = spec['filename']
			self.bucket.put(filename, data=data, mimetype=spec['mime'], metadata=metadata, headers=headers)
			print "save ok %s to s3" % filename
			self._save_meta(spec['_id'], spec)
			print "save ok meta %s" % spec['_id']
			return spec['_id']
		except Exception, e:
			raise e
		

	def _store_exists(self, id=None, *args, **kwargs):
		if 'filename' in kwargs and kwargs['filename'] is not None:
			return kwargs["filename"] in self.bucket
		return False

	@property
	def bucket(self):
		if self._bucket is None:
			from simples3 import S3Bucket, KeyNotFound
			bucket_name = self.get_config('bucket_name')
			if bucket_name is None:
				raise ValueError("no bucket_name in section '%s'" % self.section)
			access_key = self.get_config('s3_access_key')
			secret_key = self.get_config('s3_secret_key')
			self._bucket = S3Bucket(bucket_name, access_key=access_key, secret_key=secret_key)
		return self._bucket

WEED_HOST = 'weed_vol_host'
WEED_FID = 'weed_fid'

class StoreEngineWeedFs(StoreBase):
	"""docstring for StoreEngineWeedFs"""
	def __init__(self, section):
		StoreBase.__init__(self, section)
		from weedfs import WeedClient
		self.client = WeedClient()

	def _get(self, id):
		print '_get {}'.format(id)
		item = id if isinstance(id, StoreItem) else self.get_meta(id)
		if not item.has_key(WEED_HOST) or not item.has_key(WEED_HOST):
			raise ValueError('the entry has no special value ' + WEED_HOST + ' and ' + WEED_FID)
		volume_host, fid = item[WEED_HOST], item[WEED_FID]
		ctype, size, content = self.client.retrieve(volume_host, fid)
		print 'weed retrieved: %s %s' % (ctype, size)
		if content:
			from StringIO import StringIO
			return StringIO(content)
		raise ValueError('weed client.retrieve error: invalid response')

	def delete(self, id):
		raise NotImplemented()

	def _put(self, data, **spec):
		volume_host, fid = self.client.assign()
		ret = self.client.store(volume_host, fid, content=data, name=spec['filename'], content_type=spec['mime'])
		if isinstance(ret, int) and ret > 0:
			print 'saved {}/{} size {} bytes'.format(volume_host, fid, ret)
			spec[WEED_HOST] = volume_host
			spec[WEED_FID] = fid
			self._save_meta(spec['_id'], spec)
			return spec['_id']
		print 'store error: %s' % ret
		

	def _store_exists(self, id=None, *args, **kwargs):
		if hasattr(kwargs, WEED_HOST) and hasattr(kwargs, WEED_FID):
			ctype, size = self.client.retrieve(kwargs[WEED_HOST],kwargs[WEED_FID], head=True)
			print 'exists %s %s' % (ctype, size)
			return True
		return False



