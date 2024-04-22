Settings
--------

The backend by default looks for an .env file in ``${HOME}/.cvexplore`` folder, if certain values need to be
overwritten you can do it there.

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
