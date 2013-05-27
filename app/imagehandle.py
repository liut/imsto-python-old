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

#os.environ.setdefault("IMSTO_CONF_ROOT", os.path.join(os.path.dirname(__file__), '../config'))


def appImageHandle(environ, start_response):
	"""main image url process"""
	
	SECTION = environ.get('IMSTO_SECTION', 'imsto')
	#print 'engine_code: {0}'.format(engine_code)
	imsto = ImSto(SECTION)
	path = environ.get('PATH_INFO', '')
	THUMB_PATH = imsto.get_config('thumb_path').rstrip('/')
	try:
		dst_file, dst_path = imsto.load(path)
	except UrlError, e:
		return not_found(environ, start_response, e.message)
	except Exception, e:
		raise
	finally:
		imsto.close()

	print('dst_path: {}'.format(dst_path))
	#print('dst_file: {}'.format(dst_file))
	
	server_soft = environ.get('SERVER_SOFTWARE','')
	if server_soft[:5] == 'nginx' and os.name != 'nt':
		print('path: {0}/{1}'.format(THUMB_PATH, dst_path))
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


if __name__ == '__main__':
	from wsgiref.simple_server import make_server
	httpd = make_server('', 8000, appImageHandle)
	print("Listening on port 8000....\n image url example: http://localhost:8000/aj/3f/1ow9y7ks8w8s888kswkg8.jpg\n")
	httpd.serve_forever()

else:
	from errorhandle import ErrorHandle
	application = ErrorHandle(appImageHandle)
	
