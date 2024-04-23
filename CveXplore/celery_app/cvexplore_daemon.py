import json
import os

from dotenv import load_dotenv

user_wd = os.path.expanduser("~/.cvexplore")

load_dotenv(os.path.join(user_wd, ".env"))

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
from CveXplore.core.general.constants import task_status_codes
from CveXplore.core.redis_handler.redis_handler import RedisHandler

logging.setLoggerClass(AppLogger)

config = Configuration

app = Celery(
    "CveXplore",
    broker=f"{config.CELERY_REDIS_URL}{config.CELERY_REDIS_BROKER_DB}",
    backend=f"{config.CELERY_REDIS_URL}{config.CELERY_REDIS_BACKEND_DB}",
    result_extended=True,
    include=["CveXplore.celery_app.cvexplore_daemon"],
    task_time_limit=config.CELERY_TASK_TIME_LIMIT,
    task_default_queue="default",
    broker_connection_retry_on_startup=True,
    result_expires=config.CELERY_RESULT_EXPIRES,
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

    logger.info(
        f"Task post run cost: {cost}, State: {state}, Task: {task}, RetVal: {retval}"
    )

    task.request.update(task_execution_time=cost)

    if "task_slug" in task.request.kwargs:
        task_slug = task.request.kwargs["task_slug"]
    else:
        task_slug = task.name

    if isinstance(retval, Exception) or retval is None:
        task.backend.client.set(
            f"runresult_{task_slug}",
            config.CELERY_TASK_FAILED_ERROR_CODE,
            ex=86400,
        )
        insert_time = int(time.time())
        task.backend.client.zadd(
            f"sortresults_{task_slug}", {f"{task_slug}_{task_id}": insert_time}
        )
        task.backend.client.hset(
            f"{task_slug}_{task_id}",
            mapping={
                "state": state,
                "cost": cost,
                "returns": json.dumps(
                    {
                        "status": config.CELERY_TASK_FAILED_ERROR_CODE,
                        "data": {"out": "", "err": f"{type(retval)}"},
                    }
                ),
                "inserted": insert_time,
                "task_id": task_id,
            },
        )
        task.backend.client.expire(
            name=f"{task_slug}_{task_id}",
            time=config.CELERY_KEEP_TASK_RESULT * 60 * 60 * 24,
        )
    else:
        task.backend.client.set(f"runresult_{task_slug}", retval["status"], ex=86400)
        insert_time = int(time.time())
        task.backend.client.zadd(
            f"sortresults_{task_slug}", {f"{task_slug}_{task_id}": insert_time}
        )
        task.backend.client.hset(
            f"{task_slug}_{task_id}",
            mapping={
                "state": state,
                "cost": cost,
                "returns": json.dumps(retval),
                "inserted": insert_time,
                "task_id": task_id,
            },
        )
        task.backend.client.expire(
            name=f"{task_slug}_{task_id}",
            time=config.CELERY_KEEP_TASK_RESULT * 60 * 60 * 24,
        )

    logger.info("Task execution completed!")


@task_failure.connect
def general_task_failure_config(task_id, exception, traceback, einfo, *args, **kwargs):
    logger = get_task_logger(__name__)

    logger.exception(exception)


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # do tasks every xx seconds
    # sender.add_periodic_task(5.0, crt_test.s())
    pass


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


@app.task(
    autoretry_for=(Exception,),
    max_retries=5,
    retry_backoff=True,
    retry_backoff_max=700,
    retry_jitter=True,
    ignore_result=True,
)
def crt_test(task_slug: str, *args, **kwargs) -> dict:
    """
    General test task with random response

    Args:
        task_slug: Task slug
        args: Task Arguments
        kwargs: Task Keyword arguments

    Returns:
        A dictionary with key "status" with will reflect the status of the task

    Group:
        tasks

    """
    import random

    logger = get_task_logger(__name__)
    logger.info("Testing with OK / NOK response")

    a = random.randrange(20)

    if a % 2 == 0:
        return {"status": task_status_codes.OK}
    else:
        return {"status": task_status_codes.NOK}


@app.task(
    ignore_result=True,
    task_time_limit=1800,
)
def crt_update(task_slug: str, *args, **kwargs) -> dict:
    """
    Task to automatically update the database. Task will only run one instance at the time to prevent the update tasks
    interfering with each other.

    Args:
        task_slug: Task slug
        args: Task Arguments
        kwargs: Task Keyword arguments

    Returns:
        A dictionary with key "status" with will reflect the status of the task

    Group:
        tasks

    """
    from CveXplore import CveXplore

    rh = RedisHandler(redis_client=app.backend.client)

    # Acquiring a lock to prevent this specific task to run twice or more at a time
    with rh.acquire_lock(f"crt_update"):
        try:
            cvex = CveXplore()
            cvex.database.update()
            return {"status": task_status_codes.OK}
        except Exception:
            return {"status": task_status_codes.NOK}
