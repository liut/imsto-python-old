
def abuilding(self, environ, start_response):
	start_response('200 OK', [('Content-type', 'text/plain')])
	return ['Abuilding']

def not_found(environ, start_response):
	"""Called if no URL matches."""
	start_response('404 NOT FOUND', [('Content-Type', 'text/plain')])
	return ['Not Found']

def print_env(environ, start_response):
	"""list environ items"""
	import os
	print(os.environ)
	from cgi import FieldStorage
	form = FieldStorage(environ=environ)
	#print(form.keys())
	for k in form.keys():
		print ('k: %s' % k)
		f = form[k]
		print (f)
	start_response('200 OK', [('Content-Type', 'text/plain')])
	return ['\n'.join(['%s: %r' % item for item in environ.items()])]



