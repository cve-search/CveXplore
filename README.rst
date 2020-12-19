.. image:: images/CveExplore_logo.png

.. Everything after the include marker below is inserted into the sphinx html docs. Everything above this comment is
   only visible in the github README.rst
   ##INCLUDE_MARKER##

.. image:: https://img.shields.io/github/release/cve-search/CveXplore.svg
   :target: https://GitHub.com/cve-search/CveXplore/releases/

.. image:: https://img.shields.io/badge/License-GPLv3-blue.svg
   :target: https://www.gnu.org/licenses/gpl-3.0

.. image:: https://badgen.net/badge/Github/repo/green?icon=github
   :target: https://GitHub.com/cve-search/CveXplore


The CveXplore package aims to provide an object related way to interact with the data collected or hosted by a
cve-search instance. It provides an ambiguous way to interact either to the cve-search mongodb or to the cve-search API.
All the data provided by this interaction is converted into objects before being returned. And thus providing a way to
interact with objects rather then with raw data.

Dependencies
------------
As stated you will need to have one of two things; in order to fully use this package you need access to:

* A cve-search mongodb instance

OR

* A cve-search API instance

Both of them can be easily created on a physical machine or via a docker instance of cve-search;
please check `cve-search <https://github.com/cve-search/cve-search>`_ or
`CVE-Search-Docker <https://github.com/cve-search/CVE-Search-Docker>`_ for further details.

Installation
------------
Package is hosted on pypi, so just run:

.. code-block:: bash

   pip install CveXplorer

Usage
-----

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
   >>> cvx = CveXplore(mongodb_connection_details={"host": "192.168.1.1", "port": 27017})
   >>> cvx.version
   '0.1.2'

And to let CveXplore talk to an Cve Search API:

.. code-block:: python

   >>> from CveXplore import CveXplore
   >>> cvx = CveXplore(api_connection_details={"address": ("mylocal.cve-search.int", 443), "api_path": "api"})
   >>> cvx.version
   '0.1.2'
