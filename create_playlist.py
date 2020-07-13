
"""
Step 1: Log into YouTube
Step 2: Grab our liked videos
Step 3: Create a new playlist on Spotify
Step 4: Search for the song
Step 5: Add song to the Spotify playlist

"""

import json
import requests
import os

import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
import youtube_dl
from exception import ResponseException
from secrets import spotify_user_id, spotify_token


class CreatePlaylist:

    def __init__(self):
        self.user_id = spotify_user_id
        self.spotify_token = spotify_token
        self.youtube_client = self.get_youtube_client()
        self.all_song_info = {}

    # Step 1: Log into YouTube
    def get_youtube_client(self):
        # Copied from YouTube API
        # Disable OAuthlib's HTTPS verification when running locally.
        # *DO NOT* leave this option enabled in production.
        os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

        api_service_name = "youtube"
        api_version = "v3"
        client_secrets_file = "client_secrets.json"

        # Get credentials and create an API client
        scopes = ["https://www.googleapis.com/auth/youtube.readonly"]
        flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
            client_secrets_file, scopes)
        credentials = flow.run_console()

        # from the youtube DATA API
        youtube_client = googleapiclient.discovery.build(
            api_service_name, api_version, credentials=credentials)

        return youtube_client

    # Step 2: Grab our liked videos & Creating a Dictionary of Important Song Information
    def get_liked_videos(self):
        request = self.youtube_client.videos().list(
            part="snippet,contentDetails,statistics",
            myRating="like"
        )
        response = request.execute()

        # Collect each video and important information
        for item in response["items"]:
            video_title = item["snippet"]["title"]
            youtube_url = "http://www.youtube.com/watch?v={}".format(item["id"])

        # Use youtube_dl to collect the song and artist name
        video = youtube_dl.YoutubeDL({}).extract_info(youtube_url, download=False)

        song_name = video["track"]
        artist = video["artist"]

        if song_name is not None and artist is not None:
            # Save all important info and skip any missing song and artist
            self.all_song_info[video_title]={
                "youtube_url":youtube_url,
                "song_name": song_name,
                "artist": artist,

                # Add the uri, easy to get the song to put into the playlist
                "spotify_uri": self.get_spotify_uri(song_name, artist)
            }

    # Step 3: Create a new playlist on Spotify
    def create_playlist(self):

        request_body = json.dumps({
            "name": "Youtube Liked Videos",
            "description": "All Liked Youtube Videos",
            "public": True
        })

        query = "https://api.spotify.com/v1/users/{user_id}/playlists".format(self.user_id)
        response = requests.post(
            query,
            data=request_body,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(spotify_token)
            }
        )
        response_json = response.json()

        # playlist id
        return response_json["id"]

    # Step 4: Search for the song
    def get_spotify_uri(self, song_name, artist):

        query = "https://api.spotify.com/v1/search?q=Muse&type=track%2C%20artist&market=Canada&limit=10&offset=5".format(

            song_name,
            artist
        )

        response = requests.post(
            query,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(spotify_token)
            }
        )
        response_json = response.json()
        songs = response_json["tracks"]["items"]

        # Use the first song
        uri = songs[0]["uri"]

        return uri

    # Step 5: Add song to the Spotify playlist
    def add_song_to_playlist(self):
        # Populate our songs dictionary
        self.get_liked_videos()

        # Collect all of the uri
        uris = []
        for song, info in self.all_song_info.items():
            uris.append(info["spotify_uri"])

        # Create a new playlist
        playlist_id = self.create_playlist()

        # Add all songs into the new playlist
        request_data = json.dumps(uris)

        query = "	https://api.spotify.com/v1/playlists/{playlist_id}/tracks".format(playlist_id)

        response = requests.post(
            query,
            data=request_data,
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer {}".format(spotify_token)
            }
        )

        # check for valid response status
        if response.status_code != 200:
            raise ResponseException(response.status_code)

        response_json = response.json()
        return response_json


if __name__ == '__main__':
    cp = CreatePlaylist()
    cp.add_song_to_playlist()