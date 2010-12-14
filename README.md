ImSto: a little image storage
=======================================

requirement
-----------

 * mongodb
 * python
 * nginx + uwsgi


launch development
------------------

* nginx: add config/nginx/host.imsto.conf to nginx.conf
* uwsgi: uwsgi -s /tmp/uwsgi_ih.sock --ini config/uwsgi/dev.ini:app_ih


TODO list
---------

- store tool or service
- (web) grid manager
- (web) upload

