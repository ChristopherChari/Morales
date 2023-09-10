# spotify_filters.py
from django import template
from django.conf import settings  # Import the settings module
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy

register = template.Library()

@register.filter
def fetch_song_data_from_spotify(song_id):
    # Get Spotify API credentials from Django settings
    client_id = settings.SPOTIFY_API['CLIENT_ID']
    client_secret = settings.SPOTIFY_API['CLIENT_SECRET']

    # Initialize the Spotify client credentials manager
    client_credentials_manager = SpotifyClientCredentials(
        client_id=client_id,
        client_secret=client_secret
    )
    
    # Initialize the Spotify client
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    try:
        # Retrieve song details using the song_id
        song_details = sp.track(song_id)
        if song_details:
            # Extract relevant song data
            title = song_details.get('name')
            artists = song_details.get('artists')
            if artists:
                artist = artists[0].get('name')
            else:
                artist = "Unknown Artist"

            # Get album cover URL
            album_cover_url = song_details.get('album', {}).get('images', [])[0].get('url', '')

            # Create a dictionary with song details
            song_data = {
                'title': title,
                'artist': artist,
                'album_cover_url': album_cover_url,  # Add album cover URL
                # Add more song details as needed
            }
            return song_data
    except spotipy.exceptions.SpotifyException as e:
        # Handle exceptions here if needed
        pass

    return None