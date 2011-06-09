from statusapp.models import Statusentry, Descriptor
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpRequest

def index(request):
    statusentries = Statusentry.objects.filter(pk='2011-05-31 19:00:00')

    descriptors = []
    for statusentry in statusentries:
        try:
            descriptors.append(Descriptor.objects.get(descriptor=statusentry.descriptor))
        except:
            descriptors.append(Descriptor())

    statuses_descriptors = zip(statusentries, descriptors)

    clientAddress = request.META['REMOTE_ADDR']
    
    template_values = {'statuses_descriptors': statuses_descriptors, 'clientAddress': clientAddress}
    
    return render_to_response('index.html', template_values)

