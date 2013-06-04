#!/usr/bin/env python
# encoding: utf-8
"""
test CompositeImageCommand,ModulateCompositeOp

Created by liut on 2012-11-28.
Copyright (c) 2010-2012 liut. All rights reserved.
"""

import os
#from ctypes import cast,c_char_p
import imp
imsto = imp.load_module('imsto', *imp.find_module('imsto',[os.path.join(os.path.dirname(__file__), '..')]))
from imsto import *

#watermark = 'watermark-white.png'
watermark = 'watermark-color.png'
watermark = 'watermark-strike.png'

def watermark(bgnd, result, overlay=watermark):
	im = SimpImage(bgnd)
	im_w = SimpImage(overlay)
	copy = SimpImage('watermark-copy.png')
	#print im.watermark(im_w, 0.5, position='bottom-right')
	if im.watermark(im_w, 0.5, position='golden', copyright=copy):
		if im.save(result):
			print '{} -> {} ok'.format(bgnd, result)

	del im
	del im_w

watermark('monalisa.jpg', 'monalisa_wm.jpg')
# watermark('1.jpg', '1_wm.jpg')
# watermark('2.jpg', '2_wm.jpg')
# watermark('3.jpg', '3_wm.jpg')
# watermark('4.jpg', '4_wm.jpg')
# watermark('5.jpg', '5_wm.jpg')
# watermark('6_1.jpg', '6_1_wm.jpg')