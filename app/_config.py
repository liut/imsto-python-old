# encoding: utf-8
"""
ImSto Config

Created by liut on 2010-12-15.
Copyright (c) 2010 liut. All rights reserved.
"""

import ConfigParser,os

class Config():
	"""docstring for Config"""
	def __init__(self):
		
		defaulting = {
		'servers': 'localhost',
		'db_name': 'storage',
		'fs_prefix': 'img',
		'thumb_path': '/thumb',
		'thumb_root': '/opt/imsto/cache/thumb/',
		'thumb_method': 'shell', # shell, wand, pil
		'url_prefix': 'http://m.imsto.net/',
		'eggs_cache': '/opt/imsto/cache/eggs',
		'max_file_size': '102400',
		'support_size': '120,160,250,400'
		}
		self.config = ConfigParser.SafeConfigParser(defaulting)
		ini_file = os.path.join(os.path.dirname(__file__), '../config/imsto.ini')
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
		val = None
		if section != 'imsto':
			try:
				val = self.config.get(section, name)
			except Exception, e:
				#raise e
				print e
				pass
		
		if val is None:
			val = self.config.get('imsto', name)

		return val


if __name__ == '__main__':
	config = Config()
	print(config.config.sections())
	print(config.get('servers'))
	print config.get('thumb_root')
	print config.get('thumb_root', 'avatar')