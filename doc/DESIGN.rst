TorStatus Design Documentation
==============================

1: Software
-----------
This implementation of TorStatus was developed using Django 1.2.3,
Python 2.6.6, psycopg 2.2.1-1, matplotlib 0.99.3-1, and a postgreSQL
Tor Metrics database. While it is possible that TorStatus will run on
newer versions of this software, we cannot guarantee that TorStatus
will function properly.

2: Django
---------
TorStatus is written in django to take advantage of Django's easy
to understand Model-View-Controller architecture (MVC). The model
level represeants the database or the source of information, the
controller level contains most of the back-end logic, and the view level
generates the html/css response that is sent back to the client. Also
we took advantage of Django's built in object-relational mapper (ORM)
for straight-forward database access. In Django, a database table
is analogous to a class, rows are analogous to objects of that
class, and columns are analogous to the fields of that class. Data
can be directly accessed by way of Django's models, each of which
maps to a table in the database and can be utilized as an object.

3: Directory Structure
----------------------
Views are stored in ``status/statusapp/views``. Views are organized by
their functions: views that render a text/html object to response
are stored in ``pages.py``, views that render ``.png`` images to
response are stored in ``graphs.py``, and functions that do not return
an ``HttpResponse`` object are stored elsewhere as helper functions.

4: Modules in statusapp
-----------------------

4.1: ``__init__.py``
....................
Contains a custom type cast for ``BIGINT[]`` arrays. This is placed in
__init__.py because it is necessary that the custom type cast is
run on startup. For more on why this type cast is necessary, consult
__init__.py itself.

4.2: ``models.py``
..................
Contains the classes that corresponds to each table in the
Tor Metrics database, where an object is analogous to a row in the
table and a field is analogous to a column in the table.

4.3: ``tests.py``
.................
Contains basic doctests where needed, mostly for helper functions and
custom filters.

4.4: ``urls.py``
................
Contains the ``URLCONF`` for TorStatus pages. Most of urls.py consists
of tuples with two entries: the first uses regular expressions to match
page requests, and the second specifies what method in views.py will be
called to serve the page request.

4.5: ``views/``
...............
Contains the application logic used to serve each page request. Each
"view" returns an HttpResponse object that refers to an HTML template
that presents the information to the client.

4.5.1: ``csvs.py``
~~~~~~~~~~~~~~~~~~
Contains the views for generating comma-separated values files from
the relay result set currently displayed.

4.5.2: ``pages.py``
~~~~~~~~~~~~~~~~~~~
Contains the views for "pages" of the TorStatus web application.

4.5.3: ``graphs.py``
~~~~~~~~~~~~~~~~~~~~
Contains the views for the graphs of the TorStatus web application.

4.5.4: ``helpers.py``
~~~~~~~~~~~~~~~~~~~~~
Contains helper functions for ``pages.py`` and ``graphs.py``.

4.5.5: ``display_helpers.py``
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Contains helper functions for the "Display Options" page.

5: Design Decisions
-------------------

5.1: Page Sizes
...............
TorStatus is likely to be viewed by a larger-than-usual number of
clients of the Tor network. When torified, data transfer is bounded
by the connection speed of the slowest relay in a Tor relay circuit.
Additionally, many common tools such as cookies or javascript can pose
more security problems than usual.

The current design displays only 50 relays per page by default, with
options to go on to the first page, previous page, next page, or last
page. This reduces page sizes which in turn reduces loading times.

Additionally, we anticipate that many users of TorStatus only want
to view information about one specific relay in the Tor network.
Because of this, we've aimed to make the landing page for TorStatus
as small as is reasonable and to implement a simple search feature
capable of looking up relays by nickname, IP address, or fingerprint.

Thanks to gzip compression, many page sizes are smaller than the page
sizes of the old implementation. However many images (including flags,
but especially the image in the header) are far too large to expect
torified clients to download happily (in my opinion).

Currently, the average country flag is about 1KB, and there are about
80 unique country flags displayed for every index page of ALL routers
in the most recent consensus. This seems like a good place to shrink
page sizes. Note that many flags have a shaded, glossy feature to them,
which may come at the cost of larger file sizes.

5.2: Security
.............
Javascript is not used in this implementation. Instead,
secure sessions are used to store display options and search filters
on a per-user basis. Data is encrypted and stored on the server side,
and the sending and receiving of cookies is abstracted. These sessions
use only a hashed session ID rather than the data itself, so only a
hashed session ID is stored by the client.

For more on Django and sessions, see:
http://www.djangobook.com/en/2.0/chapter14/

5.3: Databases
..............
This implementation of TorStatus was designed to be integrated with the
Tor Metrics database. In this database, relay data is spread across
multiple tables, and for good reason. However, this makes displaying
dynamically-generated relay data somewhat difficult. Additionally,
clients of TorStatus may have a desire to view information about a
relay that clients of Tor Metrics rarely have interest in.

Our solution to this problem was to maintain a small schema in the
Tor Metrics database designed solely for the purpose of holding
information about active relays in the Tor network. This means that
the raw descriptor of any relay will only need to be parsed once for
information that is requested less than frequently.

This schema works by holding descriptors that were published in the
last 36 hours and by holding statusentries that were published in the
last 4 hours and keeping one table, ``active_relay``, that is
essentially a table that is the result of a ``LEFT JOIN`` between the
statusentry table and the descriptor table on the most recent
information for each relay, though without any descriptor information
or relay information older than a given interval of time (in this case,
36 hours and 4 hours, respectively).

6: Issues
---------

6.1: Documentation
..................
We love Tor and Tor Metrics, but we're not sure much of our
documentation in ``status/statusapp/models.py`` is accurate. Somebody
more familiar with Tor Metrics should check our documentation for
anything that is misleading or simply wrong.

6.2: Templates
..............
Template languages are slow. Django's template language is particularly
slow. In the past, a few clients of TorStatus have communicated desires
to view all of the active relays in the Tor network on one page, but it
currently takes far too long for the server to render such a template
to an Http Response object. Because of this, we have capped the maximum
number of relays viewable at a time at 200. This upper bound should be
modified or removed as improvements are made.

Fortunately, there are many options available. Thanks to Django's
"loose-coupling" philosophy, it is relatively easy to swap template
languages. So far, we have only experimented with Jinja2 -- a template
language with syntax that is very similar to Django's -- in tandem with
Coffin. Coffin makes the switch from Django's template language
to Jinja2's template language relatively painless, though there are a
few key differences. Preliminary tests showed pages rendering were
faster using the Jinja2 template language; if you'd like to test
this for yourself, checkout the branch called ``redesign_jinja_coffin``.
Other template languages for python pride themselves on being the
fastest template languages around, such as Cheetah and Tenjin.
However, neither of these template languages are very syntactically
similar to the Django template language.

There seem to be many ways to decreasing the load on the template,
but it seems like all of them involve writing HTML into python code
at some level. Ultimately, this might have to be done, but
we'd rather defer this decision to the future project maintainer,
as with the decision of which template language to ultimately use.

Aside from the template language itself, our team has experienced
difficulties generating the list of routers in an efficient way.
It seems to us that it is a waste of processing time to figure out
how to display the data for every relay with respect to the column
display preferences specified by the user -- this information does not
change from relay to relay. It seems that some sort of sub-template
should be generated only once with respect to the value of
"current_columns", and that this sub-template should be filled out for
each relay. We're not sure that django offers support for such a
mechanism.
