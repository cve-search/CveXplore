Settings
--------

CveXplore by default looks for an .env file in ``${HOME}/.cvexplore`` folder. If certain values need to be
overwritten you can do it either there or pass them directly as environment variables.

The following config variables are the configuration settings for the database.

Common
******

.. confval:: DATASOURCE_TYPE

   *This actually defaults to* ``mongodb`` *but that breaks the documentation automation.*

   Available options: ``mongodb``, ``api``, ``mysql``.

.. confval:: DATASOURCE_PROTOCOL

   *This actually defaults to* ``mongodb`` *but that breaks the documentation automation.*

   Used to build the URL; e.g., ``mongodb``, ``https`` or `http``.

.. confval:: DATASOURCE_DBAPI

   *This actually defaults to* ``None`` *but that breaks the documentation automation.*

   DBAPI extension for the protocol. E.g. ``srv`` in ``mongodb+srv://`` or ``pymysql`` in  ``mysql+pymysql://``.

.. confval:: DATASOURCE_USER

   Username for the data source (database or API).

.. confval:: DATASOURCE_PASSWORD

   Password for the data source (database or API).

.. confval:: DATASOURCE_DBNAME

   Database name at the data source.

.. confval:: DATASOURCE_CONNECTION_DETAILS

   *Not configurable via environment variables.*
   
   By default automatically built from the settings that are appropriate for the selected ``DATASOURCE_TYPE``,
   but documented here as this **can be overwritten in the code** using CveXplore as a library,
   which **would cause many of these settings not to be honored**.

.. confval:: API_CONNECTION_DETAILS

   *Not configurable via environment variables.*

   **Deprecated** (replaced by ``DATASOURCE_CONNECTION_DETAILS``). Will be removed in the 0.4 release.

MongoDB
*******

.. confval:: MONGODB_HOST

   MongoDB hostname (without the protocal that should be defined with ``DATASOURCE_PROTOCOL`` & ``DATASOURCE_DBAPI``).
   
.. confval:: MONGODB_PORT

   MongoDB port number.

.. confval:: MONGODB_CONNECTION_DETAILS

   *Not configurable via environment variables.*

   **Deprecated** (replaced by ``DATASOURCE_CONNECTION_DETAILS``). Will be removed in the 0.4 release.

SQL
***

.. confval:: SQLALCHEMY_DATABASE_URI

   Built from other environment variables, but can be manually overwritten.

   Defaults to ``{DATASOURCE_PROTOCOL}[+{DATASOURCE_DBAPI}]://{DATASOURCE_USER}:{DATASOURCE_PASSWORD}@{DATASOURCE_HOST}:{DATASOURCE_PORT}/{DATASOURCE_DBNAME}``.

.. confval:: SQLALCHEMY_TRACK_MODIFICATIONS

   See https://docs.sqlalchemy.org/en/20/orm/session_events.html

.. confval:: SQLALCHEMY_ENGINE_OPTIONS

   See https://docs.sqlalchemy.org/en/20/core/engines.html
