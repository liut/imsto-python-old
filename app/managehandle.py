# encoding: utf-8
"""
storehandle.py

Created by liut on 2010-12-18.
Copyright (c) 2010 liut. All rights reserved.
"""


import os
import re
import json
from _respond import not_found
from store import ImSto

def manage(environ, start_response):
	path_info = environ.get('PATH_INFO', '')
	
	man_regex = r'^/([A-Za-z]+)/(env|Gallery|Stored)'
	match = re.search(man_regex, path_info)
	#print('match: {0}'.format(match))
	if match is None:
		return not_found(environ, start_response)
	
	action = match.groups()[1]
	if (action == 'Gallery'):
		start_response('200 OK', [('Content-type', 'text/plain')])
		
		imsto = ImSto()
		gallery = imsto.browse()
		import datetime
		dthandler = lambda obj: obj.isoformat() if isinstance(obj, datetime.datetime) else None
		if hasattr(imsto, 'close'):
			imsto.close()
		return [json.dumps(gallery, default=dthandler)]
	elif (action == 'Stored'):
		return stored_process(environ, start_response)
		#start_response('200 OK', [('Content-type', 'text/plain')])
		#return ['Stored']
	elif  (action == 'env'):
		from _respond import print_env
		return print_env(environ, start_response)
	
	start_response('200 OK', [('Content-type', 'text/plain')])
	return [path_info]



def stored_process(environ, start_response):
	from cgi import FieldStorage
	form = FieldStorage(environ=environ)
	#print(form.keys())
	start_response('200 Ok', [('Content-type', 'text/javascript')])
	method = environ['REQUEST_METHOD'].upper()
	if method == 'GET' or method == 'HEAD':
		return [json.dumps([False, 'bad request'])]
	oper = form['oper']
	print(oper)
	from store import ImSto
	imsto = ImSto()
	if oper.value == 'delete':
		id = form['id']
		return [json.dumps(imsto.delete(id.value))]
	if oper.value == 'add':
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
			result.append(id)
		if hasattr(imsto, 'close'):
			imsto.close()
		
		return [json.dumps(result)]
	else:
		return [json.dumps([False, 'invalid operation'])]


if __name__ == '__main__':
	pass
else:
	from errorhandle import ErrorHandle
	application = ErrorHandle(manage)
