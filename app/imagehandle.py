"""
imsto: image handler
rule: (path) aj/3f/1ow9y7ks8w8s888kswkg8.jpg => (_id) aj3f1ow9y7ks8w8s888kswkg8

"""

import ConfigParser, os, re

os.environ['PYTHON_EGG_CACHE'] = '/opt/imsto/cache/eggs'

defaulting = {
'servers': 'localhost',
'thumb_path': '/thumb',
'thumb_root': '/opt/imsto/cache/thumb/',
'support_size': '[120, 130, 160]'
}
config = ConfigParser.SafeConfigParser(defaulting)
ini_file = os.path.join(os.path.dirname(__file__), '../config/imsto.ini')
config.read(ini_file)

GRID_SERVERS = config.get('imsto', 'servers')
THUMB_PATH = config.get('imsto', 'thumb_path').rstrip('/')
THUMB_ROOT = config.get('imsto','thumb_root').rstrip('/')
SUPPORTED_SIZE = eval(config.get('imsto', 'support_size'))

def print_env():
	"""list environ"""
	start_response('200 OK', [('Content-Type', 'text/plain')])
	return ['\n'.join(['%s: %r' % item for item in environ.items()])]

def not_found(environ, start_response):
	"""Called if no URL matches."""
	start_response('404 NOT FOUND', [('Content-Type', 'text/plain')])
	#return [environ.get('SERVER_SOFTWARE')[:5]]
	#
	return ['Not Found']


def image_handle_main(environ, start_response):
	path = environ.get('PATH_INFO', '')
	image_url_regex = r'/([a-z0-9]{2})/([a-z0-9]{2})/([a-z0-9]{20,36})(-[sc]\d{2,4})?\.(gif|jpg|jpeg|png)$'
	match = re.search(image_url_regex, path)
	#print(image_url_regex, path, match)
	if match is not None:
		ids = match.groups()
		#print(ids)
		id = '{0}{1}{2}'.format(*ids)
		file = load_file(id)
		if file is None:
			return not_found(environ, start_response)
		
		org_path = '{0}/{1}/{2}.{4}'.format(*ids)
		org_file = '{0}/{1}'.format(THUMB_ROOT, org_path)
		if not os.path.exists(org_file):
			save_file(file, org_file)
		if ids[3] is None:
			dst_path = org_path
			#dst_file = org_file
		else:
			dst_path = '{0}/{1}/{2}{3}.{4}'.format(*ids)
			dst_file = '{0}/{1}'.format(THUMB_ROOT, dst_path)
			#print(ids[3][1:])
			size = int(ids[3][2:])
			if size not in SUPPORTED_SIZE:
				print('unsupported size: {0}'.format(size))
				return not_found(environ, start_response)
			thumb_image(org_file, size, dst_file)
		#print(dst_file)
		server_soft = environ.get('SERVER_SOFTWARE')
		if server_soft is not None and server_soft[:5] == 'nginx' and os.name != 'nt':
			start_response('200 OK', [('X-Accel-Redirect', '{0}/{1}'.format(THUMB_PATH, dst_path))])
			return []
		#print(file.type) 
		headers = [('Content-Type', file.type), ('Content-Length', '{0.length}'.format(file)), ('Via','imsto')]
		start_response('200 OK', headers)
		# TODO: response file content
		return [file.read()]
		
	return not_found(environ, start_response)


def load_file(id):
	from pymongo import Connection
	import gridfs
	db = Connection(GRID_SERVERS).storage
	fs = gridfs.GridFS(db,'img')
	if fs.exists(id):
		return fs.get(id)
	#return None

def save_file(file, filename):
	import os
	dir_name = os.path.dirname(filename)
	if not os.path.exists(dir_name):
		os.makedirs(dir_name, 0777)
	fp = open(filename, 'wb')
	try:
		fp.write(file.read())
	finally:
		fp.close()


def thumb_image(filename, size_x, distname):
	from PIL import Image
	size = size_x, size_x
	#print(size)
	im = Image.open(filename)
	if im.size > size:
		print('thumbnail {0} to: {1}'.format(filename, size_x))
		im.thumbnail(size, Image.ANTIALIAS)
	im.save(distname, im.format)
	


if __name__ == '__main__':
	from wsgiref.simple_server import make_server
	httpd = make_server('', 8000, image_handle_main)
	print("Listening on port 8000....\n image url example: http://localhost:8000/aj/3f/1ow9y7ks8w8s888kswkg8.jpg")
	httpd.serve_forever()

	
else:
	from errorhandle import ErrorHandle
	application = ErrorHandle(image_handle_main)
	
