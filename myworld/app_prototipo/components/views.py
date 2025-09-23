from django.http import HttpResponse
from django.template import loader

def components(request):
  template = loader.get_template('advance_search.html')
  return HttpResponse(template.render())