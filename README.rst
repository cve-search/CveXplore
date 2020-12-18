.. image:: images/CveExplore_logo.png

.. Everything after the include marker below is inserted into the sphinx html docs. Everything above this comment is
   only visible in the github README.rst
   ##INCLUDE_MARKER##

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

Usage
-----

