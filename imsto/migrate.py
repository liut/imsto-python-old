#!/usr/bin/env python
# encoding: utf-8
"""
tool.py

Created by liut on 2013-06-18.
Copyright (c) 2010-2013 liut. All rights reserved.
"""

import sys
import os
from store import load_imsto, Config, encode_upload

def test_section(section):
	config = Config()
	return config.has_section(section)

def migrate(from_section,to_section):
	"""merge and sync data between 2 storage engines"""
	if from_section == to_section:
		return False

	if not test_section(from_section) or not test_section(to_section):
		return False

	imsto1 = load_imsto(from_section)
	imsto2 = load_imsto(to_section)

	total = imsto1.count()
	print 'total: {}'.format(total)

	limit = 50
	offset = 0
	while offset < total:
		print 'migrating {}/{}'.format(offset, total)
		for item in imsto1.browse(limit, offset, only_items=True):
			#print item
			_store_item(imsto2, item)
		offset += limit

def _store_item(imsto2, item):
	print 'item size: %s' % item.size
	r = imsto2.store(item.file, ctype=item.mime, name=item.name)
	print 'trans %s (%s): %s' % (item.id, item.name, r)

if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser(usage='%(prog)s command')
	parser.add_argument('-F','--src',metavar='section',type=str)
	parser.add_argument('-T','--dst',metavar='section',type=str)
	args, remaining = parser.parse_known_args()

	#migrate('imsto', 'weed')
	if args.src and args.dst:
		migrate(args.src, args.dst)
	else:
		parser.print_help()
