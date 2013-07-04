#!/usr/bin/env python
# encoding: utf-8
"""
tool.py

Created by liut on 2010-12-24.
Copyright (c) 2010-2013 liut. All rights reserved.
"""

import sys
import os
from store import load_imsto, Config


section = 'imsto'


def list_dir(limit=5,start=0,prefix=''):
	imsto = load_imsto(section)
	gallery = imsto.browse(limit, start)
	if gallery['total'] == 0:
		print 'total 0, empty'
		return

	print 'total {}'.format(gallery['total'])
	for item in gallery['items']:
		#print hasattr(item.file, 'read')
		#print(item)
		print("{0[filename]}\t{0[size]:8,d}".format(item))

def store_file(filename):
	if os.access(filename, os.R_OK):
		imsto = load_imsto(section)
		from _util import guess_mimetype
		ctype = guess_mimetype(filename)
		with open(filename) as fp:
			ret = imsto.store(fp, ctype, name=os.path.basename(filename))
			print ret
	else:
		print 'image {} not found or access deny'.format(filename)


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
		_file, _path = imsto.load('orig/{}'.format(args.fetch))
		print _path
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

