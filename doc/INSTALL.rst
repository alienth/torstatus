Installing TorStatus
====================
This document contains instructions on how to install TorStatus on a
minimal Debian Squeeze/6 installation. The procedure to build the
database and use TorStatus should be very similar for other Linux/Unix
distributions, but this has not yet been tested.

0: Installing the Dependencies
------------------------------
First, install the necessary software to run TorStatus:

    | ``$ sudo aptitude install python2.6 postgresql-8.4 python-matplotlib python-django python-psycopg2 git ant``
    | ``$ python --version``
    | ``Python 2.6.6``
    | ``$ psql --version``
    | ``psql (PostgreSQL) 8.4.8``
    | ``$ ant -version``
    | ``Apache Ant version 1.8.0 compiled on March 11 2010``
    | ``$ python``
    | ``>>> import matplotlib``
    | ``>>> import django``
    | ``>>> import psycopg2``
    | ``>>> matplotlib.__version__``
    | ``'0.99.3'``
    | ``>>> django.VERSION``
    | ``(1, 2, 3, 'final', 0)``
    | ``>>> psycopg2.__version__``
    | ``'2.2.1 (dt dec mx ext pq3)'``

Note: some installations of Django have issues importing modules that
are necessary for running Django itself. If you are bitten by this bug,
try running the following:

    | ``$ update-python-modules -f``

For more about this bug, see
http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=632217.

1: Installing the Database
--------------------------
This implementation of TorStatus currently uses features that are not
part of the ``master`` branch of ``metrics-web``. Do the following to
get the correct branch of ``metrics-web``:

    | ``$ mkdir /srv/metrics-web``
    | ``$ cd /srv/metrics-web``
    | ``$ git init``
    | ``$ git remote add karsten git://git.torproject.org/karsten/metrics-web``
    | ``$ git fetch karsten``
    | ``$ git checkout -b foreignkey karsten/foreignkey``

Before following the instructions in the ``README`` to build the
database, be aware that TorStatus maintains relay data from consensuses
and descriptors in its own schema that is not included in
``metrics-web``. So, before importing data into the new database, run
the following:

    | ``$ psql -U metrics tordir``
    | ``tordir=> \i /absolute/path/to/TorStatus/cache.sql``

TorStatus does not regularly use "old" relays. To delete old relays
from the caching schema, add a crontab for the metrics user that looks
something like the following:

    | ``35 * * * * psql -U metrics tordir -c 'SELECT * FROM cache.purge();'``

At this point, imported data will be added to the ``cache`` schema used
with TorStatus.

Note that if you have not previously configured postgreSQL, you may
prefer to use a "password" verification system rather than a "trust"
verification system for the user "metrics" to access the database.
This is possible by adding a line to ``pg_hba.conf``, found in
``/etc/postgresql/8.4/main/`` in Debian Squeeze, along the lines of
the following:

    | ``local     all     metrics     password``

TorStatus requires, at the least, bandwidth history information,
relay statuses, descriptors, and the MaxMind Geoip database. Executing
the instructions found in sections 1.1, 1.2, 1.3, 1.5 and 1.6 should
enter all necessary data into the database to run TorStatus.

2: Installing TorStatus
-----------------------
If you have not done so already, get the most recent version of
TorStatus:

    | ``$ git clone https://github.com/dcalderon/TorStatus``

Now change directory to ``TorStatus/status`` and edit
``config.template`` such that TorStatus can connect to the database
just built. Save these changes to a file called ``settings.py``. Note
that if you are not using password verification for the ``metrics``
user in postgres, you may leave the 'password' field blank.


Run the following to initiate TorStatus, where ``[port]`` is the
port that you would like TorStatus to run on:

    | ``$ python manage.py runserver [port]``

At this point, TorStatus should be running; navigate to
``localhost:[port]`` in your web browser to view it.

3: Installing Apache and mod_wsgi
---------------------------------

Two packages are most popular for embedding python into the Apache
server: ``libapache2-mod-python`` and ``libapache2-mod-wsgi``. We've
found the documentation on mod-wsgi extensive and the community
helpful, so we recommend mod_wsgi. If you encounter any problems
while installing mod_wsgi, additional documentation can be found at
http://code.google.com/p/modwsgi/wiki.

First, install Apache and mod_wsgi. Note that apache2 may already
be installed:

    | ``# aptitude install apache2 libapache2-mod-wsgi``

You might want to make a folder to store your sites. In this example,
we'll make this folder ``/srv/www/``, but there are many other
reasonable choices.

    | ``# mkdir /srv/www/``

We'll also create a ``torstatus`` folder to store the site pages:

    | ``# mkdir /srv/www/torstatus/``

Now we'll want to move our ``TorStatus`` project folder to the new
location:

    | ``# mv /path/to/TorStatus/* /srv/www/torstatus/``

The basic file structure is taken care of at this point, but we still
need to configure Apache and mod_wsgi. We'll create a ``.wsgi`` file
for Apache and mod_wsgi in ``/srv/www/torstatus/status/apache/``.

First, create a directory in ``torstatus/status/`` called ``apache``:

    | ``# mkdir /srv/www/torstatus/status/apache/``

Now, create a file called
``/srv/www/torstatus/status/apache/django.wsgi`` that contains the
following lines::

  import os, sys
  sys.path.append('/usr/local/www/torstatus')
  sys.path.append('/usr/local/www/torstatus/status')

  os.environ['DJANGO_SETTINGS_MODULE'] = 'status.settings'

  import django.core.handlers.wsgi

  application = django.core.handlers.wsgi.WSGIHandler()

Once this is done, change directory to your apache directory entitled
``sites-available``, this should be located at
``/etc/apache2/sites-available``:

    | ``# cd /etc/apache2/sites-available/``

In this directory, make a file, here called
``/etc/apache2/sites-available/tor-status``, that contains the
following code (but be sure to replace www.example.com,
example.com, and foo@bar.com)::

  <VirtualHost *:80>
      ServerName www.example.com
      ServerAlias example.com
      ServerAdmin foo@bar.com

      <Directory /srv/www/torstatus/status/>
          Order allow,deny
          Allow from all
      </Directory>

      WSGIScriptAlias / /srv/www/torstatus/status/apache/django.wsgi

      <Directory /srv/www/torstatus/status/apache>
          Order allow,deny
          Allow from all
      </Directory>

  </VirtualHost>

The WSGIScriptAlias first argument is where the site is hosted, so
the site will be hosted at http://localhost/example. The second
argument is the path to the django.wsgi file.

First we need to disable the default apache site:

    | ``# a2dissite default``

Now we need to let apache know that the site is active:

    | ``# a2ensite tor-status``

This creates a link in the ``sites-enabled`` folder.

Now if you reload apache using the script

    | ``# /etc/init.d/apache2 reload``

Now the site should be up and running at http://localhost/.

3.1: Troubleshooting Apache
~~~~~~~~~~~~~~~~~~~~~~~~~~~
There's much more to apache, and there is much that can go wrong. If
you've never worked with Apache before, here are some things that we
found helpful:

Find and monitor the log files of apache in case of problems.

Be careful with ``import`` statements, particularly when moving
directories.

Finally and most importantly if you are new to apache spend some time
learning how to best configure your copy to provide an adequete
level of security.
