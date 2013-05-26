
from imagehandle import appImageHandle as appImg
from managehandle import manage as appMan
from _respond import not_found

# map urls to functions
urls = [
	(r't/(.+)$', appImg),
	(r'Manage/(.*)$', appMan)
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
	path = environ.get('PATH_INFO', '').lstrip('/')
	for regex, callback in urls:
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
	from errorhandle import ErrorHandle
	application = ErrorHandle(application)
