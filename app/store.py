# encoding: utf-8
"""
store.py

imsto: core module

Created by liut on 2010-12-16.
Copyright (c) 2010 liut. All rights reserved.
"""

import re
import sys
import os
import getopt
from pymongo import Connection
import gridfs
from PIL import Image
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
		try:
			im = Image.open(file)
		except : #IOError
			return [False, 'invalid image file']
		
		print(im.format)
		from hashlib import md5
		data = file.read()
		hashed = md5(data).hexdigest()
		print ('md5 hash: {}'.format(hashed))
		id = self.makeId(hashed)
		print ('id: {}'.format(id))
		fs = self.getFs()
		if fs.exists(id) or fs.exists(md5=hashed):
			print ('id {} or hash {} exists!!'.format(id, hashed))
			return [False, 'exists']
		match = re.match('([a-z0-9]{2})([a-z0-9]{2})([a-z0-9]{20,36})',id)
		import mimetypes
		mimetypes.init()
		ext = mimetypes.guess_extension(ctype).replace('jpe', 'jpg')
		filename = '{0[0]}/{0[1]}/{0[2]}{1}'.format(match.groups(), ext)
		print ('new filename: %r' % filename)
		return [True, fs.put(data, _id=id, filename=filename, type=ctype,org_name=name,format=im.format), filename]
		
		
	def get(self, id):
		"""retrieve a file by id"""
		fs = self.getFs()
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
		newItem['size'] = newItem.pop('length')
		newItem.pop('chunkSize', None)
		newItem.pop('app_id', None)
		return newItem

	def getFs(self):
		if self.db is None:
			self.db = self.getDb()
		return gridfs.GridFS(self.db,config.get('fs_prefix'))

	def getDb(self):
		c = Connection(config.get('servers'),slave_okay=True)
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



help_message = '''
Usage: store.py [options] [filename]

Options:
  -i, --import     Import file to storeage
  -q, --id        get a file by id
  -l, --list       List files
  -h, --help       Show this message
  -v, --verbose    Verbose output
  -q, --quiet      Minimal output

'''


class Usage(Exception):
	def __init__(self, msg):
		self.msg = msg


def main(argv=None):
	if argv is None:
		argv = sys.argv
	
	try:
		try:
			opts, args = getopt.getopt(argv[1:], "hi:q:lv", ["help", "import=", "id=", "list", "limit=", "start="])
		except getopt.error, msg:
			raise Usage(msg)
		
		#print(opts)
		#print(args)
		action = None
		store_file = None
		# option processing
		for option, value in opts:
			if option == "-v":
				verbose = True
			if option in ("-h", "--help"):
				raise Usage(help_message)
			if option in ("-i", "--import"):
				store_file = value
				print('store file: {0}'.format(store_file))
				action = 'import'
			elif option in ("-l", "--list"):
				action = 'list'
			elif option in ("-q", "--id"):
				action = 'get'
				id = value
			else:
				pass
		if (action == 'list'):
			imsto = ImSto()
			gallery = imsto.browse()
			for img in gallery['items']:
				print("{0[filename]}\t{0[length]:8,d}".format(img))
			return 0
		elif (action == 'get') and id is not None:
			imsto = ImSto()
			if not imsto.getFs().exists(id):
				print ('not found')
				return 1
			gf = imsto.get(id)
			#print(gf)
			print ("found: {0.name}\t{0.length}".format(gf))
			
				

	except Usage, err:
		print >> sys.stderr, sys.argv[0].split("/")[-1] + ": " + str(err.msg)
		print >> sys.stderr, "\t for help use --help"
		return 2


if __name__ == "__main__":
	sys.exit(main())
