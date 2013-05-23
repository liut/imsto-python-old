#!/usr/bin/env python
# encoding: utf-8
"""
imsto test

Created by liut on 2012-11-28.
Copyright (c) 2010-2012 liut. All rights reserved.
"""


from _util import *

@profile
def test():
	filename = 'monalisa.jpg'
	print thumbnail_wand(filename, 160, 160, 'monalisa-s160.jpg')
	print thumbnail_wand(filename, 160, 160, 'monalisa-c160.jpg', mode='c')
	print thumbnail_wand(filename, 160, 160, 'monalisa-w160.jpg', mode='w')
	print thumbnail_wand(filename, 160, 160, 'monalisa-h160.jpg', mode='h')
	print thumbnail_wand(filename, 160, 120, 'monalisa-c160x120.jpg', mode='c')


if __name__ == "__main__":
	test()


