# encoding: utf-8
"""
image.py

Created by liut on 2010-12-04.
Copyright (c) 2010-2013 liut. All rights reserved.
"""

__all__ = ['SimpImage']

import ctypes,collections
from _wand import (NewMagickWand,DestroyMagickWand,CloneMagickWand,ClearMagickWand,
MagickReadImageBlob,MagickReadImage,MagickWriteImage,MagickGetImageBlob,
MagickGetImageFormat,MagickSetImageFormat,MagickGetImageWidth,MagickGetImageHeight,
MagickGetImageCompressionQuality,MagickSetImageCompressionQuality,
MagickScaleImage,MagickRelinquishMemory,MagickStripImage,MagickThumbnailImage,MagickCropImage,MagickSetImagePage,
MagickSetImageArtifact,
BlendCompositeOp,DissolveCompositeOp,ModulateCompositeOp,
MagickCompositeImage,MagickLabelImage,
MagickSetImageGravity,CenterGravity,SouthGravity,
MagickGetException,MagickClearException,
)
import warnings

import os

# FORMAT_JPEG = 'JPEG'
# FORMAT_PNG = 'PNG'
# FORMAT_GIF = 'GIF'

class SimpImage(object):
	_max_width, _max_height = 0, 0

	"""docstring for ClassName"""
	def __init__(self, file = None, image=None, blob=None):
		if isinstance(image, SimpImage):
			self._wand = CloneMagickWand(image.wand)
		elif blob is not None:
			if not isinstance(blob, collections.Iterable):
				raise TypeError( 'blob must be iterable, not {}'.format(repr(blob)) )
			if not isinstance(blob, basestring):
				blob = ''.join(blob)
			elif not isinstance(blob, str):
				blob = str(blob)
			self._wand = NewMagickWand()
			r = MagickReadImageBlob( self._wand, blob, len( blob ) )
			if not r:
				self.error()
		else:
			self._wand = NewMagickWand()
			self.read(file)

	def __del__(self):
		if self._wand:
			self._wand = DestroyMagickWand( self._wand )


	def __copy__( self ):
		return self.clone()

	def clone( self ):
		return type(self)(image=self)


	def _clear( self ):
		ClearMagickWand( self._wand )


	def read( self, file):
		self._clear()
		
		if isinstance(file, basestring):
			if os.access(file, os.R_OK):
				r = MagickReadImage( self._wand, file )
			else:
				#print 'image {} not found or access deny'.format(file)
				raise IOError('image {} not found or access deny'.format(file))
		elif hasattr( file, 'read' ):
			c = file.read()
			r = MagickReadImageBlob( self._wand, c, len( c ) )
		else:
			raise TypeError('file must be a readable file path or filelike object')

		if not r:
			self.error()


	@property
	def wand(self):
		return self._wand

	@property
	def format( self ):
		format = MagickGetImageFormat( self._wand )
		if format == '':
			return None
		else:
			return format

	@format.setter
	def format(self, value):
		'''The image format as a string, eg. "PNG".'''
		MagickSetImageFormat( self._wand, value )

	def max_height():
		doc = "The max_height property."
		def fget(self):
			return self._max_height
		def fset(self, value):
			self._max_height = value
		def fdel(self):
			del self._max_height
		return locals()
	max_height = property(**max_height())

	def max_width():
		doc = "The max_width property."
		def fget(self):
			#if self._max_width is None:
			#	self._max_width = 0
			return self._max_width
		def fset(self, value):
			self._max_width = value
		def fdel(self):
			del self._max_width
		return locals()
	max_width = property(**max_width())

	@property
	def quality(self):
		return MagickGetImageCompressionQuality( self._wand )

	@quality.setter
	def quality(self, value):
		MagickSetImageCompressionQuality( self._wand, int( round( value, 0 ) ) )

	@property
	def width(self):
		return MagickGetImageWidth( self._wand )

	@property
	def height(self):
		return MagickGetImageHeight( self._wand )

	def scale( self, size ):
		''' Scales the size of image to the given dimensions.
			size - A tuple containing the size of the scaled image.'''
		MagickScaleImage( self._wand, size[0], size[1] )

	def _get_size( self ):
		return ( self.width, self.height )
	size = property( _get_size, scale, None, 'A tuple containing the size of the image. Setting the size is the same as calling scale().' )

	@property
	def meta(self):
		return {'format': self.format, 'width': int(self.width), 'height': int(self.height), 'quality': int(self.quality)}

	def getBlob(self):
		size = ctypes.c_size_t()
		b = MagickGetImageBlob( self._wand, ctypes.byref(size) )
		if b and size.value:
			blob = ctypes.string_at(b, size.value)
			MagickRelinquishMemory(b)
			return blob
		self.error()

	def save( self, file = None ):
		''' Saves the image to a file.  If no file is specified, the file is
			saved with the original filename.'''
		if hasattr( file, 'write' ):
			return file.write( self.getBlob() )
		else:
			r = MagickWriteImage( self._wand, file )

			if not r:
				self.error()
			return r

	def thumbnail( self, columns, rows = None, fit = True, max_width = 0, max_height = 0 ):
		if rows is None: rows = columns
		print "thumbnail columns: {}, rows: {}, max_width: {}, max_height: {}".format(columns, rows, max_width, max_height)

		org_width, org_height = self.size

		if org_width <= columns and org_height <= rows:
			if MagickStripImage(self._wand):
				return True
			return False

		if fit:
			rel = float( org_width ) / float( org_height )
			if max_width > 0:
				columns = max_width
				rows = int( columns / rel )
			elif max_height > 0:
				rows = max_height
				columns = int( rows * rel )
			else:
				bounds = float( columns ) / float( rows )
				if rel >= bounds: rows = int( columns / rel )
				else: columns = int( rows * rel )
			print "fit columns: {}, rows: {}".format(columns, rows)
		if not MagickThumbnailImage( self._wand, columns, rows ):
			print('error: MagickThumbnailImage')

			self.error()
			
			return False
		return True


	def cropThumbnail( self, dst_width, dst_height = None ):
		if dst_height is None: dst_height = dst_width

		org_width, org_height = self.size

		if org_width <= dst_width and org_height <= dst_height:
			if MagickStripImage(self._wand):
				return True
			return False

		ratio_x = float( dst_width ) / float( org_width );
		ratio_y = float( dst_height ) / float( org_height );

		if ratio_x > ratio_y:
			new_width  = int(dst_width)
			new_height = int(ratio_x * float( org_height ))
		else:
			new_height = int(dst_height)
			new_width  = int(ratio_y * float( org_width ))
		
		if not MagickThumbnailImage(self._wand, new_width, new_height):
			print('error: MagickThumbnailImage')
			return False

		if new_width == dst_width and new_height == dst_height:
			return True

		crop_x = int((new_width - dst_width) / 2);
		crop_y = int((new_height - dst_height) / 2);

		print "crop_x: {0}, crop_y: {1}".format(crop_x, crop_y)

		if not MagickCropImage(self._wand, dst_width, dst_height, crop_x, crop_y):
			print('error: MagickCropImage')
			return False
		
		r = MagickSetImagePage(self._wand, dst_width, dst_height, 0, 0);

		if not r:
			self.error()
		
		return True

	def watermark(self, image, transparency=0.0, left=0, top=0, position=None, copyright=None):
		"""
		watermark methods:
		1. convert bgnd overlay   -compose modulate \
			-define compose:args={brigthness}[,{saturation}] \
			-composite  result
		2. convert bgnd overlay   -compose dissolve \
			-define compose:args={src_percent},{dst_percent} \
			-composite  result
		"""
		watermark_image = image.clone()
		s_width, s_height = self.size
		w_width, w_height = watermark_image.size

		if s_width < w_width or s_height < w_height:
			print 'source image is too small, must large than {} x {}'.format(w_width, w_height)
			return False

		if position == 'bottom-right':
			left = s_width - w_width - 10
			top = s_height - w_height - 10
		elif position == 'top-left':
			left = top = 10
		elif position == 'top-right':
			left = s_width - w_width - 10
			top = 10
		elif position == 'bottom-left':
			left = 10
			top = s_height - w_height - 10
		elif position == 'center':
			left = (s_width - w_width) / 2
			top = (s_height - w_height) / 2
		elif position == 'golden':
			#left = s_width * 0.382 - w_width / 2
			left = (s_width - w_width) / 2
			top = s_height * 0.618 - w_height / 2

		MagickSetImageArtifact(watermark_image.wand,"compose:args", "15%")
		#MagickSetImageArtifact(watermark_image.wand,"compose:args", "5")
		#MagickSetImageGravity(watermark_image.wand, SouthGravity)
		#op = DissolveCompositeOp
		#op = ModulateCompositeOp
		op = BlendCompositeOp
		r = MagickCompositeImage(self.wand, watermark_image.wand, op, int(left), int(top))
		del watermark_image

		if not r:
			self.error()

		if copyright and isinstance(copyright, SimpImage):
			ci = copyright.clone()
			MagickSetImageArtifact(ci.wand,"compose:args", "40%")
			MagickCompositeImage(self.wand, ci.wand, op, int(s_width * 0.382 - w_width / 2), int(s_height - w_height - s_height*.1))
			del ci

		return r


	def error(self, stacklevel=1):
		severity = ctypes.c_int()
		desc = MagickGetException(self.wand, ctypes.byref(severity))
		print severity
		print desc
		MagickClearException(self.wand)
		# TODO: process exception or warning
		#if isinstance(e, Warning):
		#	warnings.warn(e, stacklevel=stacklevel + 1)
		#elif isinstance(e, Exception):
		#	raise e
