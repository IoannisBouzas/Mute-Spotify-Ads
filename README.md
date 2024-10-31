# Mute Spotify Ads

This project mutes Spotify automatically when an ad is detected, then unmutes when a song starts. Ideal for those who want to listen without ads interrupting the flow.

## Features
- **Automatic Ad Muting**: Detects Spotify ads and mutes the volume.
- **Auto-Unmute on Song Playback**: Unmutes Spotify when a song is playing.
- **Secure Credential Handling**: Keeps sensitive credentials secure using environment variables.

## Requirements
- **Python 3.9+**
- **Spotify Developer Account** (required for Spotify API access)
- **Python Libraries**:
  - [Spotipy](https://spotipy.readthedocs.io/en/2.16.1/) - to access the Spotify API.
  - [Pycaw](https://github.com/AndreMiras/pycaw) - for controlling Spotify volume independently.
  - [psutil](https://github.com/giampaolo/psutil) - to manage Spotify processes.

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/IoannisBouzas/Mute-Spotify-Ads.git
cd Mute-Spotify-Ads
```

### 2. Install the Required Libraries
```bash
pip install spotipy pycaw psutil python-dotenv
```
### 3. Set Up a Spotify Developer Account
- Go to the [Spotify Developer Dashboard](https://developer.spotify.com/) and create a new application.
- In Redirect URIs, add: http://localhost/
- Copy your **Client ID** and **Client Secret**.

### 4. Configure Environment Variables

To keep credentials secure, set up environment variables on your system.

- **Option 1: Environment Variables** **(Recommended)**
  - **On Windows:**
  - Open Command Prompt and run:
    ```bash
    setx SPOTIPY_CLIENT_ID "your_client_id"
    setx SPOTIPY_CLIENT_SECRET "your_client_secret"
    ```
  - **On macOS/Linux:**
  - Open Command Prompt and run:
    ```bash
    export SPOTIPY_CLIENT_ID="your_client_id"
    export SPOTIPY_CLIENT_SECRET="your_client_secret"
    ```
### 5. Run the Script

Ensure Spotify is open, then run the script:
```bash
python Mute-Spotify-Ads.py
```

## How the Script Works
This script interacts with Spotify’s API to determine what’s currently playing, and it uses other Python libraries to control and monitor the Spotify app itself. Here’s a step-by-step overview of the main processes:

- Here is the general flow:
    
         Start 
         ↓
         Check token → Refresh if needed
         ↓
         Get current track info from multiple sources
         ↓
         Check for ad using multiple methods
         ↓
         Update mute state if needed
         ↓
         Wait appropriate interval
         ↓
         Repeat



### 1. Authentication and Setup:
- The script authenticates with Spotify’s API using the Spotipy library. It uses OAuth 2.0 to obtain an access token, which allows it to fetch information about the currently playing track.

- To keep sensitive credentials (Client ID and Secret) secure, it retrieves them from environment variables rather than hardcoding them into the script.

### 2. Continuous Playback Monitoring:

- Once authenticated, the script enters a loop that continuously checks the current playback state on Spotify. It does this by making requests to Spotify’s API, which provides details such as the track’s title, artist, album, and, importantly, its type (either ad or track).

### 3. Ad Detection and Volume Control:

- When Spotify API returns an item with the type ad, the script mutes Spotify’s volume:

  - The `pycaw` library allows the script to target only Spotify’s audio session, muting it without affecting the overall system volume. This way, other apps or notifications remain audible while the ad is muted.

- When the API shows that a song (type track) is playing again, the script unmutes Spotify’s volume automatically.

### 4. Process Management for Reliability:

- Occasionally, Spotify might stop responding, which can interrupt the script. To handle this, the script uses the psutil library to check if the Spotify process is running and responsive.

- If it detects issues with Spotify’s process, the script can kill and restart Spotify automatically. This ensures that the script continues functioning even if Spotify encounters problems.

### 5. Error Handling and Rate Limits:

- Spotify’s API has rate limits to prevent excessive requests in a short period. The script implements a delay between API calls, ensuring that it doesn’t exceed these limits while still checking often enough to catch ads.
- The script also includes error handling to manage authentication errors (such as expired tokens) and other potential issues gracefully, minimizing disruptions.

## Important Note

- **New Connection**: When you do the authentication process you will receive an email from spotify that will inform you for a new connection and maybe they will suggest you to change a new password due to **_"Suspicious Actions"_**. Use this script at your own risk.

## Troubleshooting

- **Authentication Errors**: Delete any `.cache` files in the project directory to reset the authentication flow.
- **No Sound Muting**: Ensure `pycaw` is installed and your system supports application-specific volume control.
- **Spotify Not Detected**: Check if Spotify is running and accessible on the same device.
- **Rate Limiting**: If you encounter rate-limiting issues, adjust the `CHECK_INTERVAL` in the script to reduce the frequency of API calls.
