"""Unused Celery app placeholder.

Celery is not required for local/dev in this project since background work
is performed via lightweight threads in complaints.utils_async.
This file remains only to avoid import errors in any environments that
reference config.celery by convention. It does not initialize a worker.
"""
