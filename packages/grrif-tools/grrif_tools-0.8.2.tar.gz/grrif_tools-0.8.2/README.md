# GRRIF Tools

A set of tools for Cool Cats™. Allows you to archive GRRIF's play history to a SQLite database (or text files), compute/display some stats (top 10/25/100 artists and tracks), stream the radio live in your console, and scrobble it to last.fm.

```
usage: grrif_tools [-h] {archive,stats,scrobble} ...

A set of tools for Cool Cats™. Allows you to archive GRRIF's play history and scrobble it to last.fm (upcoming).

positional arguments:
  {archive,stats,scrobble}
    archive             Archive GRRIF's play history.
    stats               Get some stats out of the database.
    play                Streams GRRIF to the console and displays the currently playing track.
    scrobble            Scrobble to Last.fm.

options:
  -h, --help            show this help message and exit
  ```
  
  **NOTE:** This package is unofficial and meant mostly as a playground to experiment with some new things (argparse, python packaging, etc...). Please do not DDoS GRRIF's website !  
  **NOTE2:** Last.fm scrobbling is working and active while either streaming ("play") or using "scrobble start". This library will not handle authentification and requires some manual setup for last.fm's API access. Please create your own app on last.fm (https://www.last.fm/api/account/create) to get your API_KEY and API_SECRET, and see https://www.last.fm/api/authspec on how to get your SESSION_KEY (hint: it involves getting a token first and some md5 hashing).
