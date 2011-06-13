from statusapp.models import Statusentry, Descriptor
from django.shortcuts import render_to_response #get_object_or_404
from django.http import HttpResponse, HttpRequest, Http404
import csv

def index(request):
    """
	statusEntry_FullList = Statusentry.objects.filter(pk='2011-05-31 19:00:00')
	descriptor_list = []
	for entry in statusEntry_FullList:
		try:
			descriptor_list.append(Descriptor.objects.get(pk=entry.descriptor))
		except:
			descriptor_list.append(Descriptor())
	statusEntry_descriptorEntry = zip(statusEntry_FullList, descriptor_list)
	clientAddress = request.META['REMOTE_ADDR']
	template_values = {'statusEntry_descriptorEntry': statusEntry_descriptorEntry, 'clientAddress': clientAddress, }
	return render_to_response('index.html', template_values)
    """
    from django.db import connection

    cursor = connection.cursor()

    cursor.execute('SELECT MAX(validafter) FROM statusentry')

    last_validafter = cursor.fetchone()[0]

    cursor.execute('SELECT statusentry.isbadexit, statusentry.isnamed, \
            statusentry.fingerprint, statusentry.nickname, \
            descriptor.bandwidthobserved, descriptor.uptime, \
            statusentry.address, statusentry.isfast, statusentry.isexit, \
            statusentry.isguard, statusentry.isstable, statusentry.isauthority, \
            descriptor.platform, statusentry.orport, statusentry.dirport FROM \
            statusentry LEFT JOIN descriptor ON statusentry.descriptor = \
            descriptor.descriptor WHERE statusentry.validafter = %s', \
            [last_validafter]) # Ugly, yes, but functional -- misses FOUR
                               # descriptors (out of 2256)

    relays = cursor.fetchall()
    client_address = request.META['REMOTE_ADDR']
    template_values = {'relay_list': relays, 'client_address': client_address}
    return render_to_response('index.html', template_values)

def details(request, fingerprint):
    """
    statuses = Statusentry.objects.filter(fingerprint=fingerprint)
    status_count = int(statuses.count())
    recent_statuses = statuses[max(-1, (status_count - 73)):status_count]
    recent_statuses_list = list(recent_statuses)
    recent_statuses_list.reverse()

    descriptor = None
    i = 0
    while ((descriptor == None) & (i < 72)):
        try:
            descriptor = Descriptor.objects.get(descriptor=recent_statuses_list[i].descriptor)
        except:
            i += 1
    
    if (i == 72):
        i = 0
    template_values = {'status': recent_statuses[i], 'descriptor': descriptor}
    return render_to_response('details.html', template_values)
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
            statusentry.isvalid, statusentry.isv2dir, statusentry.ports FROM \
            statusentry JOIN descriptor ON statusentry.descriptor = \
            descriptor.descriptor WHERE statusentry.fingerprint = %s ORDER BY \
            statusentry.validafter DESC LIMIT 1', [fingerprint]) 

    try: 
        nickname, fingerprint, address, orport, dirport, platform, published, \
            uptime, bandwidthburst, bandwidthavg, bandwidthobserved, \
            isauthority, isbaddirectory, isbadexit, isexit, isfast, isguard, \
            isnamed, isstable, isrunning, isvalid, isv2dir, ports = cursor.fetchone()
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
            'isvalid': isvalid, 'isv2dir': isv2dir, 'ports': ports}

    return render_to_response('details.html', template_values)

def exitnodequery(request):
    variables = "MWAHAHA"
    template_values = {'variables': variables,}
    return render_to_response('nodequery.html', template_values)

def networkstatisticgraphs(request):
    variables = "mWAHAHA"
    template_values = {'variables': variables,}
    return render_to_response('statisticgraphs.html', template_values)

def columnpreferences(request):
    variables = "SOMETHING"
    template_values = {'variables': variables,}
    return render_to_response('columnpreferences.html', template_values)

UNRULY_PASSENGERS = [146,184,235,200,226,251,299,273,281,304,203]

def unruly_passengers_csv(request):
    # Create the HttpResponse object with the appropriate CSV header.
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=test_data.csv'

    # Create the CSV writer using the HttpResponse as the "file."
    writer = csv.writer(response)
    writer.writerow(['Year', 'Unruly Airline Passengers'])
    for (year, num) in zip(range(1995, 2006), UNRULY_PASSENGERS):
        writer.writerow([year, num])

    return response
