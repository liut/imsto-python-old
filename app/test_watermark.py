#!/usr/bin/env python
# encoding: utf-8
"""
test CompositeImageCommand,ModulateCompositeOp

Created by liut on 2012-11-28.
Copyright (c) 2010-2012 liut. All rights reserved.
"""

from ctypes import cast,c_char_p
from _wand import *


original = 'monalisa.jpg'

watermark = 'watermark2.png'

output = 'monalisa_wm.jpg'

from image import SimpImage
im = SimpImage(original)
im_w = SimpImage(watermark)
print im.watermark(im_w, 0.5, position='bottom-right')
print im.save(output)

