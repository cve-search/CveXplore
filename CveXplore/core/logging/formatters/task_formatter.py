import logging


class TaskFormatter(logging.Formatter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            from celery._state import get_current_task

            self.get_current_task = get_current_task  # pragma: no cover
        except ImportError:
            self.get_current_task = lambda: None

    def format(self, record):
        task = self.get_current_task()
        if task and task.request:  # pragma: no cover
            record.__dict__.update(
                task_id=task.request.id,
                task_name=task.name,
                task_args=task.request.args,
                task_kwargs=task.request.kwargs,
            )
            if "task_execution_time" in task.request.__dict__:
                record.__dict__.update(
                    task_execution_time=task.request.task_execution_time
                )
            else:
                record.__dict__.setdefault("task_execution_time", 0)
        else:
            record.__dict__.setdefault("task_name", "")
            record.__dict__.setdefault("task_id", "")
            record.__dict__.setdefault("task_args", [])
            record.__dict__.setdefault("task_kwargs", {})
            record.__dict__.setdefault("task_execution_time", 0)
        return super().format(record)
