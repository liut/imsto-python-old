#!/usr/bin/env python
# encoding: utf-8
"""
imsto test

Created by liut on 2013-08-28.
Copyright (c) 2010-2012 liut. All rights reserved.
"""

import os
import imp
imsto = imp.load_module('imsto', *imp.find_module('imsto',[os.path.join(os.path.dirname(__file__), '..')]))
from imsto import *


#@profile
def test():
	filename = 'mold.png'
	im = SimpImage(filename)
	print "format {}, length: {}".format(im.format, len(im.getBlob()) )
	im.format = 'JPEG'
	im.quality = 88
	print "format {}, length: {}".format(im.format, len(im.getBlob()) )
	# im.save('mold_new.jpg')


if __name__ == "__main__":
	test()


