#!/usr/bin/env python
# encoding: utf-8
"""
test CompositeImageCommand,ModulateCompositeOp

Created by liut on 2012-11-28.
Copyright (c) 2010-2012 liut. All rights reserved.
"""

from ctypes import cast,c_char_p
import imp
imsto = imp.load_module('imsto', *imp.find_module('imsto',[os.path.join(os.path.dirname(__file__), '..')]))
from imsto import *


original = 'monalisa.jpg'

watermark = 'watermark.png'

output = 'monalisa_wm.jpg'

#from image import SimpImage
im = SimpImage(original)
im_w = SimpImage(watermark)
print im.watermark(im_w, 0.5, position='bottom-right')
print im.save(output)

