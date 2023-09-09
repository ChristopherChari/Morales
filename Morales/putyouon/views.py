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
from django.shortcuts import render, redirect
from .models import Song, Like, Review
from .forms import ReviewForm
from django.http import Http404


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
    
    reviews = Review.objects.filter(user=request.user)
    
    # Initialize Spotify client
    client_credentials_manager = SpotifyClientCredentials(
        client_id=settings.SPOTIFY_API['CLIENT_ID'],
        client_secret=settings.SPOTIFY_API['CLIENT_SECRET']
    )
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    # Create an empty list to store song details for the user's reviews
    reviewed_songs = []

    # Fetch song details for each review
    for review in reviews:
        try:
            song_details = sp.track(review.song_id)
        except spotipy.exceptions.SpotifyException as e:
            # Handle exceptions here if needed
            song_details = None

        # Append the song details to the list
        reviewed_songs.append(song_details)

    # Include other profile information as needed
    # ...

    context = {
        'reviews': reviews,
        'reviewed_songs': reviewed_songs,  # Include the song details in the context
        # Add other profile information here
    }

    return render(request, 'profile.html', context)
    

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

    try:
        # Retrieve song details using the song_id
        song = sp.track(song_id)
    except spotipy.exceptions.SpotifyException as e:
        # Handle exceptions here if needed
        song = None

    # Include the song_id and an empty ReviewForm in the context dictionary
    context = {
        'song': song,
        'song_id': song_id,
        'form': ReviewForm(),
    }

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            # Save the review to the database
            review = form.save(commit=False)
            review.user = request.user
            review.song_id = song_id  # Associate the review with the song_id
            review.save()
            # Redirect or return a success response
        
            # Handle the case where the form is not valid

    return render(request, 'song_detail.html', context)

def like_song(request, song_id):
    if request.method == 'POST':
        # Check if the user is logged in
        if request.user.is_authenticated:
            # Get the song object
            song = Song.objects.get(song_id=song_id)

            # Check if the user has already liked the song
            if not Like.objects.filter(user=request.user, song_id=song_id).exists():
                # Create a new Like object
                Like.objects.create(user=request.user, song_id=song_id)
        else:
            # Redirect the user to the login page or show a message
            # You can customize this part based on your preference
            return redirect('login')

    # Redirect the user back to the song detail page
    return redirect('song_detail', song_id=song_id)

from .forms import ReviewForm
