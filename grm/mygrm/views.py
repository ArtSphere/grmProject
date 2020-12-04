from django.shortcuts import render

# Create your views here.
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render

def index_view(request):
    return render(request, 'mygrm/index.html')

def show_data(request):
    print("####", "kekse: ", request.POST)
    user = request.POST['user']
    password = request.POST['password']
    return render(request, 'mygrm/showdata.html', {
            'user': user,
            'password': password,
        })