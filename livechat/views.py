from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.text import slugify
from django.core.paginator import Paginator
import json
from django.http import JsonResponse
from django.db.models import Count, Case, When, BooleanField

from .forms import RoomCreationForm
from .models import User, Room, Message
# Create your views here.


def index(request):
    if request.user.is_authenticated:
        user_rooms = Room.objects.filter(members=request.user)
        return render(request, "livechat/index.html", {
            "rooms": user_rooms
        })

    else:
        return render(request, "livechat/login.html")
    

def error(request, message):
    return render(request, "livechat/error.html", {
        "message": message
    })


@login_required
def room(request, slug):
    # Get room instance or return error if it doesn't exist
    try:
        room = Room.objects.get(slug=slug)
    except Room.DoesNotExist:
        message = "This room does not exist."
        return error(request, message)

    # Check if the current user is a member of the room
    if request.user not in room.members.all():
        message = "You are not authorized to enter this room."
        return error(request, message)
    
    # All messages
    # messages = Message.objects.filter(room=room)

    # Take the last 25 messages sent to the group and ordering them from newest to oldest
    messages = Message.objects.filter(room=room).order_by('-date_added')[:25][::-1]


    return render(request, "livechat/room.html", {
            "room": room,
            "messages": messages
        })


"""
# Used in conjunction with Django forms
@login_required
def create_room(request):
    if request.method == 'POST':
        form = RoomCreationForm(request.user, request.POST)
        print(request.POST)  # Add this line for debugging
        if form.is_valid():
            print(form.cleaned_data)  # Add this line for debugging
            room = form.save()
            return redirect('room', slug=room.slug)
    else:
        form = RoomCreationForm(request.user)

    return render(request, 'livechat/create_room.html', {'form': form})
"""


def save_member(user_id, room_id):
    # Get the user and room objects
    user = User.objects.get(id=user_id)
    room = Room.objects.get(id=room_id)

    # Add the user to the room's members
    room.members.add(user)

    # Save the room to persist the changes
    room.save()


def remove_member(user_id, room_id):
    # Get the user and room objects
    user = User.objects.get(id=user_id)
    room = Room.objects.get(id=room_id)

    # Remove the user from the room's members
    room.members.remove(user)

    # Save the room to persist the changes
    room.save()


@login_required
def create_room(request):
    try: 
        if request.method == 'POST':
            # Variables from Form
            room_name = request.POST["room_name"]
            owner = User.objects.get(id=request.user.id)
            slug = slugify(room_name)

            # Create the room
            new_room = Room.objects.create(
                name = room_name,
                owner = owner,
                slug = slug,
            )
            new_room.save()

            room_id = new_room.id

            # Add owner to the room
            save_member(new_room.owner.id, room_id)

            # Add other members to the room
            members = request.POST.getlist('members')
            for member_id in members:
                save_member(member_id, room_id)
            
            return redirect('room', slug=new_room.slug)
    
        if request.method == "GET":
            # Get all users excluding the current user
            users = User.objects.exclude(id=request.user.id).all()
            return render(request, "livechat/create_room.html", {
                "users": users,
            })
        
    except IntegrityError:
        users = User.objects.exclude(id=request.user.id).all()
        message = "That room name is already in use."
        return render(request, "livechat/create_room.html", {
            "users": users,
            "message": message
        })
    

def edit_room(request, slug):
    if request.method == "POST":

        # Get the Room instance or return error if not found
        try:
            room = Room.objects.get(slug=slug)
        except Room.DoesNotExist:
            message = "This room does not exist."
            return error(request, message)
        
        # Error handling for non-owner trying to make changes
        if request.user != room.owner:
            message = "You are not authorized to edit this room."
            return error(request, message)

        # Variables from Form
        new_name = request.POST["room_name"]
        remove_members_list = request.POST.getlist('remove_members')
        non_members_list = request.POST.getlist('non_members')

        # Check if a room with the new name already exists
        existing_room = Room.objects.filter(name=new_name).exclude(id=room.id).first()

        if existing_room:
            message = "A room with this name already exists."
            return error(request, message)

        # Update name/slug if changed
        if new_name != room.name:
            room.name = new_name
            room.slug = slugify(new_name)
            room.save()
        
        # Remove members from room
        if len(remove_members_list) > 0:
            for member_id in remove_members_list:
                remove_member(member_id, room.id)

        # Add members to room
        if len(non_members_list) > 0:
            for member_id in non_members_list:
                save_member(member_id, room.id)

        return redirect('room', slug=room.slug)
        
    if request.method == "GET":

        # Get room instance or return error if it doesn't exist
        try: 
            room = Room.objects.get(slug=slug)
        except:
            message = "This room does not exist."
            return error(request, message)

        # Error handling for unauthorized editing of a room
        if request.user.id != room.owner.id:
            message = "You are not authorized to take this action."
            return error(request, message)

        else:
            # List of members that can be removed (excludes Owner)
            remove_members = room.members.exclude(id=room.owner.id)

            # List of non-members that can be added
            users = User.objects.all()
            room_members = room.members.all()
            non_members = users.exclude(id__in=room_members.values_list('id', flat=True))

            return render(request, "livechat/edit_room.html", {
                "room": room,
                "remove_members": remove_members,
                "non_members": non_members,
            })
    

def leave_room(request, user_id, room_id):

    # Get the Room instance or return error if not found
    try:
        room = Room.objects.get(id=room_id)
    except:
        message = "This room does not exist."
        return error(request, message)

    # Error handling for unauthorized removal from a room
    if request.user.id != user_id:
        message = "You are not authorized to take this action."
        return error(request, message)
    
    # Error handling if the owner tries to leave a room via url
    elif request.user.id == room.owner.id:
        message = "As an owner you can't leave the room unless you delete it."
        return error(request, message)
    
    else:
        remove_member(user_id, room_id)
        return redirect('index')


def delete_room(request, slug):
    
    # Get the Room instance or return error if not found
    try: 
        room = Room.objects.get(slug=slug)
    except:
        message = "This room does not exist."
        return error(request, message)
    
    # Check if the current user is the owner of the room
    if request.user != room.owner:
        message = "You are not authorized to take this action."
        return error(request, message)

    # Delete the room from the database
    room.delete()

    return redirect('index')
    

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "livechat/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "livechat/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "livechat/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "livechat/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "livechat/register.html")
