from django.shortcuts import render
from django.views.generic import TemplateView

def page_not_found(request, exception):
    return render(request, template_name='pages/404.html', status=404)

def forbidden(request, exception):
    return render(request, 'pages/403csrf.html', status=403)

def internal_server_error(request):
    return render(request, 'pages/500.html', status=500)

class About(TemplateView):
    template_name = 'pages/about.html'

class Rules(TemplateView):
    template_name = 'pages/rules.html'
