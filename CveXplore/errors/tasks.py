class TaskError(Exception):
    pass


class TaskNotFoundError(TaskError):
    pass


class MissingTaskParameters(TaskError):
    pass
