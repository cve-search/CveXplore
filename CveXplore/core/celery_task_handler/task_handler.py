import ast
import collections
import inspect
import json
import logging
from datetime import datetime
from itertools import zip_longest
from urllib.parse import urlparse

import pytz
from celery.schedules import schedule, crontab
from redbeat import RedBeatSchedulerEntry
from redbeat.decoder import RedBeatJSONEncoder
from redbeat.schedulers import ensure_conf
from redis import Redis
from redis.exceptions import ConnectionError as RedisConnectionError

from CveXplore.celery_app.cvexplore_daemon import app
from CveXplore.common.config import Configuration
from CveXplore.core.general.utils import timestampTOdatetime
from CveXplore.core.logging.logger_class import AppLogger
from CveXplore.errors.tasks import TaskNotFoundError

logging.setLoggerClass(AppLogger)

TASK_START_MODULE = "CveXplore.celery_app.cvexplore_daemon"
TASK_START_STRING = "CveXplore.celery_app.cvexplore_daemon.crt_"

task_descriptions = {
    k: str(inspect.getdoc(v)).replace("\n", " ")
    for (k, v) in app.tasks.items()
    if k.startswith(TASK_START_STRING)
}


class CveXploreEntry(RedBeatSchedulerEntry):

    def __init__(
        self,
        name=None,
        task=None,
        schedule=None,
        args=None,
        kwargs=None,
        enabled=True,
        options=None,
        redis_broker=None,
        **clsargs,
    ):
        super().__init__(
            name=str(name),
            task=task,
            schedule=schedule,
            args=args,
            kwargs=kwargs,
            options=options,
            **clsargs,
        )

        self.enabled = enabled
        ensure_conf(self.app)

        self.redis_broker = redis_broker

    def save(self):
        definition = {
            "name": self.name,
            "task": self.task,
            "args": self.args,
            "kwargs": self.kwargs,
            "options": self.options,
            "schedule": self.schedule,
            "enabled": self.enabled,
        }
        meta = {
            "last_run_at": self.last_run_at,
        }
        with self.redis_broker.pipeline() as pipe:
            pipe.hset(
                self.key, "definition", json.dumps(definition, cls=RedBeatJSONEncoder)
            )
            pipe.hsetnx(self.key, "meta", json.dumps(meta, cls=RedBeatJSONEncoder))
            pipe.zadd(self.app.redbeat_conf.schedule_key, {self.key: self.score})
            pipe.execute()

        return self


class Task(object):
    def __init__(
        self,
        name: str,
        task: str,
        run: schedule | crontab = None,
        args: list = None,
        kwargs: dict = None,
        enabled: bool = True,
        last_run_at: datetime = None,
        total_run_count: int = 0,
        next_run_at: datetime = None,
    ):
        self.name = name
        self.task = (
            task if task.startswith(TASK_START_STRING) else f"{TASK_START_STRING}{task}"
        )
        self.run = run
        self.args = args if args is not None else []
        self.kwargs = kwargs if kwargs is not None else {}
        self.kwargs["task_slug"] = self.name
        self.enabled = enabled

        try:
            self.description = task_descriptions[self.task]
            self.periodic_daemon_task = False
        except KeyError:
            # daemon task
            self.description = ""
            self.periodic_daemon_task = True

        self.last_run_at = last_run_at
        self.total_run_count = total_run_count
        self.next_run_at = next_run_at

        self.task_start_string = TASK_START_STRING

        if isinstance(self.run, schedule):
            self.crontab = False
        else:
            self.crontab = True

        self.config = Configuration

        parsed_url = urlparse(self.config.REDIS_URL)

        self.redis_broker = Redis(
            host=parsed_url.hostname,
            port=parsed_url.port,
            db=int(self.config.CELERY_REDIS_BROKER_DB),
        )

        self.redis_backend = Redis(
            host=parsed_url.hostname,
            port=parsed_url.port,
            db=int(self.config.CELERY_REDIS_BACKEND_DB),
        )

        status = self.redis_backend.get(f"runresult_{self.name}")

        if status is not None:
            if isinstance(status, dict):
                status = self.decode_redis_output(status)
            else:
                status = int(status.decode())

        self.last_run_result = status

        self.logger = logging.getLogger(__name__)

    @property
    def is_enabled(self):
        return self.enabled

    def batcher(self, iterable, n):
        args = [iter(iterable)] * n
        return zip_longest(*args)

    def decode_redis_output(self, src):
        if isinstance(src, list):
            rv = list()
            for key in src:
                rv.append(self.decode_redis_output(key))
            return rv
        elif isinstance(src, dict):
            rv = dict()
            for key in src:
                if not isinstance(key, str):
                    rv[key.decode()] = self.decode_redis_output(src[key])
                else:
                    rv[key] = self.decode_redis_output(src[key])
            return rv
        elif isinstance(src, bytes):
            try:
                return ast.literal_eval(src.decode())
            except Exception:
                return src.decode()
        elif src is None:
            return src
        else:
            raise Exception("type not handled: " + type(src))

    def get_all_task_results(self):
        for keybatch in self.batcher(
            self.redis_backend.scan_iter(f"{self.name}_*"), 500
        ):
            my_pipeline = self.redis_backend.pipeline()
            cleaned_keybatch = [x.decode("utf-8") for x in keybatch if x is not None]
            for key in cleaned_keybatch:
                my_pipeline.hgetall(key)
            data = []
            for d in my_pipeline.execute():
                cleaned_data = self.decode_redis_output(d)
                data.append(cleaned_data)

            yield data

    def get_sorted_task_results(self, limit: int, desc: bool = True):
        task_results = self.redis_backend.zrange(
            f"sortresults_{self.name}", 0, limit, desc=desc, withscores=True
        )
        # fetch the keys
        key_list = [x[0] for x in task_results]

        my_pipeline = self.redis_backend.pipeline()
        cleaned_keybatch = [x.decode("utf-8") for x in key_list if x is not None]
        for key in cleaned_keybatch:
            my_pipeline.hgetall(key)
        data = []
        for d in my_pipeline.execute():
            cleaned_data = self.decode_redis_output(d)
            data.append(cleaned_data)

        return data

    def purge_task_results(self) -> bool:
        count = 0

        for keybatch in self.batcher(
            self.redis_backend.scan_iter(f"{self.name}_*"), 500
        ):
            cleaned_keybatch = [x for x in keybatch if x is not None]
            count += len(cleaned_keybatch)
            self.redis_backend.delete(*cleaned_keybatch)

        self.total_run_count = 0
        self.upsert_task()

        all_run_results = self.redis_backend.keys(f"runresult_{self.name}*")
        if len(all_run_results) != 0:
            self.redis_backend.unlink(*all_run_results)

        self.redis_backend.unlink(f"sortresults_{self.name}")

        entry = self.redis_broker.hgetall("redbeat:{}".format(self.name))

        new_entry = json.loads(entry[b"meta"])

        new_entry["total_run_count"] = 0

        entry[b"meta"] = json.dumps(new_entry).encode()

        self.redis_broker.hset("redbeat:{}".format(self.name), mapping=entry)

        self.logger.info(
            f"Purged {self.name} database entries, deleting: {count} records"
        )

        return True

    def upsert_task(self) -> bool:
        """
        Method to create or update a scheduled interval task
        """
        entry = CveXploreEntry(
            name=self.name,
            task=self.task,
            schedule=self.run,
            args=self.args,
            kwargs=self.kwargs,
            enabled=self.enabled,
            app=app,
            redis_broker=self.redis_broker,
        )
        entry.save()

        return True

    def delete_task(self) -> bool:
        """
        method to delete a task from the database
        """
        try:
            self.purge_task_results()
            self.redis_backend.delete(f"runresult_{self.name}")
            self.redis_broker.zrem("redbeat::schedule", "redbeat:{}".format(self.name))
            self.redis_broker.delete("redbeat:{}".format(self.name))

            return True
        except Exception:
            self.logger.exception("Failed to delete the task!!")
        return False

    def enable(self) -> bool:
        return self._toggle_task(1)

    def disable(self) -> bool:
        return self._toggle_task(0)

    def _toggle_task(self, value: int) -> bool:
        """
        method to enable (1) or disable (0) a task
        """

        if value == 0:
            set_value = False
        elif value == 1:
            set_value = True

        try:
            entry = self.redis_broker.hgetall("redbeat:{}".format(self.name))

            new_entry = json.loads(entry[b"definition"])

            new_entry["enabled"] = set_value
            self.enabled = set_value

            entry[b"definition"] = json.dumps(new_entry).encode()

            self.redis_broker.hset("redbeat:{}".format(self.name), mapping=entry)

            return True
        except Exception:
            self.logger.exception("Failed to toggle the task!!")
        return False

    def to_dict(self):
        my_dict = {
            k: v
            for (k, v) in self.__dict__.items()
            if not k.startswith("_")
            and k
            not in {
                "logger",
                "enable",
                "disable",
                "delete_task",
                "upsert_task",
                "config",
                "redis_broker",
                "redis_backend",
            }
        }

        if not self.crontab:
            my_dict["seconds"] = int(my_dict["run"].seconds)
            my_dict["run"] = my_dict["run"].human_seconds

        return my_dict

    def to_data(self):
        my_dict = {
            k: v
            for (k, v) in self.__dict__.items()
            if not k.startswith("_")
            and k
            not in {
                "logger",
                "enable",
                "disable",
                "delete_task",
                "upsert_task",
                "config",
                "redis_broker",
                "redis_backend",
            }
        }

        if not self.crontab:
            my_dict["seconds"] = int(my_dict["run"].seconds)
            my_dict["run"] = my_dict["run"].human_seconds

        if self.crontab:
            my_dict.pop("run")
            my_dict["minute"] = self.run._orig_minute
            my_dict["hour"] = self.run._orig_hour
            my_dict["dow"] = self.run._orig_day_of_week
            my_dict["dom"] = self.run._orig_day_of_month
            my_dict["moy"] = self.run._orig_month_of_year

        if len(self.args) != 0:
            args_str = ""
            for each in self.args:
                if isinstance(each, str):
                    args_str += f"{each}\n"
                elif isinstance(each, list):
                    args_str += ",".join(each) + "\n"
                elif isinstance(each, dict):
                    args_str += (
                        ",".join(
                            [
                                f"{':'.join(map(str,v))}"
                                for i, v in enumerate(list(each.items()))
                            ]
                        )
                        + "\n"
                    )
            my_dict["args"] = args_str

        if len(self.kwargs) != 0:
            kwargs_str = ""
            for the_key, the_val in self.kwargs.items():
                if isinstance(self.kwargs[the_key], str):
                    kwargs_str += f"{the_key}={the_val}\n"
                elif isinstance(self.kwargs[the_key], list):
                    kwargs_str += f"{the_key}={','.join(the_val)}\n"
                elif isinstance(self.kwargs[the_key], dict):
                    d = ",".join(
                        [
                            f"{':'.join(map(str, v))}"
                            for i, v in enumerate(list(the_val.items()))
                        ]
                    )
                    kwargs_str += f"{the_key}={d}\n"
            my_dict["kwargs"] = kwargs_str

        return my_dict

    def __repr__(self):
        return f"<< Task: {self.name} >>"


class TaskData(object):
    def __init__(self, entry_data: dict):
        self.entry_data = entry_data

        for k, v in self.entry_data[b"definition"].items():
            self.__setattr__(k, v)

        if hasattr(self, "schedule"):
            if self.schedule["__type__"] == "interval":
                self.run = schedule(
                    run_every=self.schedule["every"],
                    relative=self.schedule["relative"],
                )
            if self.schedule["__type__"] == "crontab":
                task_data = self.schedule
                task_data.pop("__type__")
                self.run = crontab(**task_data)

        if "total_run_count" in self.entry_data[b"meta"]:
            self.total_run_count = self.entry_data[b"meta"]["total_run_count"]
        else:
            self.total_run_count = 0

        self.last_run_at = datetime(
            year=self.entry_data[b"meta"]["last_run_at"]["year"],
            month=self.entry_data[b"meta"]["last_run_at"]["month"],
            day=self.entry_data[b"meta"]["last_run_at"]["day"],
            hour=self.entry_data[b"meta"]["last_run_at"]["hour"],
            minute=self.entry_data[b"meta"]["last_run_at"]["minute"],
            second=self.entry_data[b"meta"]["last_run_at"]["second"],
            microsecond=self.entry_data[b"meta"]["last_run_at"]["microsecond"],
            tzinfo=pytz.utc,
        )

    def to_dict(self):
        return {
            "name": self.name,
            "task": self.task,
            "run": self.run,
            "args": self.args,
            "kwargs": self.kwargs,
            "enabled": self.enabled,
            "last_run_at": self.last_run_at,
            "total_run_count": self.total_run_count,
        }

    def __repr__(self):
        return f"<< TaskData: {self.name} >>"


class TaskHandler(object):
    def __init__(self):
        self.config = Configuration

        parsed_url = urlparse(self.config.REDIS_URL)

        self.redis = Redis(
            host=parsed_url.hostname,
            port=parsed_url.port,
            db=int(self.config.CELERY_REDIS_BROKER_DB),
        )

        self.logger = logging.getLogger(__name__)

    def show_available_tasks(self) -> collections.OrderedDict:

        ordered_dict = collections.OrderedDict()

        sorted_tasks = sorted(task_descriptions.keys())

        for each in sorted_tasks:
            ordered_dict[each] = task_descriptions[each]

        return ordered_dict

    def create_task_by_number(
        self,
        task_number: int,
        task_slug: str,
        task_interval: int = None,
        task_crontab: dict = None,
    ):
        try:
            all_tasks = self.show_available_tasks()
            task_name = list(all_tasks.keys())[task_number - 1]

            return self.schedule_task(
                task_slug=task_slug,
                task_name=task_name,
                task_interval=task_interval,
                task_crontab=task_crontab,
            )
        except IndexError:
            raise TaskNotFoundError
        except Exception as err:
            self.logger.error(
                f"Uncaught exception while retrieving scheduled tasks: {err}"
            )
            raise

    def show_scheduled_tasks(self) -> list[Task]:
        try:
            tasks = self.redis.zrange("redbeat::schedule", 0, -1, withscores=True)

            ret_list = []

            for task_details in tasks:
                task, next_run = task_details

                entry = self.redis.hgetall(task)

                for each in entry:
                    entry[each] = json.loads(entry[each])

                task_data = TaskData(entry)

                ret_list.append(
                    Task(
                        **task_data.to_dict(),
                        next_run_at=timestampTOdatetime(int(next_run)),
                    )
                )

            ret_list = sorted(ret_list, key=lambda x: x.name.lower())

            return ret_list
        except RedisConnectionError as err:
            self.logger.error(f"Redis connection error; {err}")
            raise
        except Exception as err:
            self.logger.error(
                f"Uncaught exception while retrieving scheduled tasks: {err}"
            )
            raise

    def delete_scheduled_task(self, task_id: int) -> bool:
        try:
            all_tasks = self.show_scheduled_tasks()
            the_task = all_tasks[task_id - 1]
            return the_task.delete_task()
        except IndexError:
            raise TaskNotFoundError
        except Exception as err:
            self.logger.error(
                f"Uncaught exception while retrieving scheduled tasks: {err}"
            )
            raise

    def toggle_scheduled_task(self, task_id: int) -> bool:
        try:
            all_tasks = self.show_scheduled_tasks()
            the_task = all_tasks[task_id - 1]
            if the_task.enabled:
                return the_task.disable()
            else:
                return the_task.enable()
        except IndexError:
            raise TaskNotFoundError
        except Exception as err:
            self.logger.error(
                f"Uncaught exception while retrieving scheduled tasks: {err}"
            )
            raise

    def purge_scheduled_task(self, task_id: int) -> bool:
        try:
            all_tasks = self.show_scheduled_tasks()
            the_task = all_tasks[task_id - 1]
            return the_task.purge_task_results()
        except IndexError:
            raise TaskNotFoundError
        except Exception as err:
            self.logger.error(
                f"Uncaught exception while retrieving scheduled tasks: {err}"
            )
            raise

    def get_scheduled_tasks_results(self, task_id: int, limit: int = 10) -> list[dict]:
        try:
            all_tasks = self.show_scheduled_tasks()
            the_task = all_tasks[task_id - 1]
            task_results = the_task.get_sorted_task_results(limit=limit)
            return sorted(task_results, key=lambda x: x["inserted"], reverse=True)
        except IndexError:
            raise TaskNotFoundError
        except Exception as err:
            self.logger.error(
                f"Uncaught exception while retrieving scheduled tasks: {err}"
            )
            raise

    def get_scheduled_task_by_name(self, task_name: str) -> Task:
        """
        Method to retrieve the task parameters
        """
        try:
            task = [
                x
                for x in self.show_scheduled_tasks()
                if x.name == task_name
                or x.name.startswith(f"{TASK_START_STRING}{task_name}")
            ][0]

            return task
        except IndexError:
            raise TaskNotFoundError

    def schedule_task(
        self,
        task_slug: str,
        task_name: str,
        task_interval: int = None,
        task_crontab: dict = None,
        task_args: list = None,
        task_kwargs: dict = None,
        task_enabled: bool = True,
    ):
        if task_interval is not None:
            job_run = schedule(run_every=task_interval)
        elif task_crontab is not None:
            job_run = crontab(**task_crontab)
        else:
            raise ValueError("Either task_interval or task_crontab must be provided")

        try:
            my_task = Task(
                name=task_slug,
                task=task_name,
                run=job_run,
                args=task_args,
                kwargs=task_kwargs,
                enabled=task_enabled,
            )
            return my_task.upsert_task()
        except Exception as e:
            self.logger.error(f"Error creating task: {e}")
            raise

    def __repr__(self):
        return "<< TaskHandler >>"
