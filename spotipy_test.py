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


def get_images(url):
    response = requests.get(url)
    sizes = ['640x640', '64x64', '32x32']
    for size in sizes:
        im = Image.open(BytesIO(response.content))
        height = int(size.split('x')[0])
        im.thumbnail((height, height), Image.ANTIALIAS)
        im.convert('RGB')
        im.save(size+'.jpg')


def main():
    scope = 'user-read-currently-playing'
    new_current = ''
    while True:
        current = connect_spotify(scope).current_user_playing_track()
        try:
            if not current['is_playing']:
                tekst = 'Paused - ' + current['item']['name'].split(' - ')[0] +\
                        ' - ' + current['item']['album']['artists'][0]['name']
            else:
                tekst = current['item']['name'].split(' - ')[0] + ' - ' + current['item']['album']['artists'][0]['name']
            if current['item']['name'] != new_current:
                print(current['item']['name'], new_current)
                get_images(current['item']['album']['images'][0]['url'])
                new_current = current['item']['name']
        except TypeError:
            new_current = 'empty'
            tekst = 'Er wordt niks afgespeeld'
        print(tekst)
        time.sleep(2)


if __name__ == '__main__':
    main()
