#!/bin/sh

## $Id$

ROOTNAME="imsto"
PATH=/opt/local/bin:/sbin:/usr/sbin:/bin:/usr/bin:/usr/local/bin

OS=`uname -s`
echo $OS
if [ $OS = "Darwin" ]; then
	PREFIX=/opt
else
	PREFIX=/var
fi

if [ ! -d $PREFIX ]; then
	echo "$PREFIX not exists"
	exit 1;
fi

if [ ! -e ${PREFIX}/$ROOTNAME ]; then
	echo "path: ${PREFIX}/$ROOTNAME not exists"
	exit 1;
fi

STO_DIR=${PREFIX}/$ROOTNAME
CACHE_DIR=${STO_DIR}/cache

## Cache
[ ! -d $CACHE_DIR -a ! -e $CACHE_DIR ] && mkdir $CACHE_DIR
if [ -d $CACHE_DIR ]; then
	chmod a+w $CACHE_DIR
	## Cache: dirs
	for dir in thumb images eggs
	do
		[ -e $CACHE_DIR/$dir ] || mkdir $CACHE_DIR/$dir
		if [ -d $CACHE_DIR/$dir ]; then
			chmod a+w $CACHE_DIR/$dir
		fi
	done
fi


