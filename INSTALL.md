
Installation
------------

### Gentoo Linux

* add this line to your make.conf

    `USE_PYTHON="2.7 3.1 3.2"`

* `sudo emerge -av imagemagick`
* `sudo emerge -av dev-lang/python:2.7`
* `sudo eselect python set python2.7`
* `sudo emerge -av mongodb`
* `sudo emerge -av dev-python/pip`
* `sudo pip install pymongo`

### OSX

* `sudo port install ImageMagick +no_x11`
* `sudo port install python27`
* `sudo port install mongodb`
* `sudo port install py27-pymongo`


## Common: uWSGI

* `wget http://projects.unbit.it/downloads/uwsgi-lts.tar.gz`
* `tar zxvf uwsgi-lts.tar.gz`
* `cd uwsgi-$VERSION`
* `make`
* `cp uwsgi /usr/local/bin/`

## ImSto

* `cd /opt`
* `git clone git://github.com/liut/imsto.git`
* `cd imsto`
* `less README.md`: read launch development


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
