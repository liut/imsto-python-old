
import os
import json
from sys import exc_info
from traceback import format_tb
from imsto import *

__all__ = ['ErrorHandle','ImageHandler','AdminHandler']

def abuilding(self, environ, start_response):
	"""show abuilding"""
	start_response('200 OK', [('Content-type', 'text/plain')])
	return ['Abuilding']

def not_found(environ, start_response, message = 'Not Found'):
	"""Called if no URL matches."""
	start_response('404 NOT FOUND', [('Content-Type', 'text/plain')])
	return [message]

def print_env(environ, start_response):
	"""list environ items"""
	start_response('200 OK', [('Content-Type', 'text/plain')])
	return ['\n'.join(['%s: %r' % item for item in environ.items()])]

def get_path_info(environ):
	if environ.has_key('app.url_args'):
		path = ''.join(environ.get('app.url_args'))
	else:
		path = environ.get('PATH_INFO', '')

	#print 'path: %s (%s)' % (path, type(path))
	return path

class ErrorHandle(object):
	"""The middleware we use."""
	def __init__(self, app):
		self.app = app

	def __call__(self, environ, start_response):
		"""Call the application can catch exceptions."""
		appiter = None
		# just call the application and send the output back
		# unchanged but catch exceptions
		try:
			appiter = self.app(environ, start_response)
			for item in appiter:
				yield item
		# if an exception occours we get the exception information
		# and prepare a traceback we can render
		except:
			e_type, e_value, tb = exc_info()
			traceback = ['Traceback (most recent call last):']
			traceback += format_tb(tb)
			traceback.append('%s: %s' % (e_type.__name__, e_value))
			# we might have not a stated response by now. try
			# to start one with the status code 500 or ignore an
			# raised exception if the application already started one.
			try:
				start_response('500 INTERNAL SERVER ERROR', [
							   ('Content-Type', 'text/plain')])
			except:
				pass
			yield '\n'.join(traceback)

		# wsgi applications might have a close function. If it exists
		# it *must* be called.
		if hasattr(appiter, 'close'):
			appiter.close()

def ImageHandler(environ, start_response):
	"""main image url handler"""
	SECTION = environ.get('IMSTO_SECTION', 'imsto')
	#print 'engine_code: {0}'.format(engine_code)
	imsto = ImSto(SECTION)
	path = get_path_info(environ)
	#print 'path: %s' % path
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
	
	THUMB_PATH = imsto.get_config('thumb_path').rstrip('/')
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

def AdminHandler(environ, start_response):
	path = get_path_info(environ)
	
	man_regex = r'(env|Gallery|Stored)$'
	match = re.search(man_regex, path_info)
	#print('match: {0}'.format(match))
	if match is None:
		return not_found(environ, start_response)
	
	action = match.groups()[1]
	if (action == 'Gallery'):
		from cgi import FieldStorage
		form = FieldStorage(environ=environ)
		limit = 20
		start = 0
		if form.has_key("page") and form["page"].value != "":
			page = int(form["page"].value)
			if page < 1:
				page = 1
			start = limit * (page - 1)
		
		start_response('200 OK', [('Content-type', 'text/plain')])
		
		imsto = ImSto()
		gallery = imsto.browse(limit, start)
		import datetime
		dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.datetime) else None
		if hasattr(imsto, 'close'):
			imsto.close()
		return [json.dumps(gallery, default=dthandler)]
	elif (action == 'Stored'):
		return StoredHandler(environ, start_response)
		#start_response('200 OK', [('Content-type', 'text/plain')])
		#return ['Stored']
	elif  (action == 'env'):
		return print_env(environ, start_response)
	
	start_response('200 OK', [('Content-type', 'text/plain')])
	return [path_info]


def StoredHandler(environ, start_response):
	from cgi import FieldStorage
	import cgitb; cgitb.enable(display=0, logdir="/tmp")
	form = FieldStorage(fp=environ['wsgi.input'], environ=environ)
	print(form.keys())

	start_response('200 Ok', [('Content-type', 'text/javascript')])

	if "oper" not in form:
		#print("Bad Request")
		return [json.dumps([False, 'Bad Request'])]

	method = environ['REQUEST_METHOD'].upper()
	if method == 'GET' or method == 'HEAD':
		return [json.dumps([False, 'bad request'])]
	oper = form['oper']
	print(oper)
	section = form['section'] if form.has_key('section') else 'imsto'
	from store import ImSto
	imsto = ImSto(section)
	if oper.value == 'delete':
		id = form['id']
		return [json.dumps(imsto.delete(id.value))]
	if oper.value == 'add':

		if "new_file" not in form:
			return [json.dumps([False, 'please select a file'])]

		new_file = form['new_file']
		if new_file is None:
			return [json.dumps([False, 'invalid upload field'])]
		print(type(new_file))
		result = []
		if type(new_file) == type([]):
			for f in new_file:
				print('%r %r %r %r %r %r' % (f.name, f.filename, f.type, f.disposition, f.file, f.length))
				id = imsto.store(f.file, ctype=f.type, name=f.filename)
				print('new_id: %r' % id)
				result.append(id)
		else:
			f = new_file
			print('single file %r %r' % (f.name, f.filename))
			id = imsto.store(f.file, ctype=f.type, name=f.filename)
			print('new_id: %r' % id)
			result = id
		if hasattr(imsto, 'close'):
			imsto.close()
		
		return [json.dumps(result)]
	else:
		return [json.dumps([False, 'invalid operation'])]



# map urls to functions
default_urls = [
	(r't/(.+)$', ImageHandler),
	(r'Manage/(.*)$', AdminHandler)
]

def application(environ, start_response):
	"""
	The main WSGI application. Dispatch the current request to
	the functions from above and store the regular expression
	captures in the WSGI environment as  `app.url_args` so that
	the functions from above can access the url placeholders.

	If nothing matches call the `not_found` function.
	"""
	import re
	path = environ.get('PATH_INFO', '').strip('/')
	for regex, callback in default_urls:
		match = re.search(regex, path)
		if match is not None:
			environ['app.url_args'] = match.groups()
			return callback(environ, start_response)
	return not_found(environ, start_response)



if __name__ == '__main__':
	from wsgiref.simple_server import make_server
	httpd = make_server('', 8000, application)
	print("Listening on port 8000....\n image url example: http://localhost:8000/aj/3f/1ow9y7ks8w8s888kswkg8.jpg\n")
	httpd.serve_forever()

else:
	application = ErrorHandle(application)


