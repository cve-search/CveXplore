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

Documentation
-------------
Check `github pages documentation <https://cve-search.github.io/CveXplore/>`_

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

Query for data
**************
CveXplore supports multiple methods to query for data.

The queries are limited to the following collections:

* capec;
* cpe;
* cwe;
* via4;
* cves;

Free format query
*****************
Besides this restriction the queries can be free format on given parameters (returning a direct object or a
list of objects); to get a 'capec' with the id of 1 you could use:

.. code-block:: python

   >>> from CveXplore import CveXplore
   >>> cvx = CveXplore()
   >>> result = cvx.get_single_store_entry("capec", {"id": "1"})
   >>> result
   << Capec:1 >>

The above example is perfect when you would expect a single result from your query; if a query to a single collection
could yield multiple results you better use:

.. code-block:: python

   >>> from CveXplore import CveXplore
   >>> cvx = CveXplore()
   >>> result = cvx.get_single_store_entries(("cves", {"cvss": {"$eq": 8}}))
   >>> result
   [<< Cves:CVE-2011-0387 >>,
   << Cves:CVE-2015-1935 >>,
   << Cves:CVE-2014-3053 >>,
   << Cves:CVE-2010-4031 >>,
   << Cves:CVE-2016-1338 >>,
   << Cves:CVE-2013-3633 >>,
   << Cves:CVE-2017-14444 >>,
   << Cves:CVE-2017-14446 >>,
   << Cves:CVE-2017-14445 >>,
   << Cves:CVE-2016-2354 >>]

This type of query has a default limit of 10; which can be altered to a higher number if needed or disabled by setting
the limit to 0:

.. code-block:: python

   >>> from CveXplore import CveXplore
   >>> cvx = CveXplore()
   >>> result = cvx.get_single_store_entries(("cves", {"cvss": {"$eq": 8}}), limit=0)
   >>> len(result)
   32

If you need to query multiple collections at once you could use:

.. code-block:: python

   >>> from CveXplore import CveXplore
   >>> cvx = CveXplore()
   >>> result = cvx.get_multi_store_entries([("CWE", {"id": "78"}), ("cves", {"id": "CVE-2009-0018"})])
   >>> result
   [<< Cwe:78 >>, << Cves:CVE-2009-0018 >>]

Collection specific query
*************************
By using the collection specific attributes you can drill down to a specific field to query (returning an iterator to
iterate over the requested results):

.. code-block:: python

   >>> from CveXplore import CveXplore
   >>> cvx = CveXplore()
   >>> result = cvx.capec.id.find("1")
   >>> for each in result:
   ...     print(each)
   ...
   << Capec:1 >>

If you would limit (or sort / skip) the returned results you could append additional commands to your original query:

.. code-block:: python

   >>> from CveXplore import CveXplore
   >>> cvx = CveXplore()
   >>> result = cvx.cves.cvss.find(8)
   >>> len(list(result))
   32

   >>> result = cvx.cves.cvss.find(8).limit(10)
   >>> len(list(result))
   10

If you would like to sort the results:

.. code-block:: python

   >>> from CveXplore import CveXplore
   >>> cvx = CveXplore()
   >>> result = cvx.cves.cvss.find(8).limit(10).sort("id", pymongo.DESCENDING)
   >>> list(result)
   [<< Cves:CVE-2020-5735 >>,
   << Cves:CVE-2020-13122 >>,
   << Cves:CVE-2018-2926 >>,
   << Cves:CVE-2018-17022 >>,
   << Cves:CVE-2017-3807 >>,
   << Cves:CVE-2017-17223 >>,
   << Cves:CVE-2017-16347 >>,
   << Cves:CVE-2017-16346 >>,
   << Cves:CVE-2017-16345 >>,
   << Cves:CVE-2017-16344 >>]
