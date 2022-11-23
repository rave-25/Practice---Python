from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def dashboard(request):
    return render(request, 'accounts/Dashboard.html')

def client(request):
    return render(request, 'accounts/Client.html')

def orders(request):
    return render(request, 'accounts/Orders.html')

def issues(request):
    return render(request, 'accounts/Issues.html')