General
-------

The backend as referred to in this documentation consists of a celery daemon with a redis broker.
This will give CveXplore the possibility to easily create and maintain background tasks for for instance database
maintenance and re-processing of updated database entries.

The use of this backend is **optional** and CveXplore can function perfectly without one; the tasks it performs can well
be handled by another mechanism. It is, however, a nice addition to the functionalities CveXplore offers.

Task handling (CRUD actions en status updates) are handled via a separate class and can be controlled via package or
CLI commands.
