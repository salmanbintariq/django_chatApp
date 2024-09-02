from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.forms import UserCreationForm 
from .models import Room, Topic, Message
from .forms import RoomForm,UserForm
from django.db.models import Q


def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username,password=password)
        
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'home')
            return redirect('home')
        else:
            messages.error(request, "Invalid username and password.") 
    
    context = {'page':page}
    return render(request, 'base/login_register.html', context)


def logoutUSer(request):
    logout(request)
    return redirect('home')


def registerUser(request):
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    context = {'form':form}
    return render(request, 'base/login_register.html', context)


def home(request):
    q = request.GET.get('q','')
    topics = Topic.objects.all()[0:5]
    if q:
        query = Room.objects.filter(
            Q(topic__name__icontains=q) |
            Q(name__icontains=q) |
            Q(description__icontains=q)
            )
        
    else:
        query = Room.objects.all()   
    room_count = query.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))
    context = {
        'query':query,
        'topics': topics,
        'room_count': room_count,
        'q':q,
        'room_messages': room_messages,
        }
    return render(request,'base/home.html', context)

def room(request, id):
    query = Room.objects.get(id=id)
    room_messages = query.message_set.all().order_by('-created')
    participants = query.participants.all()

    if request.method == 'POST':
        new_message = Message(
            user=request.user, 
            room=query, 
            body=request.POST.get('body')
            )
        new_message.save()
        query.participants.add(request.user)
        return redirect('room', id=query.id)  # Redirect back to the room page with the new message.

    context = {'query':query, 'room_messages':room_messages, 'participants':participants}  
    return render(request,'base/room.html', context)


def userProfile(request,id):
    user = User.objects.get(id=id)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()

    context = {'user':user, 'query':rooms, 'room_messages':room_messages, 'topics':topics }
    return render(request,'base/profile.html', context)

@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    topics = Topic.objects.all()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(
            host = request.user,
            topic = topic,
            name = request.POST.get('name'),
            description = request.POST.get('description')
        )    
        return redirect('home')
        
    context = {'form':form, 'topics':topics}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def roomUpdate(request, id):
    room = get_object_or_404(Room, id=id)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()
    
    if request.user != room.host:
        return HttpResponse('You are not allowed here!!')
    
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        form = RoomForm(request.POST, instance=room)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        
        return redirect('home')
        
            
    context = {'form':form, 'topics':topics, 'room':room}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def roomDelet(request, id):
    room = get_object_or_404(Room, id=id)

    if request.user != room.host:
        return HttpResponse('You are not able to do it!!')

    previous_url = request.META.get('HTTP_REFERER', '/') # Default to home if no referer

    if request.method == 'POST':
        room.delete()
        return redirect('home')
    context = {'obj':room, 'previous_url':previous_url}
    return render(request, 'base/delete.html', context)


@login_required(login_url='login')
def messageDelet(request, id):
    message = Message.objects.get(id=id)

    if request.user != message.user:
        return HttpResponse('You are not able to do it!!')

    previous_url = request.META.get('HTTP_REFERER', '/') # Default to home if no referer

    if request.method == 'POST':
        message.delete()
        return redirect('home')
    context = {'obj':message, 'previous_url':previous_url}
    return render(request, 'base/delete.html', context)

@login_required(login_url='login')
def updateUser(request):
    form = UserForm(instance=request.user)

    if request.method == 'POST':
        form = UserForm(request.POST, instance=request.user)
        if form.is_valid:
            form.save()
            return redirect('user-profile', id=request.user.id)
        
    context = {'form':form,}
    return render(request, 'base/update-user.html',context)

def topicsPage(request):

    q = request.GET.get('q','')
    topics = Topic.objects.filter(name__icontains=q)
    context = {'topics': topics}
    return render(request, 'base/topics.html', context)

def activityPage(request):
    room_messages = Message.objects.all()
    context = {'room_messages': room_messages}
    return render(request, 'base/activity.html',context)