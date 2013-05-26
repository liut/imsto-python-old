#! /bin/sh

# tested at macosx

### BEGIN INIT INFO
# Provides:          uwsgi imsto
# Required-Start:    $remote_fs $network
# Required-Stop:     $remote_fs $network
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: starts imsto
# Description:       starts imsto
### END INIT INFO

name="imsto"

PATH=/opt/local/bin:/sbin:/usr/sbin:/bin:/usr/bin:/usr/local/bin:/usr/opt/bin

uwsgi_BIN=`which uwsgi`
uwsgi_uid="nobody"
uwsgi_gid="nobody"

uwsgi_pidfile="/var/run/${name}.pid"
uwsgi_config="/etc/uwsgi_apps/${name}.ini"

uwsgi_opts="--ini ${uwsgi_config} --pidfile ${uwsgi_pidfile}"

if [ -z "${uwsgi_BIN}" ]; then
	echo "uwsgi not found or access denied"
	exit 1;
fi


case `echo "testing\c"`,`echo -n testing` in
    *c*,-n*) echo_n=   echo_c=     ;;
    *c*,*)   echo_n=-n echo_c=     ;;
    *)       echo_n=   echo_c='\c' ;;
esac


check_dirs () {

	if [ ! -e $uwsgi_config ]; then
		echo "${uwsgi_config} not found"
		exit 1;
	fi
}

wait_for_pid () {
	try=0

	while test $try -lt 5 ; do

		case "$1" in
			'created')
			if [ -f "$2" ] ; then
				try=''
				break
			fi
			;;

			'removed')
			if [ ! -f "$2" ] ; then
				try=''
				break
			fi
			;;
		esac

		echo $echo_n ".$echo_c"
		try=`expr $try + 1`
		sleep 1
		
	done

}

case "$1" in
	start)
	
		check_dirs
	
		echo $echo_n "Starting ${name} $echo_c"

		$uwsgi_BIN $uwsgi_opts

		if [ "$?" != 0 ] ; then
			echo " failed"
			exit 1
		fi

		wait_for_pid created $uwsgi_pidfile

		if [ -n "$try" ] ; then
			echo " failed"
			exit 1
		else
			echo " done"
		fi
	;;

	stop)
		echo $echo_n "Gracefully shutting down ${name} $echo_c"

		if [ ! -r $uwsgi_pidfile ] ; then
			echo "warning, no pid file found - ${name} is not running ?"
			exit 1
		fi

		#kill -QUIT `cat $uwsgi_pidfile`
		$uwsgi_BIN --stop $uwsgi_pidfile

		wait_for_pid removed $uwsgi_pidfile

		if [ -n "$try" ] ; then
			echo " failed. Use force-quit"
			exit 1
		else
			echo " done"
		fi
	;;

	force-quit)
		echo $echo_n "Terminating ${name} "

		if [ ! -r $uwsgi_pidfile ] ; then
			echo "warning, no pid file found - ${name} is not running ?"
			exit 1
		fi

		kill -KILL `cat $uwsgi_pidfile`

		wait_for_pid removed $uwsgi_pidfile

		if [ -n "$try" ] ; then
			echo " failed"
			exit 1
		else
			echo " done"
		fi
	;;

	restart)
		$0 stop
		$0 start
	;;

	reload)

		echo $echo_n "Reload service ${name} "

		if [ ! -r $uwsgi_pidfile ] ; then
			echo "warning, no pid file found - ${name} is not running ?"
			exit 1
		fi

		#kill -TERM `cat $uwsgi_pidfile`
		$uwsgi_BIN --reload $uwsgi_pidfile

		echo " done"
	;;

	*)
		echo "Usage: $0 {start|stop|force-quit|restart|reload}"
		exit 1
	;;

esac
