import requests
import time
import os
import threading
import urllib.error
import feedparser
import unidecode
import spotipy
import queue
import RPi.GPIO as GPIO
import sys
from spotipy.oauth2 import SpotifyOAuth
from PIL import Image
from io import BytesIO
from requests.exceptions import ConnectionError

from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.core.virtual import viewport
from luma.led_matrix.device import max7219
from luma.core.legacy import text, show_message
from luma.core.legacy.font import proportional, CP437_FONT, LCD_FONT, SINCLAIR_FONT

   
def get_news():
    nieuws_data = {'Bezig met nieuws ophalen', 'Bezig boii'}
    try:
        koppen = [feedparser.parse('http://feeds.nos.nl/nosnieuwsalgemeen').entries[0:4],
                    feedparser.parse('http://feeds.nos.nl/nosnieuwsbuitenland').entries[0:4]]
        nieuws_data = set()
        for koppen_lijst in koppen:
            for kop in koppen_lijst:
                if '•' not in kop.title:
                    nieuws_data.add(kop.title)
    except urllib.error.URLError:
        pass
    except TypeError:
        pass
    return list(nieuws_data), ((len(nieuws_data)//2) + (len(nieuws_data)%2))
    
    
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
        im.save(size + '.jpg')
        

def get_spotify(scope, new_current):
    while True:
        try:
            current = connect_spotify(scope).current_user_playing_track()
            try:
                if not current['is_playing']:
                    tekst = 'Paused - ' + current['item']['name'].split(' - ')[0] +\
                            ' - ' + current['item']['album']['artists'][0]['name']
                else:
                    tekst = current['item']['name'].split(' - ')[0] + ' - ' + current['item']['album']['artists'][0]['name']
                if current['item']['name'] != new_current:
                    print('nieuw plaatje')
                    get_images(current['item']['album']['images'][0]['url'])
                    new_current = current['item']['name']
            except TypeError:
                new_current = 'empty' 
                tekst = 'Er wordt niks afgespeeld'
        except ConnectionError:
            tekst = 'Geen internet verbinding'
        q.queue.clear()
        q.put(tekst + ' ~ ')
        time.sleep(2)


def get_message(device):
    nieuws, iterations = get_news()
    start = 0
    end = 1
    for i in range(iterations):
        titel = q.get()
        print(titel)
        try:
            nieuws_tekst = titel + nieuws[start] + ' ~ ' + nieuws[end]
        except IndexError:
            nieuws_tekst = titel + nieuws[start]
        try:
            nieuws_tekst = unidecode.unidecode(nieuws_tekst)
            show_message(device, nieuws_tekst, fill='white', font=proportional(LCD_FONT), scroll_delay=0.04)
        except KeyboardInterrupt:
            GPIO.cleanup()
            device.clear()
            sys.exit()
        start += 2
        end += 2
    return

def main():
    global q
    q = queue.Queue()
    serial = spi(port=0, device=0, gpio=noop())
    device = max7219(serial, width=32, height=8, block_orientation=-90)
    device.contrast(6)
    virtual = viewport(device, width=32, height=16)
    threading.Thread(target=get_spotify, args=('user-read-currently-playing', '')).start()
    while True:
        get_message(device)

if __name__ == '__main__':
    main()
    
