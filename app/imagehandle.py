# encoding: utf-8
"""
imagehandle.py

imsto: image handler
rule: (path) aj/3f/1ow9y7ks8w8s888kswkg8.jpg => (_id) aj3f1ow9y7ks8w8s888kswkg8
if/qp/ceq9shcskssskc888k4.jpg => ifqpceq9shcskssskc888k4
Created by liut on 2010-12-04.
Copyright (c) 2010 liut. All rights reserved.
"""


from _util import *
import _config, os, re

config = _config.Config()

THUMB_PATH = config.get('thumb_path').rstrip('/')
THUMB_ROOT = config.get('thumb_root').rstrip('/')
SUPPORTED_SIZE = eval(config.get('support_size'))

from _respond import not_found

def appImageHandle(environ, start_response):
	"""main image url process"""
	engine_code = environ.get('IMSTO_ENGINE', 'default')
	print 'engine_code: {0}'.format(engine_code)
	path = environ.get('PATH_INFO', '')
	image_url_regex = r'/([a-z0-9]{2})/([a-z0-9]{2})/([a-z0-9]{19,36})(-[scwh]\d{2,4})?\.(gif|jpg|jpeg|png)$'
	match = re.search(image_url_regex, path)
	#print(image_url_regex, path, match)
	if match is None:
		return not_found(environ, start_response, 'invalid path')

	ids = match.groups()
	#print(ids)
	id = '{0}{1}{2}'.format(*ids)
	#print(id)
	org_path = '{0}/{1}/{2}.{4}'.format(*ids)
	org_file = '{0}/{1}'.format(THUMB_ROOT, org_path)

	if not os.path.exists(org_file):
		if engine_code == 's3':
			ret = processFileS3(org_path, org_file)
		else:
			ret = processFile(id, org_file)

		if ret is False:
			return not_found(environ, start_response, message = 'id not found')

	if not os.path.exists(org_file):
		return not_found(environ, start_response, message = 'file not found')

	if ids[3] is None:
		dst_path = org_path
		dst_file = org_file
	else:
		dst_path = '{0}/{1}/{2}{3}.{4}'.format(*ids)
		dst_file = '{0}/{1}'.format(THUMB_ROOT, dst_path)
		#print(ids[3][1:])
		mode = ids[3][1]
		size = int(ids[3][2:])
		if size not in SUPPORTED_SIZE:
			print('unsupported size: {0}'.format(size))
			return not_found(environ, start_response, message = 'unsupported size')
		thumb_image(org_file, size, dst_file, mode)
	#print(dst_file)
	server_soft = environ.get('SERVER_SOFTWARE','')
	if server_soft[:5] == 'nginx' and os.name != 'nt':
		print('{0}/{1}'.format(THUMB_PATH, dst_path))
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

def processFile(id, filename):
	from store import ImSto
	imsto = ImSto()
	file = imsto.get(id)
	if file is None:
		imsto.close()
		return False
	save_file(file, filename)
	imsto.close()
	return True

def processFileS3(key, filename):
	BucketName = config.get('bucket_name')
	AccessKey = config.get('s3_access_key')
	SecretKey = config.get('s3_secret_key')

	from simples3 import S3Bucket, KeyNotFound
	s = S3Bucket(BucketName, access_key=AccessKey, secret_key=SecretKey)

	try:
		file = s.get(key)
	except KeyNotFound, e:
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
	
