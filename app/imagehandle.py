# encoding: utf-8
"""
imagehandle.py

imsto: image handler
rule: (path) aj/3f/1ow9y7ks8w8s888kswkg8.jpg => (_id) aj3f1ow9y7ks8w8s888kswkg8
if/qp/ceq9shcskssskc888k4.jpg => ifqpceq9shcskssskc888k4
Created by liut on 2010-12-04.
Copyright (c) 2010 liut. All rights reserved.
"""
import imp
import os, re
imsto = imp.load_module('imsto', *imp.find_module('imsto',[os.path.join(os.path.dirname(__file__), '..')]))
from imsto import *
from _respond import *

config = Config()

def appImageHandle(environ, start_response):
	"""main image url process"""
	SECTION = environ.get('IMSTO_SECTION', 'imsto')
	#print 'engine_code: {0}'.format(engine_code)
	path = environ.get('PATH_INFO', '')
	image_url_regex = r'/(?P<size>[scwh]\d{2,4}(?P<x>x\d{2,4})?|orig)(?P<mop>[a-z])?/(?P<t1>[a-z0-9]{2})/(?P<t2>[a-z0-9]{2})/(?P<t3>[a-z0-9]{19,36})\.(?P<ext>gif|jpg|jpeg|png)$'
	match = re.search(image_url_regex, path)
	#print(image_url_regex, path, match)
	if match is None:
		return not_found(environ, start_response, 'invalid path')

	ids = match.groupdict()
	print(ids)

	id = '{t1}{t2}{t3}'.format(**ids)
	engine_code = config.get('engine', SECTION)
	print('section: {}, engine: {}, path: {}, id: {}'.format(SECTION, engine_code, path, id))

	THUMB_PATH = config.get('thumb_path', SECTION).rstrip('/')
	THUMB_ROOT = config.get('thumb_root', SECTION).rstrip('/')
	SUPPORTED_SIZE = config.get('support_size', SECTION).split(',')

	org_path = '{t1}/{t2}/{t3}.{ext}'.format(**ids)
	org_file = '{0}/orig/{1}'.format(THUMB_ROOT, org_path)

	if not os.path.exists(org_file):
		print('fetching file: {}'.format(org_path))
		if engine_code == 's3':
			ret = processFileS3(org_path, org_file, section=SECTION)
		else:
			ret = processFile(id, org_file, section=SECTION)

		if ret is False:
			print('fetch failed')
			return not_found(environ, start_response, message = 'id {} not found'.format(id))

	if not os.path.exists(org_file):
		return not_found(environ, start_response, message = 'file not found')

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
			print('unsupported size: {} {}'.format(mode, dimension))
			return not_found(environ, start_response, message = 'unsupported size')
		if ids['x'] is None:
			size = int(dimension)
			width, height = size, size
		else:
			width, height = map(int, dimension.split('x'))

		if not os.path.exists(dst_file):
			print('start thumbnail image {} {} => {}x{}'.format(mode, dimension, width, height))
			thumb_image(org_file, width, height, dst_file, mode)

		if ids['mop'] == 'w' and width < 100:
			return not_found(environ, start_response, message = 'bad size')

	if ids['mop'] is not None:
		if ids['mop'] == 'w': # watermark modifier
			org_file = '{}/{}/{}'.format(THUMB_ROOT, ids['size'], org_path)
			dst_file = '{}/{}{}/{}'.format(THUMB_ROOT, ids['size'], ids['mop'], org_path)

			if watermark_image(org_file, dst_file):
				dst_path = '{}{}/{}'.format(ids['size'], ids['mop'], org_path)

		else:
			return not_found(environ, start_response, message = 'bad modifier')


	print('dst_path: {}'.format(dst_path))
	#print('dst_file: {}'.format(dst_file))
	server_soft = environ.get('SERVER_SOFTWARE','')
	if server_soft[:5] == 'nginx' and os.name != 'nt':
		#print('{0}/{1}'.format(THUMB_PATH, dst_path))
		start_response('200 OK', [('X-Accel-Redirect', '{0}/{1}'.format(THUMB_PATH, dst_path))])
		return []
	#print(file.type) 
	mimetype = guess_mimetype(dst_path)
	filesize = os.path.getsize(dst_file)
	headers = [('Content-Type', str(mimetype)), ('Content-Length', '{0}'.format(filesize)), ('Via','imsto')]
	#print(headers)
	start_response('200 OK', headers)
	fd = open(dst_file,'r')
	return environ['wsgi.file_wrapper'](fd, 4096)

def processFile(id, filename, section='imsto'):
	imsto = ImSto(section)
	file = imsto.get(id)
	if file is None:
		imsto.close()
		print('imsto: id {} not found'.format(id))
		return False
	save_file(file, filename)
	imsto.close()
	return True

def processFileS3(key, filename, section='imsto'):
	bucket = config.get('bucket_name', section)
	AccessKey = config.get('s3_access_key', section)
	SecretKey = config.get('s3_secret_key', section)

	from simples3 import S3Bucket, KeyNotFound
	s = S3Bucket(bucket, access_key=AccessKey, secret_key=SecretKey)

	try:
		file = s.get(key)
	except KeyNotFound, e:
		print('s3: key {} not found'.format(key))
		return False
	save_file(file, filename)
	return True


if __name__ == '__main__':
	from wsgiref.simple_server import make_server
	httpd = make_server('', 8000, appImageHandle)
	print("Listening on port 8000....\n image url example: http://localhost:8000/aj/3f/1ow9y7ks8w8s888kswkg8.jpg\n")
	httpd.serve_forever()

else:
	from errorhandle import ErrorHandle
	application = ErrorHandle(appImageHandle)
	
