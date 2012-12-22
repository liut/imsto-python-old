#!/sbin/runscript

# imsto boot script for gentoo only
# install: sudo cp imsto-img.init.sh /etc/init.d/imsto-img
# author: liut, 20121210


uwsgi_config="/var/imsto/config/uwsgi/prd.ini"

command=/usr/local/bin/uwsgi
pidfile=/var/run/${SVCNAME}.pid
command_args="--uid nobody --ini ${uwsgi_config}:app_img --pidfile ${pidfile}"

extra_started_commands="reload"

depend() {
	need net
}

start() {
	ebegin "Starting ${SVCNAME}"
	${command} ${command_args} &>/dev/null
	eend $? "Failed to start ${SVCNAME}"
}

stop() {
	ebegin "Stopping ${SVCNAME}"
	${command} --stop ${pidfile} &>/dev/null
	eend $? "Failed to stop ${SVCNAME}"
}

reload() {
	ebegin "Refreshing ${SVCNAME} configuration"
	${command} --reload ${pidfile} &>/dev/null
	eend $? "Failed to reload ${SVCNAME}"
}

