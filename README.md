ImSto: a little image storage
=======================================

Requirements
-----------

 * MongoDB (GridFS)
 * Python + pymongo + PIL
 * Nginx + uWSGI


Launch development
------------------

* mongodb: 

   `mongo localhost/storage`
      db.createCollection("img.files",{autoIndexId:false});
      db.img.files.ensureIndex({md5:1},{background:true, unique:true, dropDups:true});

* nginx: add config/nginx/host.imsto.conf to nginx.conf

   `include /opt/imsto/config/nginx/host.imsto.conf;`

* uwsgi: `uwsgi -s /tmp/uwsgi_ih.sock --ini config/uwsgi/dev.ini:app_ih`


TODO list
---------

- store tool and service
- (web) gallery manager
- (web) image upload

