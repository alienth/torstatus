TorStatus README
================
.. Updated 2011-06-28 11:00:00 GMT-5
.. This file is written in reStructuredText.

Installation
------------
For help installing and running TorStatus, consult doc/INSTALL.

Generating the API
------------------
To generate the TorStatus API, install epydoc (available at
http://epydoc.sourceforge.net/installing.html) and run:

    $ epydoc . --config config/epydoc_config.py

Design Documentation
--------------------
Design documentation, like this README, is written in reStructuredText.
To generate HTML-formatted design documentation using reStructuredText,
install docutils (available at http://docutils.sourceforge.net/)
and run the following:

    | $ cd doc/
    | $ rst2html design.txt design.html

To view the documentation, open design.html using your favorite web
browser. If you'd rather view the plaintext documentation, open
design.txt