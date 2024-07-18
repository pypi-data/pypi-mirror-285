import inspect
import logging
from contextlib import contextmanager
from functools import wraps

from django.conf import settings
from django.core.management.base import BaseCommand
from kazoo.client import KazooClient
from kazoo.protocol.states import KazooState

logger = logging.getLogger(__name__)


def zk_listener(state: KazooState):
    logger.info("zk state changed: %s", state)
    if state == KazooState.LOST:
        exit(1)


@contextmanager
def lock(lock_name):
    _status_file("0")

    if not settings.ZOOKEEPER_LOCKS_ENABLED:
        logger.warning("zookeeper locks currently disabled in settings, adjust ZOOKEEPER_LOCKS_ENABLED if not intended")
        yield
        return

    if not settings.ZOOKEEPER_LOCKS_HOSTS:
        logger.error("zookeeper locks enabled but no hosts specified, adjust ZOOKEEPER_LOCKS_HOSTS")
        yield
        return

    zk = KazooClient(hosts=settings.ZOOKEEPER_LOCKS_HOSTS)
    zk.add_listener(zk_listener)
    zk.start()

    lock = zk.Lock(f"/django/{lock_name}")

    logger.info("acquiring lock %s", lock_name)
    _status_file("1")

    with lock:
        logger.info("lock %s acquired", lock_name)
        _status_file("2")
        yield

    lock.release()
    logger.info("lock %s released", lock_name)
    zk.stop()
    logger.info("zk stopped")


def locked(func_or_name=None, **lock_kwargs):
    """
    Decorator to apply the `lock()` context manager to a function or class

    :param func_or_name: decorated function/class - used as lock name
    :param lock_kwargs: passed directly to `lock()`, refer to its documentation
    :return: decorated function/class
    """

    def decorator(func):
        if func_or_name and func_or_name != func:
            name = func_or_name
        else:
            name = f"{func.__module__}.{func.__name__}"

        if inspect.isclass(func):
            if not issubclass(func, BaseCommand):
                raise NotImplementedError("only django BaseCommand subclasses are supported for now")

            orig_handle = func.handle

            @wraps(func.handle)
            def new_handle(self, *args, **kwargs):
                with lock(name, **lock_kwargs):
                    return orig_handle(self, *args, **kwargs)

            func.handle = new_handle

            return func
        else:

            @wraps(func)
            def wrapper(*args, **kwds):
                with lock(name, **lock_kwargs):
                    return func(*args, **kwds)

            return wrapper

    if func_or_name and callable(func_or_name):
        return decorator(func_or_name)
    return decorator


def _status_file(message):
    if settings.ZOOKEEPER_LOCKS_STATUS_FILE is None:
        return
    try:
        with open(settings.ZOOKEEPER_LOCKS_STATUS_FILE, "w") as _f:
            _f.write(message)
    except Exception:
        # log but don't break anything
        logger.exception("failed to update lock status file %s", settings.ZOOKEEPER_LOCKS_STATUS_FILE)
