# gunicorn.conf.py
# ─────────────────────────────────────────────────────────────────────
# Gunicorn configuration for MfalmeBits on a 2 GB RAM / 2 vCPU host.
# Optimized for production with Nginx, M-Pesa, and Stripe integrations.
#
# Launch command (Systemd service or Procfile):
#   gunicorn core.wsgi:application -c gunicorn.conf.py
#
# Architecture:
#   Nginx (port 80/443) → Gunicorn Socket → Django Application
#
# Worker sizing rationale
# ─────────────────────────
# Formula: (2 × CPU_cores) + 1
# On 2 vCPUs that gives 5 workers — but Django + Jazzmin + PostgreSQL
# uses ~250 MB RSS per worker.  5 workers × 250 MB = 1.25 GB, leaving
# only 750 MB for the OS, Redis, and PostgreSQL connections.
#
# Safe choice for 2 GB:
#   3 sync workers × 2 threads = 6 concurrent requests, ~750 MB RSS.
#
# M-Pesa/Stripe consideration:
#   External API calls may take 5-10 seconds, so increased timeout to 60s.
#
# Socket vs Network Port:
#   Using Unix socket for better performance and security behind Nginx.
# ─────────────────────────────────────────────────────────────────────

import multiprocessing
import os

# ─────────────────────────────────────────────────────────────────────
# BINDING — Unix Socket for Nginx (Production) / Network Port (Dev)
# ─────────────────────────────────────────────────────────────────────
# Use a socket for better performance on your VPS with Nginx
# This is the professional standard for Nginx communication
bind = "unix:/run/gunicorn.sock"

# Fallback for local testing or when LOCAL_DEV environment variable is set
if os.environ.get("LOCAL_DEV", "").lower() == "true":
    port = os.environ.get("PORT", "8000")
    bind = f"0.0.0.0:{port}"
    print(f"Gunicorn running in development mode on port {port}")
else:
    print("Gunicorn running in production mode with Unix socket: /run/gunicorn.sock")

# ─────────────────────────────────────────────────────────────────────
# WORKER CONFIGURATION
# ─────────────────────────────────────────────────────────────────────
# Override via GUNICORN_WORKERS env var for easy tuning without code changes.
workers = int(os.environ.get("GUNICORN_WORKERS", 3))

# Threads per worker — allows light concurrency without extra processes
# For I/O bound operations (M-Pesa/Stripe API calls), threads help
threads = int(os.environ.get("GUNICORN_THREADS", 2))

# Worker class — "sync" for pure WSGI (Django default).
# Switch to "uvicorn.workers.UvicornWorker" for ASGI (+ set workers=2).
worker_class = os.environ.get("GUNICORN_WORKER_CLASS", "sync")

# Number of workers for async worker classes (gevent, uvicorn, etc.)
# Not used with sync workers, but defined for safety
worker_connections = int(os.environ.get("GUNICORN_WORKER_CONNECTIONS", 1000))

# ─────────────────────────────────────────────────────────────────────
# TIMEOUTS — Increased for M-Pesa/Stripe API calls
# ─────────────────────────────────────────────────────────────────────
# M-Pesa/Stripe API calls may take 5-15 seconds due to network latency
# Increased timeout to prevent worker kills during payment processing
timeout = int(os.environ.get("GUNICORN_TIMEOUT", 60))           # 60 seconds for API responses
graceful_timeout = int(os.environ.get("GUNICORN_GRACEFUL_TIMEOUT", 30))  # Allow in-flight requests
keepalive = int(os.environ.get("GUNICORN_KEEPALIVE", 2))        # 2 seconds for Nginx keepalive

# ─────────────────────────────────────────────────────────────────────
# MEMORY MANAGEMENT — Prevent memory leaks
# ─────────────────────────────────────────────────────────────────────
# Recycle workers after N requests to prevent Python memory leaks.
# Jitter adds ±50 requests of randomness so workers don't restart together.
# Essential for Django + Jazzmin which can accumulate memory over time
max_requests = int(os.environ.get("GUNICORN_MAX_REQUESTS", 1000))
max_requests_jitter = int(os.environ.get("GUNICORN_MAX_REQUESTS_JITTER", 50))

# ─────────────────────────────────────────────────────────────────────
# LOGGING — Capture all output for monitoring
# ─────────────────────────────────────────────────────────────────────
# "-" means log to stdout — systemd/journald captures automatically.
loglevel = os.environ.get("GUNICORN_LOGLEVEL", "info")
accesslog = "-"
errorlog = "-"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)sµs'

# ─────────────────────────────────────────────────────────────────────
# PROCESS NAMING — For easy identification in htop/ps
# ─────────────────────────────────────────────────────────────────────
# setproctitle is required for this to work (added to requirements.txt)
proc_name = os.environ.get("GUNICORN_PROC_NAME", "mfalmebits_gunicorn")

# ─────────────────────────────────────────────────────────────────────
# PERFORMANCE TWEAKS
# ─────────────────────────────────────────────────────────────────────
backlog = int(os.environ.get("GUNICORN_BACKLOG", 64))           # Pending connection queue
max_worker_memory = int(os.environ.get("MAX_WORKER_MEMORY_MB", 300))  # Max memory per worker

# Preload the Django app in the master process, then fork.
# Saves ~50 MB RAM per worker via copy-on-write memory pages.
# Disable if you use gevent/eventlet workers (incompatible).
# Enabled by default for memory savings on 2GB VPS
preload_app = os.environ.get("GUNICORN_PRELOAD_APP", "true").lower() == "true"

# Daemon mode — Set to False when running as systemd service
daemon = os.environ.get("GUNICORN_DAEMON", "false").lower() == "true"

# PID file location (when daemon mode is enabled)
pidfile = os.environ.get("GUNICORN_PIDFILE", "/run/gunicorn.pid")

# User and group to run as (for socket permissions)
# Nginx typically runs as www-data:www-data
user = os.environ.get("GUNICORN_USER", "www-data")
group = os.environ.get("GUNICORN_GROUP", "www-data")

# ─────────────────────────────────────────────────────────────────────
# SERVER HOOKS — Lifecycle event handlers
# ─────────────────────────────────────────────────────────────────────

def on_starting(server):
    """Called before the master process is initialized."""
    server.log.info("=" * 60)
    server.log.info("MfalmeBits Gunicorn starting")
    server.log.info(f"Workers: {workers}")
    server.log.info(f"Threads per worker: {threads}")
    server.log.info(f"Worker class: {worker_class}")
    server.log.info(f"Timeout: {timeout}s")
    server.log.info(f"Bind: {bind}")
    server.log.info(f"Process name: {proc_name}")
    server.log.info(f"Preload app: {preload_app}")
    server.log.info("=" * 60)


def on_reload(server):
    """Called before the master process is reloaded."""
    server.log.info("MfalmeBits Gunicorn reloading...")


def when_ready(server):
    """Called just after the server is started."""
    server.log.info("MfalmeBits Gunicorn is ready to accept requests")
    server.log.info(f"Listening on: {bind}")


def worker_int(worker):
    """Called when a worker receives the SIGINT signal."""
    worker.log.info(f"Worker {worker.pid} received SIGINT, shutting down gracefully")


def worker_abort(worker):
    """Called when a worker receives the SIGABRT signal."""
    worker.log.warning(f"Worker {worker.pid} received SIGABRT, forcing shutdown")


def worker_exit(server, worker):
    """Called after a worker has exited."""
    server.log.info(f"Worker {worker.pid} has exited")


def post_fork(server, worker):
    """
    Called in the child worker after forking.
    Good place to reinitialize connections that shouldn't be shared
    across processes (e.g., database connection pools, Redis connections).
    """
    # Django's ORM opens connections lazily, so no action needed here.
    # However, if you have custom connection pools, reinitialize them here.
    worker.log.debug(f"Worker {worker.pid} forked and ready")


def pre_fork(server, worker):
    """Called just before a worker is forked."""
    server.log.debug(f"Pre-forking worker {worker.pid}")


def post_worker_init(worker):
    """Called just after a worker has been initialized."""
    worker.log.info(f"Worker {worker.pid} initialized successfully")


def child_exit(server, worker):
    """Called just after a worker has been exited."""
    server.log.info(f"Worker {worker.pid} has exited, cleaning up")


# ─────────────────────────────────────────────────────────────────────
# SECURITY & LIMITS
# ─────────────────────────────────────────────────────────────────────
# Limit request line size to prevent buffer overflow attacks
limit_request_line = int(os.environ.get("GUNICORN_LIMIT_REQUEST_LINE", 4094))

# Limit request headers size
limit_request_fields = int(os.environ.get("GUNICORN_LIMIT_REQUEST_FIELDS", 100))
limit_request_field_size = int(os.environ.get("GUNICORN_LIMIT_REQUEST_FIELD_SIZE", 8190))

# ─────────────────────────────────────────────────────────────────────
# HEALTH CHECK ENDPOINT (for monitoring)
# ─────────────────────────────────────────────────────────────────────
# Uncomment if you want to expose a health check endpoint
# def worker_int(worker):
#     worker.log.info("Worker received SIGINT, shutting down")
#
# def worker_abort(worker):
#     worker.log.info("Worker received SIGABRT, forcing shutdown")