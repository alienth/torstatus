Installing TorStatus
====================
This document contains instructions on how to install TorStatus on a
minimal Debian Squeeze/6 installation. The procedure to build the
database and use TorStatus should be very similar for other Linux/Unix
distributions, but this has not yet been tested.

0: Installing the Dependencies
------------------------------
First, install the necessary software to run TorStatus.

    | $ sudo aptitude install python2.6 postgresql-8.4 python-matplotlib python-django python-psycopg2 git ant
    | $ python --version
    | Python 2.6.6
    | $ psql --version
    | psql (PostgreSQL) 8.4.8
    | $ ant -version
    | Apache Ant version 1.8.0 compiled on March 11 2010
    | $ python
    | >>> import matplotlib
    | >>> import django
    | >>> import psycopg2
    | >>> matplotlib.__version__
    | '0.99.3'
    | >>> django.VERSION
    | (1, 2, 3, 'final', 0)
    | >>> psycopg2.__version__
    | '2.2.1 (dt dec mx ext pq3)'

1: Installing the Database
--------------------------
This implementation of TorStatus currently uses features that are not
part of the master branch of metrics-web. Do the following to get the
correct branch of metrics-web:

    | $ mkdir /srv/metrics-web
    | $ cd /srv/metrics-web
    | $ git init
    | $ git remote add karsten git://git.torproject.org/karsten/metrics-web
    | $ git fetch karsten
    | $ git checkout -b foreignkey karsten/foreignkey

Before following the instructions in the README to build the database,
be aware that TorStatus maintains relay data from consensuses and
descriptors in its own schema that is not included in metrics-web.
So, before importing data into the new database, run the following:

    | $ psql -U metrics tordir
    | tordir=> \i /absolute/path/to/TorStatus/cache.sql

TorStatus does not regularly use "old" relays. To delete old relays
from the caching schema, add a crontab for the metrics:

    | $ crontab -e
    | 35 * * * * psql -U metrics tordir -c 'SELECT * FROM cache.purge();'

Now imported data will be added to the cache schema used with TorStatus.

Note that if you have not previously configured postgreSQL, you may
prefer to use a "password" verification system rather than a "trust"
verification system for the user "metrics" to access the database.
This is possible by adding a line to pg_hba.conf, found in
/etc/postgresql/8.4/main/ in Debian Squeeze, along the lines of
the following:

    | local     all     metrics     password

TorStatus requires, at the least, bandwidth history information,
relay statuses, descriptors, and the MaxMind Geoip database. Executing
the instructions found in sections 1.1, 1.2, 1.3, 1.5 and 1.6 should
enter all necessary data into the database to run TorStatus.

2: Installing TorStatus
-----------------------
If you have not done so already, get the most recent version of
TorStatus:

    | $ git clone https://github.com/dcalderon/TorStatus

Now change directory to TorStatus/status and edit config.template such
that TorStatus can connect to the database just built. Save these changes
to a file called "settings.py". Note that if you are not using password
verification for the "metrics" user in postgres, you may leave the
'password' field blank.

While still in TorStatus/status, run the following to synchronize
TorStatus with the database:

    | $ python manage.py syncdb

And run the following to initiate TorStatus, where [port] is the port
that you would like TorStatus to run on:

    | $ python manage.py runserver [port]

At this point, TorStatus should be running; navigate to localhost:[port]
in your web browser to view it.

If there are any changes that you would like to see in TorStatus, please
let us know by sending e-mail to torstatus@gmail.com.

3: Running Apache and Deployment
________________________________
.. Just started this section still needs lots of work

First install Apache and mod_wsgi...
> sudo apt-get install apache2 libapache2-mod-wsgi

You might want to make a folder to store your sites
> sudo mkdir /srv/www

If you want to set up a test server create a hosts file
> sudo nano /etc/hosts

Get the appropriate packages. With a minimal debian sqeeze platform
you should have the necessary packages already.

You should get apache2-mpm-worker
apache2-utils
apache2.2-bin
apache2.2-common

Two packages are most popular for embedding python into the Apache server:
libapache2-mod-python
*recommend mod_wsgi*

documentation for mod_wsgi is located at: code.google.com/p/modwsgi/wiki
documentation for mod_python
