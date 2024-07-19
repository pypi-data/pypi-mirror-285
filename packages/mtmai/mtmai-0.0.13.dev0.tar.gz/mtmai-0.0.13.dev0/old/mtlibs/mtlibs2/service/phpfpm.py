#!/usr/bin/env python3
import sys
import os
from os.path import join
from pathlib import Path
import subprocess
import time
import subprocess
from os import path
import threading
import yaml
import logging
import shutil
from mtlibs import process_helper
from mtlibs import mtutils
import platform

logger = logging.getLogger(__name__)


class PhpFpmService():
    def __init__(self):
        pass
        # self.html_root = settings.getHtmlRoot()
        # logger.info(f"html root {self.html_root}")
        # self.smapiRoot = "/smapi"

    def start(self):
        logger.info("启动phpfpm服务进程")
        curr_php_fpm_conf = os.join(os.getcwd(), "php-fpm.conf")
        if Path(curr_php_fpm_conf).exists():
            logger.info(f"复制php-fpm配置文件到 /etc/php/7.4/fpm/php-fpm.conf")
            shutil.copy(curr_php_fpm_conf, "/etc/php/7.4/fpm/php-fpm.conf")
        port = 9000
        check_port = mtutils.get_tcp_open_port(9000)
        if not check_port:
            logger.info(f"tcp port opend {port},skip start phpFpm service")
        else:
            start_phpfpm()

    def stop(self):
        pass


def start_phpfpm(port=9000):
    fpmconf = """;;;;;;;;;;;;;;;;;;;;;
  
; FPM Configuration ;
;;;;;;;;;;;;;;;;;;;;;
; /etc/init.d/php7.4-fpm restart
; /etc/php/7.4/fpm/php-fpm.conf
; All relative paths in this configuration file are relative to PHP's install
; prefix (/usr). This prefix can be dynamically changed by using the
; '-p' argument from the command line.

;;;;;;;;;;;;;;;;;;
; Global Options ;
;;;;;;;;;;;;;;;;;;

[global]
; Pid file
; Note: the default prefix is /var
; Default Value: none
; Warning: if you change the value here, you need to modify systemd
; service PIDFile= setting to match the value here.
pid = /run/php7.4-fpm.pid

; Error log file
; If it's set to "syslog", log is sent to syslogd instead of being written
; into a local file.
; Note: the default prefix is /var
; Default Value: log/php-fpm.log
error_log = /var/log/php7.4-fpm.log

; syslog_facility is used to specify what type of program is logging the
; message. This lets syslogd specify that messages from different facilities
; will be handled differently.
; See syslog(3) for possible values (ex daemon equiv LOG_DAEMON)
; Default Value: daemon
;syslog.facility = daemon

; syslog_ident is prepended to every message. If you have multiple FPM
; instances running on the same server, you can change the default value
; which must suit common needs.
; Default Value: php-fpm
;syslog.ident = php-fpm

; Log level
; Possible Values: alert, error, warning, notice, debug
; Default Value: notice
;log_level = notice

; Log limit on number of characters in the single line (log entry). If the
; line is over the limit, it is wrapped on multiple lines. The limit is for
; all logged characters including message prefix and suffix if present. However
; the new line character does not count into it as it is present only when
; logging to a file descriptor. It means the new line character is not present
; when logging to syslog.
; Default Value: 1024
;log_limit = 4096

; Log buffering specifies if the log line is buffered which means that the
; line is written in a single write operation. If the value is false, then the
; data is written directly into the file descriptor. It is an experimental
; option that can potentionaly improve logging performance and memory usage
; for some heavy logging scenarios. This option is ignored if logging to syslog
; as it has to be always buffered.
; Default value: yes
;log_buffering = no

; If this number of child processes exit with SIGSEGV or SIGBUS within the time
; interval set by emergency_restart_interval then FPM will restart. A value
; of '0' means 'Off'.
; Default Value: 0
;emergency_restart_threshold = 0

; Interval of time used by emergency_restart_interval to determine when
; a graceful restart will be initiated. This can be useful to work around
; accidental corruptions in an accelerator's shared memory.
; Available Units: s(econds), m(inutes), h(ours), or d(ays)
; Default Unit: seconds
; Default Value: 0
;emergency_restart_interval = 0

; Time limit for child processes to wait for a reaction on signals from master.
; Available units: s(econds), m(inutes), h(ours), or d(ays)
; Default Unit: seconds
; Default Value: 0
;process_control_timeout = 0

; The maximum number of processes FPM will fork. This has been designed to control
; the global number of processes when using dynamic PM within a lot of pools.
; Use it with caution.
; Note: A value of 0 indicates no limit
; Default Value: 0
; process.max = 128

; Specify the nice(2) priority to apply to the master process (only if set)
; The value can vary from -19 (highest priority) to 20 (lowest priority)
; Note: - It will only work if the FPM master process is launched as root
; - The pool process will inherit the master process priority
; unless specified otherwise
; Default Value: no set
; process.priority = -19

; Send FPM to background. Set to 'no' to keep FPM in foreground for debugging.
; Default Value: yes
;daemonize = yes

; Set open file descriptor rlimit for the master process.
; Default Value: system defined value
;rlimit_files = 1024

; Set max core size rlimit for the master process.
; Possible Values: 'unlimited' or an integer greater or equal to 0
; Default Value: system defined value
;rlimit_core = 0

; Specify the event mechanism FPM will use. The following is available:
; - select (any POSIX os)
; - poll (any POSIX os)
; - epoll (linux >= 2.5.44)
; - kqueue (FreeBSD >= 4.1, OpenBSD >= 2.9, NetBSD >= 2.0)
; - /dev/poll (Solaris >= 7)
; - port (Solaris >= 10)
; Default Value: not set (auto detection)
;events.mechanism = epoll

; When FPM is built with systemd integration, specify the interval,
; in seconds, between health report notification to systemd.
; Set to 0 to disable.
; Available Units: s(econds), m(inutes), h(ours)
; Default Unit: seconds
; Default value: 10
;systemd_interval = 10

;;;;;;;;;;;;;;;;;;;;
; Pool Definitions ;
;;;;;;;;;;;;;;;;;;;;

; Multiple pools of child processes may be started with different listening
; ports and different management options. The name of the pool will be
; used in logs and stats. There is no limitation on the number of pools which
; FPM can handle. Your system will tell you anyway :)

; Include one or more files. If glob(3) exists, it is used to include a bunch of
; files from a glob(3) pattern. This directive can be used everywhere in the
; file.
; Relative path can also be used. They will be prefixed by:
; - the global prefix if it's been set (-p argument)
; - /usr otherwise
include=/etc/php/7.4/fpm/pool.d/*.conf


;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; custom begin
;;;;;;;;;;;;;;
listen = 127.0.0.1:@@PORT@@
; Clear environment in FPM workers
; Prevents arbitrary environment variables from reaching FPM worker processes
; by clearing the environment in workers before env vars specified in this
; pool configuration are added.
; Setting to "no" will make all environment variables available to PHP code
; via getenv(), $_ENV and $_SERVER.
; Default Value: yes
clear_env = no
user = nginx
"""
# 注意（上方配置）当前用户 user = nginx，跟nginx配置的用户一致。
    with open("/etc/php/7.4/fpm/php-fpm.conf", "w") as f:
        f.write(fpmconf.replace("@@PORT@@", str(port)))

    phpfpm_cp = process_helper.exec("/etc/init.d/php7.4-fpm restart")
    if phpfpm_cp.returncode == 0:
        logger.info("phpfpm 启动成功")
    else:
        logger.info("phpfpm 启动失败")
