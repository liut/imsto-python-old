"""
ImSto Config
"""

import ConfigParser,os

class Config():
	"""docstring for Config"""
	def __init__(self):
		
		defaulting = {
		'servers': 'localhost',
		'thumb_path': '/thumb',
		'thumb_root': '/opt/imsto/cache/thumb/',
		'eggs_cache': '/opt/imsto/cache/eggs',
		'support_size': '[120, 130, 160]'
		}
		self.config = ConfigParser.SafeConfigParser(defaulting)
		ini_file = os.path.join(os.path.dirname(__file__), '../config/imsto.ini')
		self.config.read(ini_file)
		if os.environ.has_key('PYTHON_EGG_CACHE') and not (os.environ['PYTHON_EGG_CACHE'] is None):
			pass
		else:
			os.environ['PYTHON_EGG_CACHE'] = self.get('eggs_cache')
	
	def get(self, name):
		"""docstring for get"""
		section = 'imsto'
		return self.config.get(section, name)

if __name__ == '__main__':
	config = Config()
	print(config.get('servers'))