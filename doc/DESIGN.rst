TorStatus Design Documentation
==============================
.. This file is written in reStructuredText.

Software
--------
This implementation of TorStatus was developed using Django 1.2.3,
Python 2.6.6, psycopg 2.2.1-1, matplotlib 0.99.3-1, and a postgreSQL Tor
Metrics database. While it is possible that TorStatus will run on newer
versions of this software, we cannot guarantee that TorStatus will
function properly.

Django
------
TorStatus is written in django to take advantage of Django's
object-relational mapper (ORM) for straight-forward database access.
In Django, a database table is analogous to a class, rows are
analogous to objects of that class, and columns are analogous to the
fields of that class. Data can be directly accessed by way of Django's
models, each of which maps to a table in the database and can be
utilized as an object. Django's adaptation of the model-view-controller
schema is a bit confusing: controllers are stored in a module named
views.py and views are called templates (but models are still,
thankfully, called models).

Directory Structure
-------------------
While the directory structure in commit 237303b...00cc7ed seems to be
the most djangonic file structure that we've used yet, the directory
structure is not yet settled.

Modules in statusapp
--------------------
__init__.py
...........
Contains a custom type cast for BIGINT[] arrays. This is placed in
__init__.py because it is necessary that the custom type cast is
run on startup. For more on why this type cast is necessary, consult
__init__.py itself.

models.py
.........
Contains the classes that corresponds to each table in the
Tor Metrics database, where an object is analogous to a row in the
table and a field is analogous to a column in the table.

tests.py
........
Contains basic doctests where needed, mostly for helper functions and
custom filters.

urls.py
.......
Contains the URLCONF for TorStatus pages. Most of urls.py consists of
tuples with two entries: the first uses regular expressions to match
page requests, and the second specifies what method in views.py will be
called to serve the page request.

views
........
Contains the application logic used to serve each page request. Each
"view" returns an HttpResponse object that refers to an HTML template
that presents the information to the client.

pages.py
~~~~~~~~
Contains the "views" for "pages" of the TorStatus web application.

graphs.py
~~~~~~~~~
Contains the "views" for the graphs of the TorStatus web application.

helpers.py
~~~~~~~~~~
Contains helper functions for pages.py and graphs.py.
