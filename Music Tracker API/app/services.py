import spotipy
from spotipy.oauth2 import SpotifyOAuth
from app.models import Track
from app import db
from app.config import Config

# Spotify client setup
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=Config.CLIENT_ID,
    client_secret=Config.CLIENT_SECRET,
    redirect_uri=Config.REDIRECT_URI,
    scope=Config.SPOTIFY_SCOPE
))

# Function to fetch and store recent tracks
def fetch_recent_tracks():
    results = sp.current_user_recently_played(limit=50)
    for item in results['items']:
        track_name = item['track']['name']
        artist_name = item['track']['artists'][0]['name']
        played_at = item['played_at']
        
        # Check for duplicates
        if not Track.query.filter_by(played_at=played_at).first():
            new_track = Track(track_name=track_name, artist_name=artist_name, played_at=played_at)
            db.session.add(new_track)
            db.session.commit()
            print(f"Saved track: {track_name} by {artist_name} at {played_at}")

# Scheduler to fetch new tracks at intervals
from apscheduler.schedulers.background import BackgroundScheduler
scheduler = BackgroundScheduler()
scheduler.add_job(fetch_recent_tracks, 'interval', minutes=1)