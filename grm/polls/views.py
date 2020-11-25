from django.shortcuts import render

from django.http import HttpResponse


def index(request):
    return HttpResponse("Hallo Tom, Papa ist der coolste Mensch der Welt")
