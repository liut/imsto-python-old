#!/usr/bin/env python
# encoding: utf-8
"""
tool.py

Created by liut on 2010-12-24.
Copyright (c) 2010 liut. All rights reserved.
"""

import sys
import os
import getopt
from store import load_imsto, Config

help_message = '''
Usage: store.py [options] [filename]

Options:
  -i, --import filename	 Import file to storeage
  -q, --id		get a file by id
  -l, --list	   List files
  -m, --meta filename	  get a file meta
  -t, --test	   test a file
  -h, --help	   Show this message
  -v, --verbose	Verbose output
  -q, --quiet	  Minimal output

'''

section = 'imsto'

class Usage(Exception):
	def __init__(self, msg):
		self.msg = msg

def list_dir(limit=5,start=0,prefix=''):
	imsto = load_imsto(section)
	gallery = imsto.browse(limit, start)
	for img in gallery['items']:
		#print(img)
		print("{0[filename]}\t{0[size]:8,d}".format(img))

def store_file(filename):
	if os.access(filename, os.R_OK):
		imsto = load_imsto(section)
		from _util import guess_mimetype
		ctype = guess_mimetype(filename)
		with open(filename) as fp:
			ret = imsto.store(fp, ctype)
			print ret
	else:
		print 'image {} not found or access deny'.format(filename)

"""
def main(argv=None):
	if argv is None:
		argv = sys.argv
	
	try:
		try:
			opts, args = getopt.getopt(argv[1:], "hi:q:lm:t:v", ["help", "import=", "id=", "list", "meta", "test", "verbose", "limit=", "start="])
		except getopt.error, msg:
			raise Usage(msg)
		
		#print(opts)
		#print(args)
		action = None
		store_file = None
		limit = 5
		start = 0
		# option processing
		for option, value in opts:
			if option == "-v":
				verbose = True
			if option == "--limit":
				limit = int(value)
			if option == "--start":
				start = int(value)

			if option in ("-h", "--help"):
				raise Usage(help_message)
			if option in ("-i", "--import"):
				filename = value
				print('store file: {0}'.format(filename))
				action = 'import'
			elif option in ("-l", "--list"):
				action = 'list'
			elif option in ("-t", "--test"):
				action = 'test'
				filename = value
			elif option in ("-m", "--meta"):
				action = 'meta'
				path = value
			elif option in ("-q", "--id"):
				action = 'get'
				id = value
			else:
				pass
		
		if action is None:
			raise Usage(help_message)

		print('action: {}'.format(action))
		if (action == 'list'):
			list_dir(limit, start)
			return 0
		elif (action == 'get') and id is not None:
			imsto = load_imsto()
			if not imsto.exists(id):
				print ('not found')
				return 1
			gf = imsto.get(id)
			#print(gf)
			print ("found: {0.name}\t{0.length}".format(gf))
			return 0
		elif action == 'import':
			store_file(filename)
			return 0
		elif action == 'meta':
			print 'meta for path: {}'.format(path)
			imsto = load_imsto()
			print imsto.meta(path=path)
		elif (action == 'test'):
			print('filename: %r' % filename)
			fp = open(filename, 'rb')
			h = fp.read(32)
			print(getImageType(h))
			return 0
				

	except Usage, err:
		print >> sys.stderr, sys.argv[0].split("/")[-1] + ": " + str(err.msg)
		#print >> sys.stderr, "\t for help use --help"
		return 2
"""

if __name__ == "__main__":
	import argparse
	config = Config()
	parser = argparse.ArgumentParser(usage='%(prog)s [options]')
	parser.add_argument('-s', '--section', metavar='section', default='imsto', choices=config.sections(), type=str, help='Special config section')
	parser.add_argument('-i', '--add', metavar='filename', type=str, help='Import file to storeage')
	parser.add_argument('-q', '--query', metavar='[exist|meta]', type=str, choices=['exist', 'meta'], help='query a file')
	parser.add_argument('-f', '--fetch', metavar='path', type=str, help='fetch a file')
	parser.add_argument('--id', metavar='id', type=str, help='Special file id')
	parser.add_argument('--path', metavar='path', type=str, help='Special file path')
	parser.add_argument('-v', '--verbose', action='store_true')
	parser.add_argument('-l', '--list', action='store_true', help='List files')
	#default=argparse.SUPPRESS
	parser.add_argument('--limit', type=int, default=5)
	parser.add_argument('--start', type=int, default=0)
	parser.add_argument('--prefix', type=str, default='')
	args, remaining = parser.parse_known_args()
	#print args

	section = args.section
	print section
	if args.list:
		list_dir(args.limit, args.start, prefix=args.prefix)
	elif args.fetch:
		imsto = load_imsto(section)
		print imsto.load('orig/{}'.format(args.fetch))
	elif args.query:
		imsto = load_imsto(section)
		method = imsto.get_meta if args.query == 'meta' else imsto.exists
		print method
		print method(args.id or None,filename=args.path or None)
	elif args.add:
		store_file(filename=args.add)
	else:
		parser.print_help()
	#sys.exit(main())

