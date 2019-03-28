import json
import os
import requests
import urllib
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from os.path import join, dirname

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

spotify_token = os.environ.get("SPOTIFY_TOKEN")
genius_access_token = os.environ.get("GENIUS_TOKEN")

artists_limit = 10

assert spotify_token is not "", "Must declare SPOTIFY_TOKEN env variable"
assert genius_access_token is not "", "Must declare GENIUS_TOKEN env variable"

i = 3
x = set([])
artists = []
topSongs = {}


# Get lyrics from Genius
def downloadLyrics(artistName):
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json',
               'Authorization': 'Bearer ' + genius_access_token}
    r = requests.get("https://api.genius.com/search?q=" + urllib.parse.quote(artistName), headers=headers)
    y = json.loads(r.text)
    if r.status_code != 200:
        print(r.text)
        return -1
    songs = y['response']['hits']
    topSongs[artistName] = {
        'songs': []
    }
    print("* Scrapping songs of " + artistName + " *")
    for song in songs:
        music = song
        title = music['result']['title']
        print(title)
        r = requests.get("https://api.genius.com" + music['result']['api_path'], headers=headers)
        y = json.loads(r.text)
        lyrics = scrap_song_url(y['response']['song']['url'])
        topSongs[artistName]['songs'].append({
            'song': title,
            'lyrics': lyrics
        })
    writeJson(topSongs)


# Get trending french rappers
def getTrendyRappers():
    global artists
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json',
               'Authorization': 'Bearer ' + spotify_token}
    r = requests.get(
        "https://api.spotify.com/v1/playlists/37i9dQZF1DWU4xkXueiKGW/tracks?market=FR&limit=" + str(artists_limit),
        headers=headers)
    y = json.loads(r.text)
    if r.status_code != 200:
        print(r.text)
        return -1
    songs = y['items']
    for song in songs:
        artist = song['track']['artists'][0]['name']
        if "#" in artist:
            print("Invalid " + artist)
        else:
            x.add(artist)
    artists = list(x)


# Get lyrics from Genius
def scrap_song_url(url):
    page = requests.get(url)
    html = BeautifulSoup(page.text, 'html.parser')
    lyrics = html.find('div', class_='lyrics').get_text()
    return lyrics


# Write songs in file
def writeJson(jsonText):
    with open('lyrics.json', 'w') as f:  # writing JSON object
        json.dump(jsonText, f)


def main():
    getTrendyRappers()
    print('** Found rappers **\n' + '\n'.join(artists))
    print('****')
    for artist in artists:
        downloadLyrics(artist)


if __name__ == '__main__':
    main()
