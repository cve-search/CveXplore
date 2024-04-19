Installation
------------

The backend assumes that the CveXplore package is installed **first**; check the package :ref:`installation <index:installation>`
paragraph.

Docker
######

Please ensure that you have docker and docker-compose installed before processing with the rest of this paragraph.



Systemd
#######

The backend tasks are powered by celery; please follow
`these instructions <https://docs.celeryq.dev/en/stable/userguide/daemonizing.html#usage-systemd>`_ if you prefer
to use systemd instead of a docker deployment
