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
			pass
		elif (path_info == '/Upload'):
			pass
		elif (path_info == '/env' and environ.get('REMOTE_ADDR','') == '127.0.0.1'):
			import printenv
			return printenv.print_env(environ, start_response)
		else:
			import imagehandle
			return imagehandle.image_handle_main(environ, start_response)
		
application = Dispatcher()

