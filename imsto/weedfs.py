# encoding: utf-8
"""
weedfs.py

Created by liut on 2013-06-09.
Copyright (c) 2010-2013 liut. All rights reserved.
"""


import os
import urllib
import httplib2
import json
from _util import *

class WeedClient(object):
	"""Client for weed-fs
		Learn from: https://github.com/micjohnson/weed-php
	"""
	def __init__(self, master = 'localhost:9333', replication = None):
		self.master = master
		self.default_replication = replication

	def _request(self, url, method = 'GET', body = None, headers = None):
		print '_request: %s' % url
		h = httplib2.Http()
		if method == 'POST':
			resp, content, = h.request(url, method, body=body, headers=headers)
		else:
			resp, content = h.request(url, method)

		#print resp
		#print content
		try:
			if resp.status >= 400:
				print 'request error: {} {}'.format(resp.status, resp.reason)
				print 'response: {}'.format(content)
				return resp.status, resp.reason, json.loads(content) if content.startswith('{') else content
			if resp['content-type'] == 'application/javascript' or resp.status == 201 and resp['content-type'] == 'text/plain; charset=utf-8':
				return resp.status, resp.reason, json.loads(content)
			# get content
			return resp['content-type'], int(resp['content-length']), content
		except Exception, e:
			print e
			print resp
			return resp.status, e, None

	def assign(self, count = 1, replication = None):
		url = 'http://{}/dir/assign?count={}'.format(self.master,int(count))
		if replication is None:
			replication = self.default_replication
		if replication:
			url = '{}&replication={}'.format(url, replication)
		#{"count":1,"fid":"2,753b19e78fe6","publicUrl":"127.0.0.1:9334","url":"localhost:9334"}
		first, second, result = self._request(url)
		#volume_host, fid = 
		if isinstance(result, dict):
			return result['publicUrl'], result['fid']
		print 'error assign {}: {}, content: {}'.format(first, second, result)

	def status(self):
		url = 'http://{}/dir/status'.format(self.master)

		return self._request(url)

	def retrieve(self, volume_host, fid, head=False):
		url = 'http://{}/{}'.format(volume_host, fid)
		#f = urllib.urlopen(url)
		first, second, content = self._request(url, 'HEAD' if head else 'GET')
		#print 'retrieve %s %s' % (first, second)
		if isinstance(first, str):
			return first, second, content
		print 'error retrieve: {}: {}, content: {}'.format(first, second, len(content))
		return first, second, None

	def delete(self, volume_host, fid):
		url = 'http://{}/{}'.format(volume_host, fid)
		return self._request(url, 'DELETE')

	def lookup(self, volumeId):
		url = 'http://{}/dir/lookup?volumeId={}'.format(self.master, volumeId)
		return self._request(url)

	def grow(self, count, replication):
		url = 'http://{}/dir/grow?count={}&replication={}'.format(self.master,int(count),replication)
		return self._request(url)

	def store(self, volume_host, fid, file = None, content = None, name = None, content_type = None):
		content_type, body = encode_upload(file=file, content=content, name=name, content_type=content_type)
		headers = { 'Content-Type': content_type }
		url = 'http://{}/{}'.format(volume_host, fid)
		ret = self._request(url, 'POST', body=body, headers=headers)
		print type(ret)
		if isinstance(ret, dict):
			return ret['size']




if __name__ == '__main__':
	import argparse
	parser = argparse.ArgumentParser(usage='%(prog)s command')
	parser.add_argument('-a','--assign',metavar='count',type=int)
	parser.add_argument('-l','--lookup',metavar='volumeId',type=int)
	parser.add_argument('-u','--upload',metavar='filename',type=str)
	parser.add_argument('-f','--fetch',metavar='host/fid',type=str)
	parser.add_argument('-r','--replication',metavar='type',type=str,default=None)
	parser.add_argument('-s','--status', action='store_true')
	args, remaining = parser.parse_known_args()

	client = WeedClient()
	if args.assign:
		ret = client.assign(args.assign,args.replication)
		print type(ret)
		print json.dumps(ret, indent=4)
	elif args.lookup:
		ret = client.lookup(args.lookup)
		print type(ret)
		print json.dumps(ret, indent=4)
	elif args.status:
		ret = client.status()
		print json.dumps(ret, indent=4)
	elif args.upload:
		volume_host, fid = client.assign(1,args.replication)
		ret = client.store(volume_host, fid, args.upload)
		#ret = client.store(volume_host, fid, open(args.upload, 'rb'), name=os.path.basename(args.upload))
		print type(ret)
		print ret
	elif args.fetch:
		volume_host, fid = args.fetch.split('/', 2)
		ret = client.retrieve(volume_host, fid, head=True)
		print ret
	else:
		parser.print_help()
