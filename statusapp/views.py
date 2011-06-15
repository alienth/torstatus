from statusapp.models import Statusentry, Descriptor
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpRequest, Http404
#from django.views.decorators.cache import cache_page
import csv

# To do: get rid of javascript sorting: pass another argument
# to this view function and sort the table accordingly.
#@cache_page(60 * 15) # Cache is turned off for development,
                      # but it works.
def index(request):
    """
    Supply a dictionary to the index.html template consisting of keys
    equivalent to columns in the statusentry and descriptor tables in the
    database. Querying the database is done with raw SQL. This needs 
    to be fixed.
    """

    from django.db import connection
    import datetime
    import time # Processing time, in unix...

    start = datetime.datetime.now()
    tick = time.clock()

    # Search options should probably not be implemented this way in a 
    # raw SQL query for security reasons.
    #ordering = ""
    #restrictions = ""
    #adv_search = ""
    #if request.GET:
            
    cursor = connection.cursor()

    cursor.execute('SELECT MAX(validafter) FROM statusentry')

    validafter_range = (cursor.fetchone()[0] - datetime.timedelta(hours=24))

    # Problem: Query takes a LONG time (7.96 sec on wesleyan's server). This
    # should be cached.
    # When a foreign key relationship is defined, this query will be done
    # through Django's ORM
    cursor.execute('SELECT sentry.isbadexit, sentry.isnamed, \
            sentry.fingerprint, sentry.nickname, descriptor.bandwidthobserved, \
            descriptor.uptime, sentry.address, sentry.isfast, sentry.isexit, \
            sentry.isguard, sentry.isstable, sentry.isauthority, \
            descriptor.platform, sentry.orport, sentry.dirport, sentry.isv2dir FROM \
            descriptor RIGHT JOIN (SELECT u.isbadexit, u.isnamed, \
            u.fingerprint, u.nickname, u.address, u.isfast, u.isexit, \
            u.isguard, u.isstable, u.isauthority, u.orport, u.dirport, \
            u.descriptor, u.isv2dir, q.validafter FROM statusentry AS u JOIN \
            (SELECT nickname, MAX(validafter) AS validafter FROM statusentry \
            WHERE validafter > %s GROUP BY nickname) AS q \
            ON u.nickname = q.nickname AND u.validafter = q.validafter WHERE \
            u.validafter > %s) as sentry ON \
            sentry.descriptor = descriptor.descriptor;', \
            [validafter_range, validafter_range])

    relays = cursor.fetchall()
    num_routers = len(relays)
    client_address = request.META['REMOTE_ADDR']
    end = datetime.datetime.now()
    tock = time.clock()
    # proc_time definitely is not accurate -- looks like it doesn't take into
    # account work done with cursor
    proc_time = tock - tick
    gen_clock = end - start
    gen_time = str((gen_clock).seconds) + "." + str((gen_clock).microseconds)
    template_values = {'relay_list': relays, 'client_address': client_address, \
            'cache_updated': end, 'gen_time': gen_time, 'proc_time': proc_time,\
             'num_routers': num_routers, 'exp_time': 900}
    return render_to_response('index.html', template_values)

def details(request, fingerprint):
    """
    Supply a dictionary to the details.html template consisting of relevant
    values associated with a given fingerprint. Querying the database is done 
    with raw SQL. This needs to be fixed.
    """

    cursor = connection.cursor()
    cursor.execute('SELECT statusentry.nickname, statusentry.fingerprint, \
            statusentry.address, statusentry.orport, statusentry.dirport, \
            descriptor.platform, descriptor.published, descriptor.uptime, \
            descriptor.bandwidthburst, descriptor.bandwidthavg, \
            descriptor.bandwidthobserved, statusentry.isauthority, \
            statusentry.isbaddirectory, statusentry.isbadexit, \
            statusentry.isexit, statusentry.isfast, statusentry.isguard, \
            statusentry.isnamed, statusentry.isstable, statusentry.isrunning, \
            statusentry.isvalid, statusentry.isv2dir, statusentry.ports, \
            descriptor.rawdesc FROM statusentry JOIN descriptor ON \
            statusentry.descriptor = descriptor.descriptor WHERE \
            statusentry.fingerprint = %s ORDER BY \
            statusentry.validafter DESC LIMIT 1', [fingerprint]) 

    try: 
        nickname, fingerprint, address, orport, dirport, platform, published, \
            uptime, bandwidthburst, bandwidthavg, bandwidthobserved, \
            isauthority, isbaddirectory, isbadexit, isexit, isfast, isguard, \
            isnamed, isstable, isrunning, isvalid, isv2dir, ports, rawdesc \
            = cursor.fetchone()
    except:
        raise Http404
    
    template_values = {'nickname': nickname, 'fingerprint': fingerprint, \
            'address': address, 'orport': orport, 'dirport': dirport, \
            'platform': platform, 'published': published, 'uptime': uptime, \
            'bandwidthburst': bandwidthburst, 'bandwidthavg': bandwidthavg, \
            'bandwidthobserved': bandwidthobserved, 'isauthority': isauthority,\
             'isbaddirectory': isbaddirectory, 'isbadexit': isbadexit, \
            'isexit': isexit, 'isfast': isfast, 'isguard': isguard, \
            'isnamed': isnamed, 'isstable': isstable, 'isrunning': isrunning, \
            'isvalid': isvalid, 'isv2dir': isv2dir, 'ports': ports, \
            'rawdesc': rawdesc}

    return render_to_response('details.html', template_values)

def exitnodequery(request):
    """
    This method will present the client with a query result of an ip.


    The variables recieved from the get method are:

    queryAddress: the query address it will be an ip and this field is required

    destinationAddress: the destination address, it will be an ip and it is optional

    destinationPort: it will be a port number, it is also optional
    """
    #This method also needs a lot of work. We need some way of maintaing a list
    #of the ips. And we need to check them for the stuff inputted.

    variables = "TEMP STRING"
    message = ""
    if 'queryAddress' in request.GET:
        if request.GET['queryAddress']:
            from django.db.models import Max
            ip_address = request.GET['queryAddress']
            last_va = Statusentry.objects.aggregate\
                    (last=Max('validafter'))['last']
            if (Statusentry.objects.filter(address=ip_address, \
                    validafter__gte=(last_va - \
                    datetime.timedelta(days=1))).count() == 0):
                message = "%s is not an active Tor server" % (ip_address)
            else:
                message = "%s is an active Tor server" % (ip_address)
            #elif ( #Finish this later
    template_values = {'variables': variables,'message': message}
    return render_to_response('nodequery.html', template_values)

def csv_current_results(request):
    """
    """
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=test.csv'

    # Table is undefined now, but it should be what is returned by the query.
    writer = csv.writer(response)
    writer.writerow(['variables', 'go', 'here'])
    for row in table:
        writer.writerow(row)

    return response

def networkstatisticgraphs(request):
    variables = "TEMP STRING"

    # For now, this function is just a placeholder.
    variables = "MWAHAHA"
    template_values = {'variables': variables,}
    return render_to_response('nodequery.html', template_values)

def columnpreferences(request):
    variables = "TEMP STRING"
    template_values = {'variables': variables,}
    return render_to_response('columnpreferences.html', template_values)

def networkstatisticgraphs(request):
    """
    """

    # For now, this function is just a placeholder.
    variables = "mWAHAHA"
    template_values = {'variables': variables,}
    return render_to_response('statisticgraphs.html', template_values)

def unruly_passengers_csv(request):
    """
    """
    # For now, this function is just a placeholder.
    UNRULY_PASSENGERS = [146,184,235,200,226,251,299,273,281,304,203]
    
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=test_data.csv'

    # Create the CSV writer using the HttpResponse as the "file."
    writer = csv.writer(response)
    writer.writerow(['Year', 'Unruly Airline Passengers'])
    for (year, num) in zip(range(1995, 2006), UNRULY_PASSENGERS):
        writer.writerow([year, num])

    return response
