import requests
from requests.exceptions import ConnectionError
import time
import os
import threading
import re
import urllib.error
import feedparser
import unidecode

from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.core.virtual import viewport
from luma.led_matrix.device import max7219
from luma.core.legacy import text, show_message
from luma.core.legacy.font import proportional, CP437_FONT, LCD_FONT, SINCLAIR_FONT



serial = spi(port=0, device=0, gpio=noop())
device = max7219(serial, width=32, height=8, block_orientation=-90)
device.contrast(6)
virtual = viewport(device, width=32, height=16)

def start_server():
    try:
        os.chdir('Documents/node-sonos-http-api-master')
    except FileNotFoundError:
        os.chdir('node-sonos-http-api-master')
    os.system('npm start')
    
def get_sonos_data():
    regex = re.compile('npo |radio.*\d|.radio$|qmusic|kink')
    try:
        sonos = requests.get('http://localhost:5005/Woonkamer/state')
        try:
            if re.search(regex, sonos.json()['currentTrack']['artist'].lower()):
                titel = sonos.json()['currentTrack']['artist'] + ': ' + sonos.json()['currentTrack']['title']
                if 'npo radio 2' in sonos.json()['currentTrack']['title'].lower():
                    return sonos.json()['currentTrack']['artist'] + ' ~ '
                else:
                    return titel + ' ~ '
            return sonos.json()['currentTrack']['title'].split('-')[0] + ' - ' + sonos.json()['currentTrack']['artist'].split('•')[0] + ' ~ '
        except KeyError:
            return ''
    except:
        return 'Verbinden met Sonos server... ~ '
    
def get_news():
    nieuws_data = set({'Bezig met nieuws ophalen', 'Bezig boi'})
    try:
        nieuws_data = set()
        koppen = [feedparser.parse('http://feeds.nos.nl/nosnieuwsalgemeen').entries[0:4],
                    feedparser.parse('http://feeds.nos.nl/nosnieuwsbuitenland').entries[0:4]]
        for koppen_lijst in koppen:
            for kop in koppen_lijst:
                if '•' not in kop.title:
                    nieuws_data.add(kop.title)
        return list(nieuws_data), ((len(nieuws_data)//2) + (len(nieuws_data)%2))
    except urllib.error.URLError:
        pass

    
def main():
    time.sleep(5)
    threading.Thread(target=start_server).start()
    while True:
        nieuws, iterations = get_news()
        start = 0
        end = 1
        for i in range(iterations):
            titel = get_sonos_data()
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
            start += 2
            end += 2

if __name__ == '__main__':
    main()
    
