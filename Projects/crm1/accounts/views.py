from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def home(request):
    return render(request, 'accounts/Dashboard.html')

def products(request):
    return render(request, 'accounts/Products.html')

def customer(request):
    return render(request, 'accounts/Customer.html')
