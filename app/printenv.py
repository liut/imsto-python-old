


def print_env(environ, start_response):
    """list environ items"""
    start_response('200 OK', [('Content-Type', 'text/plain')])
    return ['\n'.join(['%s: %r' % item for item in environ.items()])]

application = print_env

