from statusapp.models import Statusentry
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse

import os

def index(request):
	statusEntry_FullList = Statusentry.objects.all()
	debugText = ""
	if statusEntry_FullList:
		debugText = "Everything is fine!"
		template_values = {'statusEntry_FullList': statusEntry_FullList, 'debugText': debugText}
	else:
		debugText = "Didn't get anything from the all()"
		template_values = {'debugText': debugText}
	return render_to_response('statusapp/index.html', template_values)

def displayFlag(request, country_code):
	imagePath = os.path.join(os.path.dirname(__file__), 'templates/statusapp/flags/' + str(country_code) + '.gif')
	from PIL import Image
	Image.init()
	i = Image.open(imagePath)
	response = HttpResponse(content_type='image/gif')
	i.save(response, 'GIF')
	return response

