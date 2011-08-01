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

3: Installing Apache
________________________________

Two packages are most popular for embedding python into the Apache server:
libapache2-mod-python
and libapache2-mod-wsgi

We've found the documentation on mod-wsgi extensive and the community helpful.
Apparently it is also faster and simpler to set up, so we recommend
*mod_wsgi*

Documentation for mod_wsgi is located at: code.google.com/p/modwsgi/wiki

Here is a basic recipe for setting up a django powered site with mod_wsgi
on apache:

First install Apache and mod_wsgi...
    | $ sudo apt-get install apache2 libapache2-mod-wsgi

apache2 is probably already installed

For this example we'll make a directory to store the site pages
    | $ sudo mkdir /usr/local/www/EXAMPLE

You want to move your files to the EXAMPLE Directory. It should be
the directory in which you ran the django-admin startproject command.

Let's say your project is called "project". So in your project directory
you want to make a directory entitled "apache" and in that directory
create a file called "django.wsgi".

    | $ sudo mkdir /usr/local/www/EXAMPLE/project/apache
    | $ sudo vim /usr/local/www/EXAMPLE/project/apache/django.wsgi

In this document type the following code:

import os, sys
sys.path.append('/usr/local/www/EXAMPLE')

os.environ['DJANGO_SETTINGS_MODULE'] = 'project.settings'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()


Once this is done go to your apache directory entitled
"sites-available", this should be located at
/etc/apache2/sites-available.

Make a file to put the virtual host.
    | $ cd /etc/apache2/sites-available
    | $ sudo vim example

In this file put the following code:

<VirtualHost *:80>
    ServerName www.example.com
    ServerAlias example.com
    ServerAdmin webmaster@example.com

    <Directory /usr/local/www/EXAMPLE/project/>
        Order allow,deny
        Allow from all
    </Directory>

    WSGIScriptAlias /example /usr/local/www/EXAMPLE/project/apache/django.wsgi

    <Directory /usr/local/www/EXAMPLE/project/apache>
        Order allow,deny
        Allow from all
    </Directory>

</VirtualHost>


***
The WSGIScriptAlias first argument is where you have the site so for example
now it would be at http://localhost/example. The second argument is
the path to the django.wsgi file.

Now you need to let apache know that the site is active.

So from the command line input

    | $ sudo a2ensite example

This creates a link in the sites-enabled folder of apache.

Now if you reload apache using the script

    | $ sudo /etc/init.d/apache2 reload

the site should be up and running at http://localhost/example


EXTRA NOTES on apache:

Apache is quite the beast to set up and this is not a tell all guide.
Searching the internet for debugging help would be your best bet.
Although some helpful tips:

Find and monitor the log files of apache (they can be a life saver)

Sometimes when you move files around for sites the import statements
might not work any more. Be careful with those.

If you are new with apache you might want to practice on something
smaller before setting up a full fledged django site.



