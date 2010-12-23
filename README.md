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
		uwsgi --pp /opt/imsto/app --vacuum -C 666 -s /tmp/imsto_img.sock -p 2 -M -t 20 --limit-as 128 -m -w imagehandle -d logs/images.log
	 start manage handle:
		uwsgi --pp /opt/imsto/app --vacuum -C 666 -s /tmp/imsto_man.sock -p 1 -M -t 20 --limit-as 128 -m -w managehandle -d logs/manage.log

* open url http://man.imsto.net/

TODO list
---------

- store tool (closed 50%)
- <del>(web) gallery manager</del>
- <del>(web) image upload</del>
- permisions

