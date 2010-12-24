# encoding: utf-8
"""
store.py

imsto: core module

Created by liut on 2010-12-16.
Copyright (c) 2010 liut. All rights reserved.
"""

import re
import _config
config = _config.Config()

class ImSto:
	db = None
	def __init__(self):
		pass
		
	def browse(self, limit=20, start=0):
		"""retrieve files from mongodb for gallery"""
		#return getFs().list()
		sort = [('updateDate',-1)]
		coll = self.getCollection()
		cursor = coll.find(limit=limit,skip=start,sort=sort)
		items = []
		for item in cursor:
			items.append(self.makeItem(item))
		return {'items':items,'total':cursor.count(),'url_prefix': config.get('url_prefix')}
		
	def store(self, file, ctype, name):
		"""save a file to mongodb"""
		if not hasattr(file, 'read'):
			raise TypeError('invalid file-like object')
		if ctype is None or ctype == '':
			raise ValueError('invalid content type value')
		#try:
		#	im = Image.open(file)
		#except : #IOError
		#	return [False, 'invalid image file']
		
		#print(im.format)
		data = file.read()
		if (len(data) > int(config.get('max_file_size'))):
			return [False, 'file: {} too big'.format(name)]
		ext = getImageType(data[:32])
		if ext is None:
			return [False, 'invalid image file']
		from hashlib import md5
		hashed = md5(data).hexdigest()
		print ('md5 hash: {}'.format(hashed))
		id = self.makeId(hashed)
		print ('id: {}'.format(id))
		fs = self.getFs()
		if fs.exists(id) or fs.exists(md5=hashed):
			print ('id {} or hash {} exists!!'.format(id, hashed))
			return [False, 'exists']
		match = re.match('([a-z0-9]{2})([a-z0-9]{2})([a-z0-9]{20,36})',id)
		filename = '{0[0]}/{0[1]}/{0[2]}.{1}'.format(match.groups(), ext)
		print ('new filename: %r' % filename)
		return [True, fs.put(data, _id=id, filename=filename, type=ctype,note=name), filename]
		
		
	def get(self, id):
		"""retrieve a file by id"""
		fs = self.getFs()
		if fs.exists(id):
			return fs.get(id)
		
	def delete(self, id):
		fs = self.getFs()
		fs.delete(id)
		if fs.exists(id):
			return False
		return True

	def exists(self, hashed):
		"""check special hash value """
		coll = self.getCollection()
		return coll.findOne([('md5', hashed)])

	def makeId(self, hashed):
		"""make mongo item id by file hash value"""
		from _base import base_convert
		return base_convert(hashed, 16, 36)

	def makeItem(self, item):
		newItem = item.copy()
		newItem['id'] = newItem.pop('_id')
		newItem['created'] = newItem.pop('uploadDate')
		newItem.pop('chunkSize', None)
		newItem.pop('app_id', None)
		return newItem

	def getFs(self):
		import gridfs
		if self.db is None:
			self.db = self.getDb()
		return gridfs.GridFS(self.db,config.get('fs_prefix'))

	def getDb(self):
		from pymongo import Connection
		c = Connection(config.get('servers'))
		return c[config.get('db_name')]

	def getCollection(self):
		if self.db is None:
			self.db = self.getDb()
		cn = '{0}.files'.format(config.get('fs_prefix'))
		return self.db[cn]

	def close(self):
		""" close db connection"""
		if self.db is not None:
			self.db.connection.disconnect()


sig_gif = b'GIF'
sig_jpg = b'\xff\xd8\xff'
#sig_png = b'\x89\x50\x4e\x47\x0d\x0a\x1a\x0a'
sig_png = b"\211PNG\r\n\032\n"

def getImageType(data):
	if data[:3] == sig_gif:
		return 'gif'
	elif data[:3] == sig_jpg:
		return 'jpg'
	elif data[:8] == sig_png:
		return 'png'
	else:
		return None

