import os
import subprocess
import time
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = "http://localhost:8888/callback"
CACHE_PATH = ".spotify_cache"

def initialize_spotify():
    """Initialize Spotify client with proper authentication handling"""
    print("Initializing Spotify client...")

    if not CLIENT_ID or not CLIENT_SECRET:
        raise ValueError(
            "Missing Spotify credentials. Please set SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET environment variables."
        )

    sp_oauth = SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope="user-read-playback-state user-read-currently-playing",
        cache_path=CACHE_PATH,
        open_browser=True
    )

    # Force authentication if no cache exists
    if not os.path.exists(CACHE_PATH):
        print("No authentication cache found. Starting first-time authentication...")
        print("A browser window will open. Please log in to Spotify and authorize the application.")
        token_info = sp_oauth.get_cached_token()
        if not token_info:
            #auth_url = sp_oauth.get_authorize_url()
            #print(f"Please visit this URL to authorize the application: {auth_url}")
            auth_code = sp_oauth.get_auth_response()
            token_info = sp_oauth.get_access_token(auth_code)
            if not token_info:
                raise Exception("Failed to get access token. Please try again.")
        print("Authentication successful! Cache file created.")

    return spotipy.Spotify(auth_manager=sp_oauth)


def refresh_token(sp_oauth):
    try:
        token_info = sp_oauth.get_cached_token()
        if not token_info:
            print("No token cache found. Starting new authentication...")
            auth_url = sp_oauth.get_authorize_url()
            print(f"Please visit this URL to authorize the application: {auth_url}")
            auth_code = sp_oauth.get_auth_response()
            token_info = sp_oauth.get_access_token(auth_code)
            if not token_info:
                return None

        if sp_oauth.is_token_expired(token_info):
            print("Token expired, refreshing...")
            try:
                token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
                sp_oauth.cache_handler.save_token_to_cache(token_info)
                print("Token refreshed successfully")
            except Exception as e:
                print(f"Error refreshing token: {e}")
                return None

        return token_info['access_token']

    except Exception as e:
        print(f"Error in token refresh: {e}")
        return None


def get_current_track(sp):
    try:
        # Try both endpoints to get playback information
        current = sp.currently_playing()
        playback = sp.current_playback()

        print("\nDebug - API responses:")
        print(f"currently_playing response: {current is not None}")
        print(f"current_playback response: {playback is not None}")

        # If both endpoints return None, player might be inactive
        if current is None and playback is None:
            print("No active playback detected")
            return None

        # If we have a current track response, use it
        if current is not None:
            # Check if it's an advertisement
            if current.get('currently_playing_type') == 'ad':
                print("Advertisement detected via API")
                return {
                    'track_name': 'Advertisement',
                    'track_length': 0,
                    'track_artist': '',
                    'is_playing': True,
                    'is_ad': True
                }

            item = current.get('item')
            is_playing = current.get('is_playing', False)
        # Fall back to playback data if current track data isn't available
        elif playback is not None:
            item = playback.get('item')
            is_playing = playback.get('is_playing', False)
        else:
            return None

        # If there's no item but playback is active, it might be an ad
        if item is None and (current or playback):
            print("No track item but playback is active - likely an advertisement")
            return {
                'track_name': 'Advertisement',
                'track_length': 0,
                'track_artist': '',
                'is_playing': is_playing,
                'is_ad': True
            }

        return {
            'track_name': item.get('name', 'Unknown'),
            'track_length': item.get('duration_ms', 0) / 1000,
            'track_artist': ', '.join([artist['name'] for artist in item.get('artists', [])]),
            'is_playing': is_playing,
            'is_ad': False
        }
    except Exception as e:
        print(f"Error getting track info: {e}")
        return None


def is_ad_playing(track_info):
    if track_info is None:
        return False

    print("\nAd Detection Analysis:")
    print(f"Track info: {track_info}")

    # Check explicit ad flag
    if track_info.get('is_ad', False):
        print("Detected as advertisement (explicit flag)")
        return True

    # Check for very short track or missing artist
    if track_info['track_length'] < 30 or not track_info['track_artist']:
        print(
            f"Detected as advertisement (length: {track_info['track_length']}s, artist: '{track_info['track_artist']}')")
        return True

    print("Not detected as advertisement")
    return False


def check_for_ads(sp):
    track_info = get_current_track(sp)
    if track_info:
        print(f"\nCurrent Track Details:")
        for key, value in track_info.items():
            print(f"{key}: {value}")

        return is_ad_playing(track_info)
    return False


def get_spotify_session():
    sessions = AudioUtilities.GetAllSessions()
    for session in sessions:
        try:
            if session.Process and session.Process.name() == "Spotify.exe":
                return session
        except Exception as e:
            print(f"Error checking session: {e}")
            continue
    return None


def mute_spotify(mute=True):
    try:
        session = get_spotify_session()
        if session:
            volume = session.SimpleAudioVolume
            current_mute = volume.GetMute()

            if current_mute != mute:
                volume.SetMute(mute, None)
                print(f"Spotify {'muted' if mute else 'unmuted'} successfully")
            else:
                print(f"Spotify already {'muted' if mute else 'unmuted'}")

            # Double-check mute state
            if volume.GetMute() != mute:
                print("Warning: Mute state didn't change as expected")
                volume.SetMute(mute, None)  # Try one more time
        else:
            print("Spotify session not found")
    except Exception as e:
        print(f"Error while muting: {e}")


def restart_spotify():
    print("\nRestarting Spotify...")
    try:
        subprocess.run("taskkill /f /im Spotify.exe", shell=True)
        time.sleep(2)
        subprocess.Popen("spotify", shell=True)
        time.sleep(5)
    except Exception as e:
        print(f"Error restarting Spotify: {e}")


def monitor_spotify():
    try:
        # Initialize Spotify client with proper authentication
        sp = initialize_spotify()
        sp_oauth = sp.auth_manager
    except Exception as e:
        print(f"Failed to initialize Spotify client: {e}")
        return


    is_muted = False
    consecutive_errors = 0
    max_errors = 3
    last_check_time = 0

    print("\nStarting Spotify ad monitor...")
    print("Waiting for Spotify playback...")

    while True:
        try:
            current_time = time.time()

            # Ensure we're not checking too frequently
            if current_time - last_check_time < 1:
                time.sleep(0.1)
                continue

            token = refresh_token(sp_oauth)
            if not token:
                print("No valid token. Waiting before retry...")
                time.sleep(30)
                continue

            sp.auth = token

            is_ad = check_for_ads(sp) # Passing sp to check_for_ads
            print(f"\nAd check result: {is_ad}")

            if is_ad:
                if not is_muted:
                    print("Ad detected, muting...")
                    mute_spotify(True)
                    is_muted = True
            else:
                if is_muted:
                    print("Regular content detected, unmuting...")
                    mute_spotify(False)
                    is_muted = False

            consecutive_errors = 0
            last_check_time = current_time

            # Short sleep to prevent hammering the API
            time.sleep(1)

        except Exception as e:
            print(f"\nError in main loop: {e}")
            consecutive_errors += 1

            if consecutive_errors >= max_errors:
                print(f"Too many consecutive errors ({consecutive_errors}). Restarting Spotify...")
                restart_spotify()
                consecutive_errors = 0
                time.sleep(5)
            else:
                time.sleep(2)


if __name__ == "__main__":
    monitor_spotify()