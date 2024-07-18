import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import yt_dlp

def res_spotify_url(spotify_url, client_id, client_secret):
    sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id, client_secret))
    track_info = sp.track(spotify_url)
    track_name = track_info['name']
    artist_name = track_info['artists'][0]['name']
    search_query = f"{track_name} {artist_name}"
    ydl_opts = {
        'format': 'bestaudio/best',
        'quiet': True,
        'skip_download': True,
        'extract_flat': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        search_results = ydl.extract_info(f"ytsearch:{search_query}", download=False)
        video_url = f"https://www.youtube.com/watch?v={search_results['entries'][0]['id']}"
        return video_url

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 4:
        
        sys.exit(1)
    spotify_url = sys.argv[1]
    client_id = sys.argv[2]
    client_secret = sys.argv[3]
    youtube_url = res_spotify_url(spotify_url, client_id, client_secret)
    print(youtube_url)
