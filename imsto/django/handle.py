
import os
from imsto import load_imsto, UrlError, guess_mimetype
from django.http import HttpResponse, HttpResponseNotFound, StreamingHttpResponse
from django.conf import settings

__all__ = ['ImageHandle', 'ManageHandle']

def ImageHandle(request, path):
	environ = request.META
	SECTION = get_section(request.META)

	imsto = load_imsto(SECTION)
	try:
		dst_file, dst_path = imsto.load(path)
	except UrlError, e:
		return HttpResponseNotFound(e.message)
	except Exception, e:
		raise
	finally:
		imsto.close()

	THUMB_PATH = imsto.get_config('thumb_path').rstrip('/')
	mimetype = guess_mimetype(dst_path)
	server_soft = environ.get('SERVER_SOFTWARE','')
	if server_soft[:5] == 'nginx' and os.name != 'nt':
		print('path: {0}/{1}'.format(THUMB_PATH, dst_path))
		response = HttpResponse(content_type=mimetype)
		response['X-Accel-Redirect'] = '{0}/{1}'.format(THUMB_PATH, dst_path)
		return response

	fd = open(dst_file,'r')
	response = StreamingHttpResponse(fd, content_type=mimetype)
	response['Content-Length'] = os.path.getsize(dst_file)
	response['Via'] = 'imsto'
	return response
	#return environ['wsgi.file_wrapper'](fd, 4096)

def ManageHandle(request, path):
	#print request
	#print path
	# TODO:
	return HttpResponse('manage')

def get_section(environ):
	if hasattr(settings, 'IMSTO_SECTION'):
		return settings.IMSTO_SECTION
	elif environ.has_key('IMSTO_SECTION'):
		return environ.get('IMSTO_SECTION')
	else:
		return 'imsto'
