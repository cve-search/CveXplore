.. image:: images/CveExplore_logo.png

.. Everything after the include marker below is inserted into the sphinx html docs. Everything above this comment is only visible in the github README.rst ##INCLUDE_MARKER##

.. image:: https://img.shields.io/github/release/cve-search/CveXplore.svg
   :target: https://GitHub.com/cve-search/CveXplore/releases/

.. image:: https://img.shields.io/badge/License-GPLv3-blue.svg
   :target: https://www.gnu.org/licenses/gpl-3.0

.. image:: https://badgen.net/badge/Github/repo/green?icon=github
   :target: https://GitHub.com/cve-search/CveXplore


The CveXplore package aims to provide an object related way to interact with the data collected or hosted by a
cve-search instance. It provides an ambiguous way to interact with either the cve-search mongodb or the cve-search API.

From version 0.2.5 onwards CveXplore has the possibility to initialize and update the database without the need of any of
the cve-search binaries and thus providing the same functionality as cve-search but without the GUI components.

A click command line functionality is being build but for now still in progress...

All the data provided by this interaction is converted into objects before being returned. And thus providing a way to
interact with objects rather then with raw data.

Dependencies
------------

As stated you will need to have one of two things; in order to fully use this package you need access to:

* MongoDB; either an empty or an already populated cve-search mongodb instance

OR

* A cve-search API instance (will be retired in the 0.4 release)

Both of them can be easily created on a physical machine or via a docker instance of cve-search;
please check `cve-search <https://github.com/cve-search/cve-search>`_ or
`CVE-Search-Docker <https://github.com/cve-search/CVE-Search-Docker>`_ for further details.

Installation
------------
Package is hosted on pypi, so to install the minimal core just run:

.. code-block:: bash

   pip install CveXplore

This command will install the core logic of CveXplore and, by default, installs the mongodb module also.

CveXplore is setup in a modular way and therefor has multiple modules which can be installed separately by specifying
them as an extra requirement. To install the mysql module only, specify:

.. code-block:: bash

   pip install CveXplore[mysql]

Or for multiple modules:

.. code-block:: bash

   pip install CveXplore[mysql, redis]

Or simple install all modules:

.. code-block:: bash

   pip install CveXplore[all]

Documentation
-------------

Check `github pages documentation <https://cve-search.github.io/CveXplore/>`_.

Most of the following configuration including the configuration directory path can be altered using
`settings <https://cve-search.github.io/CveXplore/general/settings.html>`_ from environment variables.

General
-------

Configuration
*************

CveXplore automatically creates a config folder in ``~/.cvexplore``. CveXplore stores several configuration
files in here such as the ``.env`` for general configuration and the ``.sources.ini`` for data sources configuration.

Logging
*******

CveXplore stores all logs in the ``~/.cvexplore/log`` folder:

* ``update_populate.log``; logging produced during database updates and database initialization.

Local Database populate / update
********************************

As of version 0.2.5 CveXplore can populate and update a local mongodb instance from either the command line:

.. code-block:: bash

    $ cvexplore database initialize
    $ cvexplore database update

Check the `CLI Documentation <https://cve-search.github.io/CveXplore/cli/cli.html>`_ for more information.

Or via the the CveXplore object:

.. code-block:: python

    >>> from CveXplore import CveXplore
    >>> cvx = CveXplore()
    >>> cvx.database.populate()
    >>> cvx.database.update()

You can add your `NIST API Key <https://nvd.nist.gov/developers/request-an-api-key>`_ in the environment variable
:code:`NVD_NIST_API_KEY` (e.g., in the :code:`~/.cvexplore/.env` file). You can populate CveXplore without an API key,
but it will limit the amount of parallel requests made to the NIST API.

For the NVD API, the update starts from the last modified document in the database. In case of missing CPEs or CVEs
caused by failures during the regular updates you can manually update entries for 1–120 days. (If the period is longer
than 120 days you would need to re-populate the entire database.) Example:

.. code-block:: python

    >>> cvx.database.update(manual_days=7)

Package usage
-------------

Instantiation
*************

CveXplore can be instantiated with different parameters, depending to which data source you're going to connect to.
If no parameters are given it is assumed that you're going to connect to a mongodb database running on localhost with
default port and security settings (Cve Search default parameters).

.. code-block:: python

    >>> from CveXplore import CveXplore
    >>> cvx = CveXplore()
    >>> cvx.version
    '0.1.2'

To let CveXplore connect to an mongodb with specific parameters:

.. code-block:: python

    >>> from CveXplore import CveXplore
    >>> cvx = CveXplore(datasource_type="mongodb", datasource_connection_details={"host": "mongodb://127.0.0.1:27017"})
    >>> cvx.version
    '0.1.2'

And to let CveXplore talk to an Cve Search API (only query POST endpoint needed):

.. code-block:: python

   >>> from CveXplore import CveXplore
   >>> cvx = CveXplore(datasource_type="api", datasource_connection_details={"address": ("mylocal.cve-search.int", 443), "api_path": "api"})
   >>> cvx.version
   '0.1.2'

For More options please check the package documentation

Command line usage
------------------

CveXplore has a 'Python Click' (`Documentation <https://click.palletsprojects.com/en/>`_) command line interpreter
available. Click provides an extensive help function to guide you through the different options; also check the full
documentation for examples and usage instructions

.. code-block:: bash

    $ cvexplore --help
    Usage: cvexplore [OPTIONS] COMMAND [ARGS]...

    Options:
      -v, --version  Show the current version and exit
      --help         Show this message and exit.

    Commands:
      capec     Query for capec specific data
      cpe       Query for cpe specific data
      cve       Query for cve specific data
      cwe       Query for cwe specific data
      database  Database update / populate commands
      find      Perform find queries on a single collection
      stats     Show datasource statistics
      tasks     Perform task related operations.
