"""
GRRIF Player helper functions
"""
import os
import requests
import miniaudio
import threading
import time
from .grrif_scrobbler import currently_playing

buffer_file = "buferr.mp3"
max_file_size = 0.25 * 1024 * 1024  # 250 KB
min_play_size = 2 * 1000  # 2 seconds

def stream_and_write(url, file_path, max_size, stop_event):
    response = requests.get(url, stream=True)

    with open(file_path, 'wb') as file:
        buffer = bytearray()
        current_size = 0

        for chunk in response.iter_content(chunk_size=1024):
            if stop_event.is_set():
                break

            buffer.extend(chunk)
            current_size += len(chunk)

            while current_size > max_size:
                buffer.pop(0)
                current_size -= 1024

            file.write(chunk)
            file.flush()

def play_stream(file_path, stop_event):
    print("Buffering...")
    time.sleep(3) # Let the buffer fill up for 3 seconds before playing...

    try:
        stream = miniaudio.stream_file(file_path)

        with miniaudio.PlaybackDevice() as device:
            device.start(stream)
            currently_playing_thread = threading.Thread(target=currently_playing, args=("0", stop_event))
            currently_playing_thread.start()
            input("Streaming. Press the Enter key to stop playback.\n")
            print("Stopping playback, this can take up to 10 seconds.")
    except miniaudio.DecodeError as e:
        print(f"Failed to start streaming: {e}")

    stop_event.set()

def start_playback(quality="mp3_high"):
    stop_event = threading.Event()

    if quality == "mp3_high":
        url = "https://grrif.ice.infomaniak.ch/grrif-high.mp3"
    elif quality == "mp3_low":
        url = "https://grrif.ice.infomaniak.ch/grrif-48.mp3"
    elif quality == "aac_high":
        url = "https://grrif.ice.infomaniak.ch/grrif-128.aac"

    if not os.path.exists(buffer_file):
        open(buffer_file, 'w').close()  # Create an empty file if it doesn't exist
        time.sleep(1) # Give the OS a little time to create the file before writing to it

    stream_thread = threading.Thread(target=stream_and_write, args=(url, buffer_file, max_file_size, stop_event))
    stream_thread.start()

    play_thread = threading.Thread(target=play_stream, args=(buffer_file, stop_event))
    play_thread.start()

    # Wait for both threads to complete
    stream_thread.join()
    play_thread.join()

    # Delete the buffer file
    if os.path.exists(buffer_file):
        os.remove(buffer_file)
