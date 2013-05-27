# encoding: utf-8
"""
_util.py

Created by liut on 2010-12-04.
Copyright (c) 2010 liut. All rights reserved.
"""

import os

from _wand import NewMagickWand,MagickReadImage,MagickToMime,\
MagickGetImageFormat,MagickGetImageWidth,MagickGetImageHeight,MagickGetImageCompressionQuality

__all__ = ['check_dirs', 'save_file', 'thumb_image', 'guess_mimetype', 'watermark_image']

def check_dirs(filename):
	dir_name = os.path.dirname(filename)
	if not os.path.exists(dir_name):
		os.makedirs(dir_name, 0777)

def save_file(file, filename):
	check_dirs(filename)
	fp = open(filename, 'wb')
	try:
		fp.write(file.read())
	except Exception, e:
		print('save file {} failed, error: {}'.format(filename, e))
	finally:
		fp.close()

	statinfo = os.stat(filename)
	if statinfo.st_size == 0:
		print('file size is zero, remove it')
		os.remove(filename)

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

def thumbnail_wand(filename, width, height, distname, mode='s'):
	from image import SimpImage
	im = SimpImage(filename)
	if mode == 'c':
		ret = im.cropThumbnail(width, height)
	elif mode == 'w':
		ret = im.thumbnail(width, max_width=width)
	elif mode == 'h':
		ret = im.thumbnail(width, max_height=width)
	else:
		ret = im.thumbnail(width, height)

	print "thumbnail {} {}x{} result: {}".format(mode, width, height, ret)
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

def thumb_image(filename, width, height, distname, mode='s', method='wand'):
	check_dirs(distname)
	if method == 'shell':
		return thumbnail_shell(filename, width, distname)
	elif method == 'wand':
		return thumbnail_wand(filename, width, height, distname, mode=mode)
	elif method == 'pil':
		return thumbnail_pil(filename, width, distname)



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

def watermark_image(filename, distname):
	from image import SimpImage
	im = SimpImage(filename)
	if os.environ.has_key('IMSTO_SETTINGS_ROOT'):
		watermark = os.path.join(os.environ['IMSTO_SETTINGS_ROOT'], 'watermark.png')
	else:
		watermark = os.path.join(os.getcwd(), 'config/watermark.png')
	#print ini_file
	im_w = SimpImage(watermark)
	#print im_w.wand
	check_dirs(distname)
	r = None
	if im.watermark(im_w, 0.5, position='bottom-right'):
		print 'watermark ok'
		r = im.save(distname)

	if r is None:
		print 'error watermark'

	del im
	del im_w
	return r





