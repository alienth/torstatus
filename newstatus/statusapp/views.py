from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpRequest

from statusapp.models import *

def index(request):
    """
    """
    
    template_values = {}

    return render_to_response('index.html', template_values)
