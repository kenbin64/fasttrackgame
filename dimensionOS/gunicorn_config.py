"""
Gunicorn configuration for DimensionOS production deployment
"""

import multiprocessing

# Server socket
bind = "127.0.0.1:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
worker_connections = 1000
timeout = 60
keepalive = 2

# Logging
accesslog = "/var/log/dimensionos/access.log"
errorlog = "/var/log/dimensionos/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "dimensionos"

# Server mechanics
daemon = False
pidfile = "/var/run/dimensionos.pid"
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (handled by nginx, not gunicorn)
# keyfile = None
# certfile = None

