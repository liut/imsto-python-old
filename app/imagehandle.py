# encoding: utf-8
"""
imagehandle.py

imsto: image handler
rule: (path) aj/3f/1ow9y7ks8w8s888kswkg8.jpg => (_id) aj3f1ow9y7ks8w8s888kswkg8
if/qp/ceq9shcskssskc888k4.jpg => ifqpceq9shcskssskc888k4
Created by liut on 2010-12-04.
Copyright (c) 2010 liut. All rights reserved.
"""


import _config, os, re

config = _config.Config()

THUMB_PATH = config.get('thumb_path').rstrip('/')
THUMB_ROOT = config.get('thumb_root').rstrip('/')
SUPPORTED_SIZE = eval(config.get('support_size'))

from _respond import not_found


def image_handle(environ, start_response):
	"""main url process"""
	path = environ.get('PATH_INFO', '')
	image_url_regex = r'/([a-z0-9]{2})/([a-z0-9]{2})/([a-z0-9]{19,36})(-[sc]\d{2,4})?\.(gif|jpg|jpeg|png)$'
	match = re.search(image_url_regex, path)
	#print(image_url_regex, path, match)
	if match is not None:
		ids = match.groups()
		#print(ids)
		id = '{0}{1}{2}'.format(*ids)
		from store import ImSto
		imsto = ImSto()
		file = imsto.get(id)
		if file is None:
			imsto.close()
			return not_found(environ, start_response)

		org_path = '{0}/{1}/{2}.{4}'.format(*ids)
		org_file = '{0}/{1}'.format(THUMB_ROOT, org_path)
		if not os.path.exists(org_file):
			save_file(file, org_file)
		if ids[3] is None:
			dst_path = org_path
			dst_file = org_file
		else:
			dst_path = '{0}/{1}/{2}{3}.{4}'.format(*ids)
			dst_file = '{0}/{1}'.format(THUMB_ROOT, dst_path)
			#print(ids[3][1:])
			size = int(ids[3][2:])
			if size not in SUPPORTED_SIZE:
				print('unsupported size: {0}'.format(size))
				imsto.close()
				return not_found(environ, start_response)
			thumb_image(org_file, size, dst_file)
		#print(dst_file)
		server_soft = environ.get('SERVER_SOFTWARE','')
		if server_soft[:5] == 'nginx' and os.name != 'nt':
			imsto.close()
			start_response('200 OK', [('X-Accel-Redirect', '{0}/{1}'.format(THUMB_PATH, dst_path))])
			return []
		#print(file.type) 
		headers = [('Content-Type', str(file.type)), ('Content-Length', '{0.length}'.format(file)), ('Via','imsto')]
		#print(headers)
		start_response('200 OK', headers)
		# TODO: response file content
		#data = file.read()
		imsto.close()
		#return [data]
		fd = open(dst_file,'r')
		return environ['wsgi.file_wrapper'](fd, 4096)
		
	return not_found(environ, start_response)


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

"""
test log
magickwand: 25M
PIL: 12M
shell: 11M
"""
def thumbnail_shell(filename, size_x, distname):
	size = size_x, size_x
	info = identify_shell(filename)
	if info is None:
		return None
	if info['size'] > size:
		print('thumbnail {0} to: {1}'.format(filename, size_x))
		from subprocess import check_call
		check_call(['convert','-thumbnail',str(size_x),filename,distname])
	else:
		from shutil import copyfile
		copyfile(filename, distname)

def identify_shell(imagefile):
	from subprocess import check_output
	try:
		output = check_output(['identify', '-format', '%m %w %h %Q', imagefile])
		info = output.split(' ')
		return {'format': info[0], 'size': (int(info[1]), int(info[2])), 'quality': int(info[3])}
	except CalledProcessError, e:
		print (e)
		return None

def thumbnail_wand(filename, size_x, distname):
	size = size_x, size_x
	from magickwand.image import Image
	im = Image(filename)
	if im.size > size:
		im.thumbnail(size_x)
	im.save(distname)
	del im

def thumbnail_pil(filename, size_x, distname):
	size = size_x, size_x
	from PIL import Image
	im = Image.open(filename)
	if im.size > size:
		im.thumbnail(size, Image.ANTIALIAS)
	im.save(distname, im.format)
	del im

def thumb_image(filename, size_x, distname):
	tt = config.get('thumb_method')
	if tt == 'shell':
		return thumbnail_shell(filename, size_x, distname)
	elif tt == 'wand':
		return thumbnail_wand(filename, size_x, distname)
	elif tt == 'pil':
		return thumbnail_pil(filename, size_x, distname)

if __name__ == '__main__':
	from wsgiref.simple_server import make_server
	httpd = make_server('', 8000, image_handle)
	print("Listening on port 8000....\n image url example: http://localhost:8000/aj/3f/1ow9y7ks8w8s888kswkg8.jpg")
	httpd.serve_forever()

	
else:
	from errorhandle import ErrorHandle
	application = ErrorHandle(image_handle)
	
