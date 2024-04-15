import contextlib
import logging
import time

from celery import Celery
from celery.backends.database import SessionManager
from celery.signals import (
    task_postrun,
    task_retry,
    task_failure,
    task_prerun,
    setup_logging,
)
from celery.utils.log import get_task_logger

from CveXplore.common.config import Configuration
from CveXplore.core.logging.logger_class import AppLogger

logging.setLoggerClass(AppLogger)

config = Configuration

app = Celery(
    "CveXplore",
    broker=f"{config.CELERY_REDIS_URL}{config.CELERY_REDIS_BROKER_DB}",
    backend=f"{config.CELERY_REDIS_URL}{config.CELERY_REDIS_BACKEND_DB}",
    result_extended=True,
    include=["CveXplore.celery_app.cvexplore_daemon"],
    task_time_limit=900,
    task_default_queue="default",
    broker_connection_retry_on_startup=True,
    result_expires=300,
)

execution_times = {}


@setup_logging.connect
def setup_logging(logger, *args, **kwargs):
    # Disregard all celery processing on loggers and let the generic loggerClass handle the configuration of the loggers
    pass


@task_prerun.connect
def general_task_pre_run_config(task_id, task, *args, **kwargs):
    logger = get_task_logger(__name__)

    execution_times[task_id] = time.time()

    task.update_state(state="STARTED")

    logger.info("Task started!")


@task_retry.connect
def general_task_retry_config(request, reason, einfo, *args, **kwargs):
    logger = get_task_logger(__name__)

    logger.warning(f"Task retry initiated reason: {reason}")


@task_postrun.connect
def general_task_post_run_config(task_id, task, retval, state, *args, **kwargs):
    logger = get_task_logger(__name__)

    try:
        cost = time.time() - execution_times.pop(task_id)
    except KeyError:
        cost = -1

    task.request.update(task_execution_time=cost)

    logger.info("Task execution completed!")


@task_failure.connect
def general_task_failure_config(task_id, exception, traceback, einfo, *args, **kwargs):
    logger = get_task_logger(__name__)

    logger.exception(exception)


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # do tasks every xx seconds
    sender.add_periodic_task(5.0, test.s())


@contextlib.contextmanager
def get_db_session():
    session_logger = logging.getLogger(__name__)

    session_manager = SessionManager()
    engine, Session = session_manager.create_session(config.SQLALCHEMY_DATABASE_URI)
    session = Session()

    try:
        yield session
    except Exception as err:
        session_logger.warning(f"Error inserting data into database: {err}")
        session_logger.exception(err)
        session.rollback()
    finally:
        session.close()


@app.task()
def test():
    print("Test")
