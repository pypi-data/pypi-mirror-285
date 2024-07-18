import requests
import time
import titlecase

from grrif_secrets import API_KEY, API_SECRET, SESSION_KEY

artist = ""
title = ""

def hashRequest(obj, secretKey):
    """
    Lifted from https://github.com/bretsky/lastfm-scrobbler/blob/master/lastpy/__init__.py
    MIT License
    Copyright (c) 2019 Noah Huber-Feely
    """
    import hashlib

    string = ''
    items = list(obj.keys())
    items.sort()
    for i in items:
        string += i
        string += obj[i]
    string += secretKey
    stringToHash = string.encode('utf8')
    requestHash = hashlib.md5(stringToHash).hexdigest()
    return requestHash

def scrobble_track(artist, track, timestamp):
    """
    Crafts and sends a POST request to Last.fm's API to scrobble a track.
    """
    url = "http://ws.audioscrobbler.com/2.0/"

    params = {
        "method": "track.scrobble",
        "api_key": API_KEY,
        "artist": artist,
        "chosenByUser": "0",
        "sk": SESSION_KEY,
        "timestamp": str(timestamp),
        "track": track,
        }

    reqhash = hashRequest(params, API_SECRET)
    params["api_sig"] = reqhash

    response = requests.post(url, params=params)

    if response.status_code == 200:
        print("Track scrobbled successfully!")
    else:
        print("Failed to scrobble track.")

def currently_playing(ctime, stop_event):
    """
    Scrobble while streaming from the console (multi-threading coord)
    """
    while not stop_event.is_set():
        start_scrobbling(ctime)

def start_scrobbling(ctime):
    """
    Function to get the currently playing track (every 60 seconds).
    """
    while True:
        response = requests.get("https://www.grrif.ch/live/covers.json")

        # Check if the request was successful
        if response.status_code == 200:
            ltime = response.json()[3].get("Hours")
            if ctime == 0 or ctime != ltime:
                data = response.json()[3]
                title = titlecase.titlecase(data.get("Title"))
                artist = titlecase.titlecase(data.get("Artist"))
                ctime = ltime
                utctime = int(int(time.time() - 30))
                print(f"Currently playing {title} by {artist}.")
                scrobble_track(artist, title, utctime)
            else:
                pass
        else:
            print("Failed to retrieve data from the URL.")

        time.sleep(60)
