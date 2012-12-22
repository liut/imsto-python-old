# encoding: utf-8
"""
_util.py

Created by liut on 2010-12-04.
Copyright (c) 2010 liut. All rights reserved.
"""

import os
import _config
config = _config.Config()

from _wand import *

def save_file(file, filename):
	dir_name = os.path.dirname(filename)
	if not os.path.exists(dir_name):
		os.makedirs(dir_name, 0777)
	fp = open(filename, 'wb')
	try:
		fp.write(file.read())
	finally:
		fp.close()

"""
test log
magickwand: 25M
PIL: 12M
shell: 11M
"""
def thumbnail_shell(filename, size_1, distname):
	size = size_1, size_1
	info = identify_shell(filename)
	if info is None:
		return None
	if info['size'] > size:
		print('thumbnail {0} to: {1}'.format(filename, size_1))
		from subprocess import check_call
		check_call(['convert','-thumbnail',str(size_1),filename,distname])
	else:
		from shutil import copyfile
		copyfile(filename, distname)

def identify_shell(imagefile):
	from subprocess import check_output
	try:
		output = check_output(['identify', '-format', '%m %w %h %Q', imagefile])
		info = output.split(' ')
		return {'format': info[0], 'size': (int(info[1]), int(info[2])), 'quality': int(info[3])}
	except CalledProcessError, e:
		print (e)
		return None

def identify_wand(imagefile):
	magick_wand = NewMagickWand()
	if not MagickReadImage(magick_wand, imagefile):
		return False
	format = MagickGetImageFormat(magick_wand)
	info = {
		'format': format,
		'mime': MagickToMime(format),
		'size': (MagickGetImageWidth(magick_wand), MagickGetImageHeight(magick_wand)),
		'quality': MagickGetImageCompressionQuality(magick_wand)
	}

	DestroyMagickWand(magick_wand)

	return info

def thumbnail_wand(filename, size_1, distname, mode='s'):
	from image import SimpImage
	im = SimpImage(filename)
	if mode == 'c':
		ret = im.cropThumbnail(size_1, size_1)
	elif mode == 'w':
		ret = im.thumbnail(size_1, max_width=size_1)
	elif mode == 'h':
		ret = im.thumbnail(size_1, max_height=size_1)
	else:
		ret = im.thumbnail(size_1)

	print "thumbnail {} result: {}".format(size_1, ret)
	if ret:
		ret = im.save(distname)
	del im

	return ret



def thumbnail_pil(filename, size_1, distname):
	size = size_1, size_1
	from PIL import Image
	im = Image.open(filename)
	if im.size > size:
		im.thumbnail(size, Image.ANTIALIAS)
	im.save(distname, im.format)
	del im

def thumb_image(filename, size_1, distname, mode='s'):
	tt = config.get('thumb_method')
	#print('thumb_method: {0}'.format(tt))
	if tt == 'shell':
		return thumbnail_shell(filename, size_1, distname)
	elif tt == 'wand':
		return thumbnail_wand(filename, size_1, distname, mode=mode)
	elif tt == 'pil':
		return thumbnail_pil(filename, size_1, distname)



def guess_mimetype(fn, default="application/octet-stream"):
	"""Guess a mimetype from filename *fn*.

	>>> guess_mimetype("foo.txt")
	'text/plain'
	>>> guess_mimetype("foo")
	'application/octet-stream'
	"""
	import mimetypes
	if "." not in fn:
		return default
	bfn, ext = fn.lower().rsplit(".", 1)
	if ext == "jpg": ext = "jpeg"
	return mimetypes.guess_type(bfn + "." + ext)[0] or default
