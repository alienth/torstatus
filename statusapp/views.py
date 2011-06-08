from statusapp.models import Statusentry, Descriptor
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse, HttpRequest


import os

def index(request):
    statusEntry_FullList = Statusentry.objects.filter(pk='2011-05-31 19:00:00')
    descriptor_list = []
    for entry in statusEntry_FullList:
        try:
            descriptor_list.append(Descriptor.objects.get(pk=entry.descriptor))
        except:
            descriptor_list.append(Descriptor())
    template_values = zip(statusEntry_FullList, descriptor_list)
    return render_to_response('index.html', {'template_values': template_values})

