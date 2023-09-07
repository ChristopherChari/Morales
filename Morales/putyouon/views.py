import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from django.conf import settings
from django.shortcuts import render, HttpResponse, redirect
from .models import Song
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import (
    LoginView, LogoutView, PasswordResetView,
    PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView,
)
from django.http import JsonResponse
import requests
from .forms import CustomUserCreationForm 

from spotipy.oauth2 import SpotifyOAuth
from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, "home.html")


def song_list(request):
    songs = Song.objects.all()
    return render(request, 'songs.html', {'songs': songs})

# Login view
class CustomLoginView(LoginView):
    template_name = 'login.html'
    authentication_form = AuthenticationForm

# Logout view
class CustomLogoutView(LogoutView):
    next_page = 'home'  # Redirect to your home page after logout

# Registration view
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/registration.html', {'form': form})

# Password Reset views (you can customize these as needed)
class CustomPasswordResetView(PasswordResetView):
    template_name = 'password_reset.html'

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'password_reset_done.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'password_reset_confirm.html'

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'password_reset_complete.html'

def profile_view(request):
    return render(request, 'profile.html')

# views.py

# views.py

def search_spotify(request, query):
    # Initialize Spotify client
    client_credentials_manager = SpotifyClientCredentials(
        client_id=settings.SPOTIFY_API['CLIENT_ID'],
        client_secret=settings.SPOTIFY_API['CLIENT_SECRET']
    )
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    # Make a Spotify API request (example: search for tracks)
    results = sp.search(q=query, type='track', limit=10)

    # Extract relevant data from the results
    tracks = results.get('tracks', {}).get('items', [])

    return render(request, 'search_results.html', {'tracks': tracks})


def song_detail(request, song_id):
    # Initialize Spotify client
    client_credentials_manager = SpotifyClientCredentials(
        client_id=settings.SPOTIFY_API['CLIENT_ID'],
        client_secret=settings.SPOTIFY_API['CLIENT_SECRET']
    )
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    # Retrieve song details using the song_id
    song = sp.track(song_id)

    return render(request, 'song_detail.html', {'song': song})