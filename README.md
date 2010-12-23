ImSto: a little image storage
=======================================

Requirements
-----------

 * MongoDB (GridFS)
 * Python + [pymongo][pymongo] + [magckwand][magckwand]
 * Nginx + [uWSGI][uWSGI]


Launch development
------------------

* mongodb: 

	 mongo localhost/storage

		db.createCollection("img.files",{autoIndexId:false});
		db.img.files.ensureIndex({md5:1},{background:true, unique:true, dropDups:true});

* nginx: add config/nginx/host.imsto.conf to nginx.conf

		include /opt/imsto/config/nginx/host.imsto.conf;
		
	vim /etc/hosts
	
		127.0.0.1   m.imsto.net
		127.0.0.1   man.imsto.net

* uwsgi: there have two socket service

	 start image handle:
		sudo ./server_image.sh start
	 start manage handle:
		sudo ./server_man.sh start

* open url http://man.imsto.net/

TODO list
---------

- store tool (closed 60%)
- <del>(web) gallery manager</del>
- <del>(web) image upload</del>
- permisions
- demo: <http://demo.imsto.org:81/>

[pymongo]: http://pypi.python.org/pypi/pymongo/
[magckwand]: http://pypi.python.org/pypi/magickwand/0.2
[uWSGI]: http://projects.unbit.it/uwsgi/