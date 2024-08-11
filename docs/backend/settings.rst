Settings
--------

The backend by default looks for an .env file in ``${HOME}/.cvexplore`` folder, if certain values need to be
overwritten you can do it either there or pass them directly as environment variables.

The following config variables are the configuration settings for the backend:

.. confval:: CELERY_REDIS_URL

   Url to be used by the backend for contacting redis.

.. confval:: CELERY_REDIS_BROKER_DB

   The redis database to use by the broker.

.. confval:: CELERY_REDIS_BACKEND_DB

   The redis database to use by the backend to store the results of the tasks in.

.. confval:: CELERY_TASK_FAILED_ERROR_CODE

   Code to set in the task result if a task fails.

.. confval:: CELERY_KEEP_TASK_RESULT

   The amount of days to keep the task results in the database.

.. confval:: CELERY_TASK_TIME_LIMIT

    The time limit that is set for a task as a limit

.. confval:: CELERY_RESULT_EXPIRES

    The amount of seconds that the results from the tasks (if `ignore_result=False` is set in the task decorator) will
    stay in the Redis database.
