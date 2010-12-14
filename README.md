ImSto: a little image storage
=======================================

requirement
-----------

 * mongodb
 * python
 * nginx + uwsgi


launch development
------------------

* mongodb: 

   mongo localhost/storage
      db.createCollection("img.files",{autoIndexId:false}) 
      db.img.files.ensureIndex({md5:1},{background:true, unique:true, dropDups:true});

* nginx: add config/nginx/host.imsto.conf to nginx.conf

   include /opt/imsto/config/nginx/host.imsto.conf;

* uwsgi: uwsgi -s /tmp/uwsgi_ih.sock --ini config/uwsgi/dev.ini:app_ih


TODO list
---------

- store tool or service
- (web) grid manager
- (web) upload

