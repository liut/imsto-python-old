# encoding: utf-8
"""
ImSto Config

Created by liut on 2010-12-15.
Copyright (c) 2010-2013 liut. All rights reserved.
"""

__all__ = ['Config']

import ConfigParser,os

class Singleton(type):
	_instances = {}
	def __call__(cls, *args, **kwargs):
		if cls not in cls._instances:
			cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
		return cls._instances[cls]

class Config(object):
	__metaclass__ = Singleton

	"""docstring for Config"""
	def __init__(self):
		
		self.defaulting = {
		'servers': 'localhost',
		'replica_set': None,
		'engine': 'mongodb',
		'db_name': 'storage',
		'fs_prefix': 'img',
		'thumb_path': '/thumb',
		'thumb_root': '/opt/imsto/cache/thumb/',
		'temp_root': '/tmp/',
		'thumb_method': 'shell', # shell, wand, pil
		'url_prefix': 'http://m.imsto.net/',
		'eggs_cache': '/opt/imsto/cache/eggs',
		'max_file_size': '102400',
		'max_jpeg_quality': '88',
		'max_width': '1920',
		'max_height': '1920',
		'support_size': '120,160,250,400',
		'admin_name': 'imsto',
		'admin_pass': '',
		}
		self.config = ConfigParser.ConfigParser()
		if os.environ.has_key('IMSTO_CONF_DIR'):
			ini_file = os.path.join(os.environ['IMSTO_CONF_DIR'], 'imsto.ini')
		else:
			ini_file = os.path.join(os.getcwd(), 'config/imsto.ini')
		print 'config: {}'.format(ini_file)

		ret = self.config.read(ini_file)
		if len(ret) == 0:
			print('Error: imsto.ini not found or read error')
		
		if os.environ.has_key('PYTHON_EGG_CACHE') and not (os.environ['PYTHON_EGG_CACHE'] is None):
			pass
		else:
			pass
			#os.environ['PYTHON_EGG_CACHE'] = self.get('eggs_cache')
	
	def get(self, name, section='imsto'):
		"""docstring for get"""
		for s in [section, 'common']:
			if self.config.has_option(s, name):
				return self.config.get(s, name)

		if self.defaulting.has_key(name):
			return self.defaulting[name];

		if name.startswith('s3_'):
			return os.environ.get(name.upper(), None)

		return None

	def sections(self):
		ss = self.config.sections()
		if 'common' in ss:
			del ss[ss.index('common')]
		return ss

	def has_section(self, section):
		return self.config.has_section(section)


if __name__ == '__main__':
	config = Config()
	config2 = Config()
	print id(config)
	print id(config2)
	print(config.config.sections())
	print(config.get('servers'))
	print config.get('thumb_root')
	print config.get('thumb_root', 'avatar')