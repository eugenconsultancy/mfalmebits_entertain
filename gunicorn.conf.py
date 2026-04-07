# gunicorn.conf.py
# ─────────────────────────────────────────────────────────────────────
# Gunicorn configuration for MfalmeBits on a 2 GB RAM / 2 vCPU host.
#
# Launch command (Render Start Command or Procfile):
#   gunicorn core.wsgi:application -c gunicorn.conf.py
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
# If you switch to --worker-class uvicorn.workers.UvicornWorker, reduce
# to 2 workers (each uvicorn worker is heavier than sync).
# ─────────────────────────────────────────────────────────────────────

import multiprocessing
import os

# ── Binding ───────────────────────────────────────────────────────────
# Render injects $PORT; fall back to 8000 for local testing.
port = os.environ.get("PORT", "8000")
bind = f"0.0.0.0:{port}"

# ── Workers ───────────────────────────────────────────────────────────
# Override via GUNICORN_WORKERS env var for easy tuning without code changes.
workers = int(os.environ.get("GUNICORN_WORKERS", 3))

# Threads per worker — allows light concurrency without extra processes
threads = int(os.environ.get("GUNICORN_THREADS", 2))

# Worker class — "sync" for pure WSGI (Django default).
# Switch to "uvicorn.workers.UvicornWorker" for ASGI (+ set workers=2).
worker_class = os.environ.get("GUNICORN_WORKER_CLASS", "sync")

# ── Timeouts ─────────────────────────────────────────────────────────
timeout = 120           # Kill workers that take > 120 s (prevents zombie workers)
graceful_timeout = 30   # Allow 30 s for in-flight requests on SIGTERM
keepalive = 5           # Keep idle HTTP connections alive for 5 s (helps Nginx)

# ── Memory management ────────────────────────────────────────────────
# Recycle workers after N requests to prevent Python memory leaks.
# Jitter adds ±50 requests of randomness so workers don't restart together.
max_requests = 1000
max_requests_jitter = 50

# ── Logging ──────────────────────────────────────────────────────────
# "-" means log to stdout — Render captures stdout automatically.
loglevel = "info"
accesslog = "-"
errorlog = "-"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)sµs'

# ── Process naming ───────────────────────────────────────────────────
proc_name = "mfalmebits"

# ── Performance tweaks ───────────────────────────────────────────────
worker_connections = 1000   # Max simultaneous clients per worker (async workers only)
backlog = 64                # Pending connection queue (low to avoid OOM on busy spikes)

# Preload the Django app in the master process, then fork.
# Saves ~50 MB RAM per worker via copy-on-write memory pages.
# Disable if you use gevent/eventlet workers (incompatible).
preload_app = True

# ── Server hooks ─────────────────────────────────────────────────────

def on_starting(server):
    server.log.info("MfalmeBits Gunicorn starting — workers=%s threads=%s", workers, threads)


def worker_exit(server, worker):
    server.log.info("Worker %s exiting (pid=%s)", worker.pid, worker.pid)


def post_fork(server, worker):
    """
    Called in the child worker after forking.
    Good place to reinitialise connections that shouldn't be shared
    across processes (e.g. database connection pools).
    """
    # Django's ORM opens connections lazily, so no action needed here.
    pass