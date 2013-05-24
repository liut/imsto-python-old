# encoding: utf-8
"""
storehandle.py

Created by liut on 2010-12-18.
Copyright (c) 2010 liut. All rights reserved.
"""

import os,re,imp
imsto = imp.load_module('imsto', *imp.find_module('imsto',[os.path.join(os.path.dirname(__file__), '..')]))
from imsto import *
from _respond import *

import json

def manage(environ, start_response):
	path_info = environ.get('PATH_INFO', '')
	
	man_regex = r'^/([A-Za-z]+)/(env|Gallery|Stored)'
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
		return stored_process(environ, start_response)
		#start_response('200 OK', [('Content-type', 'text/plain')])
		#return ['Stored']
	elif  (action == 'env'):
		return print_env(environ, start_response)
	
	start_response('200 OK', [('Content-type', 'text/plain')])
	return [path_info]



def stored_process(environ, start_response):
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
	from store import ImSto
	imsto = ImSto()
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


if __name__ == '__main__':
	from wsgiref.simple_server import make_server
	httpd = make_server('', 8001, manage)
	print("Listening on port 8001....\n image manage example: http://localhost:8001/\n")
	httpd.serve_forever()
else:
	from errorhandle import ErrorHandle
	application = ErrorHandle(manage)
