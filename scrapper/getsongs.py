import json
import os
import requests
import time
import urllib
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from os.path import join, dirname

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

spotify_token = os.environ.get("SPOTIFY_TOKEN")
genius_access_token = os.environ.get("GENIUS_TOKEN")
artists_limit = os.environ.get("MAX_ARTISTS_SCRAPPING") or 10
assert spotify_token is not "", "Must declare SPOTIFY_TOKEN env variable"
assert genius_access_token is not "", "Must declare GENIUS_TOKEN env variable"
playlists = [
    "37i9dQZF1DX1X23oiQRTB5",
    "37i9dQZF1DWU4xkXueiKGW",
    "37i9dQZF1DWYVURwQHUqnN",
    "37i9dQZF1DX4sJFeoGlF41",
    "37i9dQZF1DWSrqNVMcxGKc"

]
current_milli_time = lambda: int(round(time.time() * 1000))
current_timestamp = ""
topSongs = {}
artistsList = []


# Get lyrics from Genius
def downloadLyrics(rapper):
    rapperName = rapper["name"]
    rapperPopularity = rapper["popularity"]
    rapperFollowers = rapper["followers"]
    rapperImage = rapper["image"]
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json',
               'Authorization': 'Bearer ' + genius_access_token}
    r = requests.get("https://api.genius.com/search?q=" + urllib.parse.quote(rapperName), headers=headers)
    y = json.loads(r.text)
    if r.status_code != 200:
        print(r.text)
        return -1
    songs = y['response']['hits']
    topSongs[rapperName] = {
        'popularity': rapperPopularity,
        'image': rapperImage,
        'followers': rapperFollowers,
        'songs': []
    }
    print("* Scrapping songs of " + rapperName + " *")
    for song in songs:
        music = song
        title = music['result']['title']
        print("- " + title)
        # Fetch song path for given title
        r = requests.get("https://api.genius.com" + music['result']['api_path'], headers=headers)
        y = json.loads(r.text)
        # Get lyrics
        lyrics = scrapeSong(y['response']['song']['url'])
        topSongs[rapperName]['songs'].append({
            'song': title,
            'lyrics': lyrics
        })
    # Append lyrics to file
    writeJson(topSongs)


# Get playlist name for given playlist ID
def getPlaylistName(playlistId):
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json',
               'Authorization': 'Bearer ' + spotify_token}
    r = requests.get(
        "https://api.spotify.com/v1/playlists/" + playlistId + "?market=FR&fields=name",
        headers=headers)
    if r.status_code != 200:
        print(r.text)
        return -1
    return json.loads(r.text)["name"]


# Get artist informations
def getArtistInfos(artistId):
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json',
               'Authorization': 'Bearer ' + spotify_token}
    r = requests.get(
        "https://api.spotify.com/v1/artists/" + artistId,
        headers=headers)
    if r.status_code != 200:
        print(r.text)
        return -1
    return json.loads(r.text)


# Get trending french rappers
def getTrendyRappers(Playlists):
    global artists
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json',
               'Authorization': 'Bearer ' + spotify_token}
    print("\nGet rappers from :")
    # Get all rappers from given playlists
    for playlist in Playlists:
        # Limiting 100 artists per request (Spotify limitations)
        if int(artists_limit) > 100:
            limit = 100
        else:
            limit = int(artists_limit)
        r = requests.get(
            "https://api.spotify.com/v1/playlists/" + playlist + "/tracks?market=FR&limit=" + str(limit),
            headers=headers)
        if r.status_code != 200:
            print(r.text)
            return -1
        y = json.loads(r.text)
        print("- " + getPlaylistName(playlist))
        songs = y['items']
        for song in songs:
            if song["track"] is None:
                continue
            artist = song['track']['artists'][0]['name']
            artistId = song['track']['artists'][0]['id']
            infos = getArtistInfos(artistId)
            if "#" in artist:
                print("Invalid " + artist)
            else:
                if len(artistsList) < int(artists_limit):
                    if not any(d['name'] == artist for d in artistsList):
                        if "image" and "popularity" in infos:
                            if len(infos["images"]) > 0 and len(infos["followers"]) > 0:
                                artistsList.append({
                                    "name": artist,
                                    "popularity": infos["popularity"],
                                    "followers": infos["followers"]["total"],
                                    "image": infos["images"][0]["url"] or None
                                })
                else:
                    print("\n! Limit reached !\n")
                    return -1


# Get lyrics from Genius
def scrapeSong(url):
    page = requests.get(url)
    html = BeautifulSoup(page.text, 'html.parser')
    lyrics = html.find('div', class_='lyrics').get_text()
    return lyrics


# Write songs in file
def writeJson(jsonText):
    global current_timestamp
    with open('../dataset/lyrics-' + str(current_timestamp) + '.json', 'w') as f:  # writing JSON object
        json.dump(jsonText, f)


def main():
    global current_timestamp, playlists
    # Get rappers list
    getTrendyRappers(playlists)
    current_timestamp = current_milli_time()
    numberOfRappers = len(artistsList)
    print('** Found ' + str(numberOfRappers) + ' rappers **')
    for rapper in artistsList:
        print(rapper["name"])
    print('****')
    # Get lyrics of all rappers
    for idx, rapper in enumerate(artistsList):
        print("\n# Progress : " + str(idx + 1) + '/' + str(numberOfRappers) + "\n")
        downloadLyrics(rapper)


if __name__ == '__main__':
    main()
