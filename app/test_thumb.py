#!/usr/bin/env python
# encoding: utf-8
"""
imsto test

Created by liut on 2012-11-28.
Copyright (c) 2010-2012 liut. All rights reserved.
"""


from _util import *

def test():
	filename = '1.jpg'
	#thumbnail_wand(filename, 120, '1-120.jpg')
	thumbnail_wand(filename, 120, '1-c120.jpg', mode='c')
	thumbnail_wand(filename, 120, '1-w120.jpg', mode='w')
	thumbnail_wand(filename, 120, '1-h120.jpg', mode='h')


if __name__ == "__main__":
	test()


