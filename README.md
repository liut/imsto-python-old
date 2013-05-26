ImSto: a little image storage
=======================================

Requirements
-----------

 * MongoDB (GridFS)
 * Python 2.7 + [pymongo][pymongo]
 * [ImageMagick][ImageMagick] or PIL
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
	
		127.0.0.1   m.imsto.net  man.imsto.net

* uwsgi: there have two socket service

	 start image handle:
		`sudo ./sbin/server_image.sh start`
	
	 start manage handle:
		`./server_man.sh start`

* open url http://man.imsto.net/




TODO list
---------

- store tool (closed 80%)
- (web) gallery manager (need refactory)
- (web) image upload (need refactory)
- permisions & auth
- demo: [demo]

[pymongo]: http://pypi.python.org/pypi/pymongo/
[ImageMagick]: http://www.imagemagick.org/
[uWSGI]: http://projects.unbit.it/uwsgi/
[demo]: http://demo.imsto.org/
