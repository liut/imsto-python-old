# encoding: utf-8
"""
dispatcher.py

Created by liut on 2010-12-16.
Copyright (c) 2010 liut. All rights reserved.
"""

class Dispatcher(object):
	def __call__(self, environ, start_response):
		"""custom dispatch"""
		path_info = environ.get('PATH_INFO', '')
		if (path_info == '/Gallery'):
			# TODO:
			return self.abuilding(environ, start_response)
		elif (path_info == '/Upload'):
			# TODO:
			return self.abuilding(environ, start_response)
		elif (path_info == '/env' and environ.get('REMOTE_ADDR','') == '127.0.0.1'):
			import printenv
			return printenv.print_env(environ, start_response)
		else:
			import imagehandle
			return imagehandle.image_handle_main(environ, start_response)

	def not_found(self, environ, start_response):
		start_response('404 Not Found', [('Content-type', 'text/plain')])
		return ['Not found']

	def abuilding(self, environ, start_response):
		start_response('200 OK', [('Content-type', 'text/plain')])
		return ['Abuilding']

application = Dispatcher()

