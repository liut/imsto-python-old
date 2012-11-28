#!/usr/bin/env python
# encoding: utf-8
"""
imsto test

Created by liut on 2012-11-28.
Copyright (c) 2010-2012 liut. All rights reserved.
"""

filename = '1.jpg'

from imagehandle import thumbnail_wand


if __name__ == "__main__":
	thumbnail_wand(filename, 120, '1-120.jpg')

