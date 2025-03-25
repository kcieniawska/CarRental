from django.shortcuts import render
from django.shortcuts import HttpResponse

def index(request):
    return  HttpResponse("List of cars")

def car(request, car_id):
    return HttpResponse(f"Car with id {car_id}")

def category(request, name):
    return HttpResponse(f"Category {name}")