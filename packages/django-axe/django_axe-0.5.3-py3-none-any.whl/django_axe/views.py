import logging
from django.shortcuts import render

logger = logging.getLogger(name="django_axe").setLevel(level=logging.INFO)

def home(request):
    return render(request=request, template_name="base.html")
