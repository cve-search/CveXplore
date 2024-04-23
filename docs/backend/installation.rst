Installation
------------

The backend assumes that the CveXplore package is installed **first**; check the package :ref:`installation <index:installation>`
paragraph. Furthermore it assumes that **only** the package is installed and the complete code base is not on the
system.

Docker
######

Please ensure that you have docker and docker-compose installed before processing with the rest of this paragraph.

.. warning::

   The steps below (creating docker containers from package) are only available for versions >= 0.3.31

Retrieve the files which are present in the ``CveXplore/backend/docker/from_package`` folder; and save them to your home
folder. Navigate into the ``CveXplore/backend/docker/from_package`` folder. Run the following command:

.. code-block:: bash

    $ docker-compose build
    $ cp CveXplore/backend/docker/docker-compose_example.yml ~/.cvexplore/docker-compose.yml
    $ cp CveXplore/backend/docker/cvexplore-backend.service /etc/systemd/system/cvexplore-backend.service
    $ sudo systemctl daemon-reload
    $ sudo systemctl start cvexplore-backend.service

If you want to auto-start the cvexplore-backend.service upon reboot; then run:

.. code-block:: bash

    $ sudo systemctl enable cvexplore-backend.service

If all went well; you can look at the :ref:`cli <cli/cli:tasks>` *or* package section of this documentation for the commands to check the
tasks backend.

Systemd
#######

The backend tasks are powered by celery; please follow
`these instructions <https://docs.celeryq.dev/en/stable/userguide/daemonizing.html#usage-systemd>`_ if you prefer
to use systemd instead of a docker deployment

There are a few points to make notice of:

- The celery.service command should consist of the following variables:

  1. ``$CELERY_BIN`` = Depending on your environment; e.g. '/home/basicuser/.local/bin/celery'
  2. ``$CELERY_APP`` = CveXplore.celery_app.cvexplore_daemon
  3. ``$CELERYD_OPTS`` = -O fair --without-heartbeat --without-gossip --without-mingle

All other variables are to be set as you wish, it is however advised to run at least 2 worker nodes;
so ``$CELERYD_NODES`` should be at least 2 nodes long; e.g.:"worker1 worker2"

- The celerybeat.service command should consist of the following variables:

  1. ``$CELERY_BIN`` = Depending on your environment
  2. ``$CELERY_APP`` = CveXplore.celery_app.cvexplore_daemon
  3. The ``ExecStart`` should be appended (after the word ``beat``) with ``-S redbeat.RedBeatScheduler`` to make use of the dynamic taskadjustments functionalities
