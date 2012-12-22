
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

