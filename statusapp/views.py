from statusapp.models import Statusentry, Descriptor
from django.shortcuts import render_to_response #get_object_or_404
from django.http import HttpResponse, HttpRequest, Http404
import csv

# To do: get rid of javascript sorting: pass another argument
# to this view function and sort the table accordingly.
def index(request):
    """
    Supply a dictionary to the index.html template consisting of keys
    equivalent to columns in the statusentry and descriptor tables in the
    database. Querying the database is done with raw SQL, and currently
    only relays in the last consensus are found. This needs to be fixed
    as soon as possible.
    """

    from django.db import connection
    import datetime

    cursor = connection.cursor()

    cursor.execute('SELECT MAX(validafter) FROM statusentry')

    validafter_range = (cursor.fetchone()[0] - datetime.timedelta(hours=24))

    ## Problem: only gets routers published in the last consensus, not in
    ## the last 24 hours.

    # New Problem: Query takes a LONG time (7.96 sec on marlow). 
    # cache is NECESSARY!

    # Other Problem: this is even uglier.
    cursor.execute('SELECT sentry.isbadexit, sentry.isnamed, \
            sentry.fingerprint, sentry.nickname, descriptor.bandwidthobserved, \
            descriptor.uptime, sentry.address, sentry.isfast, sentry.isexit, \
            sentry.isguard, sentry.isstable, sentry.isauthority, \
            descriptor.platform, sentry.orport, sentry.dirport FROM \
            descriptor RIGHT JOIN (SELECT u.isbadexit, u.isnamed, \
            u.fingerprint, u.nickname, u.address, u.isfast, u.isexit, \
            u.isguard, u.isstable, u.isauthority, u.orport, u.dirport, \
            u.descriptor, q.validafter FROM statusentry AS u JOIN \
            (SELECT nickname, MAX(validafter) AS validafter FROM statusentry \
            WHERE validafter > %s GROUP BY nickname) AS q \
            ON u.nickname = q.nickname AND u.validafter = q.validafter WHERE \
            u.validafter > %s) as sentry ON \
            sentry.descriptor = descriptor.descriptor;', \
            [validafter_range, validafter_range])

    relays = cursor.fetchall()
    client_address = request.META['REMOTE_ADDR']
    template_values = {'relay_list': relays, 'client_address': client_address}
    return render_to_response('index.html', template_values)

def details(request, fingerprint):
    """
    Supply a dictionary to the details.html template consisting of keys
    equivalent to columns in the statusentry and descriptor tables in the
    database. Querying the database is done with raw SQL.
    """

    from django.db import connection

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
            isnamed, isstable, isrunning, isvalid, isv2dir, ports, rawdesc = cursor.fetchone()
    except:
        raise Http404
    
    template_values = {'nickname': nickname, 'fingerprint': fingerprint, \
            'address': address, 'orport': orport, 'dirport': dirport, \
            'platform': platform, 'published': published, 'uptime': uptime, \
            'bandwidthburst': bandwidthburst, 'bandwidthavg': bandwidthavg, \
            'bandwidthobserved': bandwidthobserved, 'isauthority': isauthority, \
            'isbaddirectory': isbaddirectory, 'isbadexit': isbadexit, \
            'isexit': isexit, 'isfast': isfast, 'isguard': isguard, \
            'isnamed': isnamed, 'isstable': isstable, 'isrunning': isrunning, \
            'isvalid': isvalid, 'isv2dir': isv2dir, 'ports': ports, 'rawdesc': rawdesc}

    return render_to_response('details.html', template_values)

def exitnodequery(request):
    """
    """

    # For now, this function is just a placeholder.
    variables = "MWAHAHA"
    template_values = {'variables': variables,}
    return render_to_response('nodequery.html', template_values)

def networkstatisticgraphs(request):
    """
    """

    # For now, this function is just a placeholder.
    variables = "mWAHAHA"
    template_values = {'variables': variables,}
    return render_to_response('statisticgraphs.html', template_values)

def columnpreferences(request):
    """
    """

    # For now, this function is just a placeholder.
    variables = "SOMETHING"
    template_values = {'variables': variables,}
    return render_to_response('columnpreferences.html', template_values)

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
