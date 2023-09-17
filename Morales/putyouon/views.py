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
import logging
from .forms import ReviewForm
from .models import Song, Review, Like
from .forms import ReviewForm

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
    # Retrieve the user's reviews
    reviews = Review.objects.filter(user=request.user)
    user = request.user
    liked_songs = Like.objects.filter(user=user).values_list('song_id', flat=True)
    context = {
        'user': user,
        'liked_songs': liked_songs,
    }

    # Initialize Spotify client
    client_credentials_manager = SpotifyClientCredentials(
        client_id=settings.SPOTIFY_API['CLIENT_ID'],
        client_secret=settings.SPOTIFY_API['CLIENT_SECRET']
    )
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    # Create a list to store song details for each review
    reviewed_songs = []

    for review in reviews:
        # Retrieve the song details from Spotify using the song_id saved in the review
        try:
            song_details = sp.track(review.song_id)
        except spotipy.exceptions.SpotifyException as e:
            # Handle exceptions here if needed
            song_details = None

        # Create a dictionary with song details
        song_info = {
            'title': song_details['name'] if song_details else '',
            'artist': song_details['artists'][0]['name'] if song_details else '',
            # Add more song details here as needed
        }
        reviewed_songs.append(song_info)

    # Add other profile information as needed
    # ...

    return render(request, 'profile.html', {'reviews': reviews, 'reviewed_songs': reviewed_songs, 'liked_songs': liked_songs})

def search_spotify(request):
    query = request.GET.get('q', '')
    
    if query:
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
    else:
        # No query provided, return an empty list of tracks
        tracks = []

    context = {
        'query': query,
        'tracks': tracks,
    }

    return render(request, 'search_results.html', context)

@login_required
def song_detail(request, song_id):
    client_credentials_manager = SpotifyClientCredentials(
        client_id=settings.SPOTIFY_API['CLIENT_ID'],
        client_secret=settings.SPOTIFY_API['CLIENT_SECRET']
    )
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    try:
        # Retrieve song details using the song_id
        song_details = sp.track(song_id)
    except spotipy.exceptions.SpotifyException as e:
        # Handle exceptions here if needed
        song_details = None

    # Check if the song already exists in the database based on song_id
    song, created = Song.objects.get_or_create(
        song_id=song_id,
        defaults={
            'title': song_details['name'],
            'artist': song_details['artists'][0]['name'],
            'album': song_details['album']['name'],
            'cover_url': song_details['album']['images'][0]['url'],
        }
    )

    # Check if the user has already reviewed the song
    existing_review = Review.objects.filter(user=request.user, song_id=song_id).first()

    # Check if the user has already liked the song
    existing_like = Like.objects.filter(user=request.user, song_id=song_id).first()

    if request.method == 'POST':
        if 'like' in request.POST:
            # Handle like/unlike action
            if existing_like:
                # If the user has an existing like, delete it to "unlike" the song
                existing_like.delete()
            else:
                # If the user doesn't have an existing like, create a new one
                like_form = LikeForm({'user': request.user.id, 'song_id': song_id})
                if like_form.is_valid():
                    like_form.save()

        else:
            # Handle review submission
            if existing_review:
                # If the user has an existing review, update it
                review_form = ReviewForm(request.POST, instance=existing_review)
            else:
                # If the user doesn't have an existing review, create a new one
                review_form = ReviewForm(request.POST)

            if review_form.is_valid():
                # Save the updated or new review
                review = review_form.save(commit=False)
                review.user = request.user
                review.song_id = song_id  # Use the song_id from the URL
                review.edited = True  # Set the 'edited' flag to True
                review.save()

    else:
        if existing_review:
            # If the user has an existing review, populate the review form with their review
            review_form = ReviewForm(instance=existing_review)
        else:
            # If the user doesn't have an existing review, create an empty review form
            review_form = ReviewForm()

    # Filter reviews based on the song_id stored in each review
    reviews = Review.objects.filter(song_id=song_id)

    context = {
        'song': song_details,
        'review_form': review_form,
        'reviews': reviews,
        'edited': existing_review.edited if existing_review else False,  # Pass the 'edited' flag
        'updated_created_at': existing_review.updated_at if existing_review else song.created_at if hasattr(song, 'created_at') else None,  # Pass updated created_at or song's created_at
        'liked': existing_like is not None,  # Pass whether the user has liked the song
        'song_id': song_id,  # Include the song_id in the context
    }

    return render(request, 'song_detail.html', context)

@login_required
def like_song(request, song_id):
    if request.method == 'POST':
        # Check if the user is logged in
        if request.user.is_authenticated:
            # Get the song object
            song = Song.objects.get(song_id=song_id)

            try:
                # Try to get an existing like for this user and song
                like = Like.objects.get(user=request.user, song_id=song_id)
                
                # If the like exists, delete it (unlike)
                like.delete()
                
                liked = False  # The user unliked the song
            except Like.DoesNotExist:
                # If the like does not exist, create it (like)
                Like.objects.create(user=request.user, song_id=song_id)
                
                liked = True  # The user liked the song

            like_count = Like.objects.filter(song_id=song_id).count()

            return JsonResponse({'liked': liked, 'like_count': like_count})
        else:
            # Redirect the user to the login page or show a message
            # You can customize this part based on your preference
            return redirect('login')

    return JsonResponse({'liked': liked, 'like_count': like_count})
