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

From version 0.2.5 onwards CveXplore has the possibility to populate and update the database without the need of any of
the cve-search binaries and thus providing the same functionality as cve-search but without the GUI components.

A click command line functionality is being build but for now still in progress...

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

Local Database populate / update
********************************

As of version 0.2.5 CveXplore can populate and update a local mongodb instance from either the command line:

.. code-block:: bash

   # cvexplore database populate
   # cvexplore database update

Or via the the CveXplore object:

.. code-block:: python

   >>> from CveXplore import CveXplore
   >>> cvx = CveXplore()
   >>> cvx.database.populate()
   >>> cvx.database.update()

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

And to let CveXplore talk to an Cve Search API (only query POST endpoint needed):

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

Collection specific functions
*****************************
Some collections are equipped with specific functions; like the 'cves' collection has a function to query cve's based
on a given vendor:

.. code-block:: python

   >>> from CveXplore import CveXplore
   >>> cvx = CveXplore()
   >>> result = cvx.cves.get_cves_for_vendor("microsoft", limit=10)
   >>> result
   [<< Cves:CVE-2018-8540 >>,
   << Cves:CVE-2018-8476 >>,
   << Cves:CVE-2018-8154 >>,
   << Cves:CVE-2018-8500 >>,
   << Cves:CVE-2018-8626 >>,
   << Cves:CVE-2018-8421 >>,
   << Cves:CVE-2018-8327 >>,
   << Cves:CVE-2018-8302 >>,
   << Cves:CVE-2018-8273 >>,
   << Cves:CVE-2017-8658 >>]

When objects can be linked together, like for instance related capecs for a given cve, these are automatically queried
from the data source and inserted into the requested object, so building on the example above, requesting related
capecs from the CVE-2018-8540, could be done directly:

.. code-block:: python

   >>> result[0].capec
   [<< Capec:77 >>, << Capec:242 >>, << Capec:35 >>]

Or by iterating the generator function of the cves object:

.. code-block:: python

   >>> for each in result[0].iter_capec():
   ...     print(each)
   ...
   << Capec:77 >>
   << Capec:242 >>
   << Capec:35 >>

All returned objects can be serialized into a dictionary with the to_dict() function:

.. code-block:: python

   >>> result = cvx.capec.id.find("1")
   >>> result = list(result)[0]
   >>> pprint(result.to_dict())
   {'execution_flow': {'1': {'Description': '[Survey] The attacker surveys the '
                                         'target application, possibly as a '
                                         'valid and authenticated user',
                          'Phase': 'Explore',
                          'Techniques': ['Spidering web sites for all '
                                         'available links',
                                         'Brute force guessing of resource '
                                         'names',
                                         'Brute force guessing of user names / '
                                         'credentials',
                                         'Brute force guessing of function '
                                         'names / actions']},
                    '2': {'Description': '[Identify Functionality] At each '
                                         'step, the attacker notes the '
                                         'resource or functionality access '
                                         'mechanism invoked upon performing '
                                         'specific actions',
                          'Phase': 'Explore',
                          'Techniques': ['Use the web inventory of all forms '
                                         'and inputs and apply attack data to '
                                         'those inputs.',
                                         'Use a packet sniffer to capture and '
                                         'record network traffic',
                                         'Execute the software in a debugger '
                                         'and record API calls into the '
                                         'operating system or important '
                                         'libraries. This might occur in an '
                                         'environment other than a production '
                                         'environment, in order to find '
                                         'weaknesses that can be exploited in '
                                         'a production environment.']},
                    '3': {'Description': '[Iterate over access capabilities] '
                                         'Possibly as a valid user, the '
                                         'attacker then tries to access each '
                                         'of the noted access mechanisms '
                                         'directly in order to perform '
                                         'functions not constrained by the '
                                         'ACLs.',
                          'Phase': 'Experiment',
                          'Techniques': ['Fuzzing of API parameters (URL '
                                         'parameters, OS API parameters, '
                                         'protocol parameters)']}},
   'id': '1',
   'loa': 'High',
   'name': 'Accessing Functionality Not Properly Constrained by ACLs',
   'prerequisites': 'The application must be navigable in a manner that '
                  'associates elements (subsections) of the application with '
                  'ACLs. The various resources, or individual URLs, must be '
                  'somehow discoverable by the attacker The administrator must '
                  'have forgotten to associate an ACL or has associated an '
                  'inappropriately permissive ACL with a particular navigable '
                  'resource.',
   'related_capecs': ['122'],
   'related_weakness': ['1191',
                      '1193',
                      '1220',
                      '1224',
                      '1244',
                      '1252',
                      '1257',
                      '1262',
                      '1268',
                      '1283',
                      '276',
                      '285',
                      '434',
                      '693',
                      '721',
                      '732'],
   'solutions': 'In a more general setting, the administrator must mark every '
              'resource besides the ones supposed to be exposed to the user as '
              'accessible by a role impossible for the user to assume. The '
              'default security setting must be to deny access and then grant '
              'access only to those resources intended by business logic.',
   'summary': 'In applications, particularly web applications, access to '
            'functionality is mitigated by an authorization framework. This '
            'framework maps Access Control Lists (ACLs) to elements of the '
            "application's functionality; particularly URL's for web apps. In "
            'the case that the administrator failed to specify an ACL for a '
            'particular element, an attacker may be able to access it with '
            'impunity. An attacker with the ability to access functionality '
            'not properly constrained by ACLs can obtain sensitive information '
            'and possibly compromise the entire application. Such an attacker '
            'can access resources that must be available only to users at a '
            'higher privilege level, can access management sections of the '
            'application, or can run queries for data that they otherwise not '
            'supposed to.',
   'taxonomy': {'ATTACK': {'1574_010': {'Entry_ID': '1574.010',
                                      'Entry_Name': 'Hijack Execution Flow: '
                                                    'ServicesFile Permissions '
                                                    'Weakness',
                                      'URL': 'https://attack.mitre.org/techniques/T1574/010'}}},
   'typical_severity': 'High'}
