import time

import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from PIL import Image
import requests
from io import BytesIO


def connect_spotify(scope):
    sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=os.getenv('SPOTIFY_CLIENT_ID'),
                                                   client_secret=os.getenv('SPOTIFY_CLIENT_SECRET'),
                                                   redirect_uri='http://localhost:8080',
                                                   scope=scope))
    return sp


def main():
    scope = 'user-read-currently-playing'
    new_current = ''
    new_timestamp = ''
    while True:
        current = connect_spotify(scope).current_user_playing_track()
        try:
            if new_timestamp == current['progress_ms']:
                tekst = 'Paused - ' + current['item']['name'].split(' - ')[0] +\
                        ' - ' + current['item']['album']['artists'][0]['name']
            else:
                tekst = current['item']['name'].split(' - ')[0] + ' - ' + current['item']['album']['artists'][0]['name']
            new_timestamp = current['progress_ms']
            if current['item']['name'] != new_current:
                url = current['item']['album']['images'][0]['url']
                im = Image.open(requests.get(url, stream=True).raw)
                im.save('test.jpg')
                response = requests.get(url)
                image = Image.open(BytesIO(response.content))
                image2 = Image.open(BytesIO(response.content))
                image.thumbnail((32, 32), Image.ANTIALIAS)
                image2.thumbnail((64, 64), Image.ANTIALIAS)
                image.convert('RGB')
                image2.convert('RGB')
                image.save('test2.jpg')
                image2.save('test3.jpg')
                new_current = current['item']['name']
        except TypeError:
            new_current = 'empty'
            tekst = 'Er wordt niks afgespeeld'
        print(tekst)
        time.sleep(2)


if __name__ == '__main__':
    main()
