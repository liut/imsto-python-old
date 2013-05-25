#!/sbin/runscript

# uwsgi boot script for gentoo only
# install:
# - sudo cp uwsgi.init.gentoo.sh /etc/init.d/uwsgi
# - cd /etc/init.d
# - sudo chmod a+x uwsgi
# - sudo ln -s uwsgi myapp
# - cd /etc/uwsgi_apps
# - sudo vim myapp.ini
# author: liut, 20121210


uwsgi_config="/etc/uwsgi_apps/${SVCNAME}.ini"

command=/usr/local/bin/uwsgi
pidfile=/var/run/${SVCNAME}.pid
command_args="--uid nobody --ini ${uwsgi_config} --pidfile ${pidfile}"

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

