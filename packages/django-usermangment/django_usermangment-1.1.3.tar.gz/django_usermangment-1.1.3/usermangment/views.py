from django.shortcuts import render
from django.views.generic import View


# Create your views here.
def home(request):
    return render(request, 'home.html', {'title': 'Home'})