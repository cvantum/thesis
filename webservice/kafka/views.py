from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

def index(request):
    return render(request, 'kafka/index.html')

def room(request, room_name):
    return render(request, 'kafka/rooms.html', {
        'room_name': room_name
    })