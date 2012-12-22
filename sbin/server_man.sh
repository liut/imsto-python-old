#! /bin/sh

### BEGIN INIT INFO
# Provides:          uwsgi imsto
# Required-Start:    $remote_fs $network
# Required-Stop:     $remote_fs $network
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: starts imsto
# Description:       starts imsto
### END INIT INFO

name="manage"
uwsgi_module="managehandle"
uwsgi_socket="/tmp/imsto_man.sock"

prefix=/opt/imsto
#exec_prefix=${prefix}

PATH=/opt/local/bin:/sbin:/usr/sbin:/bin:/usr/bin:/usr/local/bin:/usr/opt/bin
PYTHON_EGG_CACHE=${prefix}/cache/eggs

uwsgi_BIN=`which uwsgi`
uwsgi_pidfile="${prefix}/logs/${name}.pid"
uwsgi_logfile="${prefix}/logs/${name}.log"
uwsgi_flags="--pp ${prefix}/app --vacuum -C -p 1 -M -t 20 --limit-as 32 -m -w ${uwsgi_module}"

uwsgi_opts="--pidfile ${uwsgi_pidfile} -s ${uwsgi_socket} -d ${uwsgi_logfile} ${uwsgi_flags}"
# --uid ${uwsgi_uid} --gid ${uwsgi_gid}

#echo "${uwsgi_BIN}"
if [ -z "${uwsgi_BIN}" ]; then
	echo "uwsgi not found or access denied"
	exit 1;
fi


case `echo "testing\c"`,`echo -n testing` in
    *c*,-n*) echo_n=   echo_c=     ;;
    *c*,*)   echo_n=-n echo_c=     ;;
    *)       echo_n=   echo_c='\c' ;;
esac

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

		kill -QUIT `cat $uwsgi_pidfile`

		wait_for_pid removed $uwsgi_pidfile

		if [ -n "$try" ] ; then
			echo " failed. Use force-exit"
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

		echo $echo_n "Reload service ${name} $echo_c"

		if [ ! -r $uwsgi_pidfile ] ; then
			echo "warning, no pid file found - ${name} is not running ?"
			exit 1
		fi

		kill -TERM `cat $uwsgi_pidfile`

		echo " done"
	;;

	*)
		echo "Usage: $0 {start|stop|force-quit|restart|reload}"
		exit 1
	;;

esac
