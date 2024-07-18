### [ GRRIF Tools by Julien 'fetzu' Bono ]
## [ IMPORTS ]
import sys
import argparse
from datetime import date, datetime

## [ CONFIGURATION ]
__version__ = "0.8.2"

## [ Is CLI even cooler with argparse? ]
parser = argparse.ArgumentParser(
    description="A set of tools for Cool Cats™. Allows you to archive GRRIF's play history and scrobble it to last.fm (upcoming)."
)

subparsers = parser.add_subparsers(dest="command")

archive_parser = subparsers.add_parser("archive", help="Archive GRRIF's play history.")
archive_parser.add_argument(
    "destination",
    choices=["print", "db", "txt"],
    help="Specify where to archive the play history (print to stdout, save to SQLite database or to text in YYYY/MM/DD.txt file(s)).",
)
archive_parser.add_argument(
    "from_date",
    nargs="?",
    default="2021-01-01",
    help="Specify the start date for the archive in YYYY-MM-DD format. Defaults to 2021-01-01.",
)
archive_parser.add_argument(
    "to_date",
    nargs="?",
    default=date.today().strftime("%Y-%m-%d"),
    help=f"Specify the start date for the archive in YYYY-MM-DD format. Defaults to today ({date.today().strftime('%Y-%m-%d')}).",
)

stats_parser = subparsers.add_parser(
    "stats", help="Get some stats out of the database."
)
stats_subparsers = stats_parser.add_subparsers(dest="stats_command")
artists_parser = stats_subparsers.add_parser(
    "artists", help="Display stats for artists"
)
artists_parser.add_argument(
    "topofthepop",
    choices=["top10", "top25", "top100"],
    help="Display the top 10, 25 or 100 artists.",
)
artists_parser.add_argument(
    "from_date",
    nargs="?",
    default="2021-01-01",
    help="Specify the start date for the stats in YYYY-MM-DD format. Defaults to 2021-01-01.",
)
artists_parser.add_argument(
    "to_date",
    nargs="?",
    default=date.today().strftime("%Y-%m-%d"),
    help=f"Specify the start date for the stats in YYYY-MM-DD format. Defaults to today ({date.today().strftime('%Y-%m-%d')}).",
)
tracks_parser = stats_subparsers.add_parser("tracks", help="Display stats for tracks")
tracks_parser.add_argument(
    "topofthepop",
    choices=["top10", "top25", "top100"],
    help="Display the top 10, 25 or 100 tracks.",
)
tracks_parser.add_argument(
    "from_date",
    nargs="?",
    default="2021-01-01",
    help="Specify the start date for the stats in YYYY-MM-DD format. Defaults to 2021-01-01.",
)
tracks_parser.add_argument(
    "to_date",
    nargs="?",
    default=date.today().strftime("%Y-%m-%d"),
    help=f"Specify the start date for the stats in YYYY-MM-DD format. Defaults to today ({date.today().strftime('%Y-%m-%d')}).",
)

scrobble_parser = subparsers.add_parser(
    "scrobble",
    help="Scrobble to Last.fm.",
)
scrobble_subparsers = scrobble_parser.add_subparsers(dest="scrobble_command")

settings_parser = scrobble_subparsers.add_parser(
    "settings", help="Set your last.fm scrobbling settings"
)
settings_parser.add_argument(
    "API_KEY",
    type=str,
    help="Your last.fm API Key",
)
settings_parser.add_argument(
    "API_SECRET",
    type=str,
    help="Your last.fm API secret",
)
settings_parser.add_argument(
    "SESSION_KEY",
    type=str,
    help="Your last.fm API session key",
)

livescrobble_parser = scrobble_subparsers.add_parser(
    "start", help="Start scrobbling to last.fm now."
)


stream_parser = subparsers.add_parser(
    "play",
    help="Play GRRIF in your terminal!",
).add_argument(
    "quality",
    choices=["mp3_high", "mp3_low", "aac_high"],
    nargs="?",
    default="mp3_high",
    help="Specify streaming quality (default: mp3_high)",
)

args = parser.parse_args()


## [ MAIN ]
def main():
    print(
        "##########################################\n"
        f"##### [ GRRIF Tools version {__version__} ] ######\n"
        "##########################################\n"
    )

    # Displays argparse's help message if no arguments are given
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    if args.command == "archive" or args.command == "stats":
        # Set the base URL to scrape data from
        BASE_URL = "https://www.grrif.ch/recherche-de-titres/?date={}"

        # Set the date range to scrape data for
        START_DATE = datetime.strptime(args.from_date, "%Y-%m-%d")
        END_DATE = datetime.strptime(args.to_date, "%Y-%m-%d")

    # Archive was passed !
    if args.command == "archive":
        # The "save to SQLite database" option was chosen
        if args.destination == "db":
            # Let the user know what we are attempting
            print(
                f"Attempting to archive plays from {START_DATE.strftime('%Y-%m-%d')} to {END_DATE.strftime('%Y-%m-%d')} to a SQLite database."
            )

            # Import the necessary functions
            from .grrif_archiver import plays_to_db

            # Create/open the database
            plays_to_db(BASE_URL, START_DATE, END_DATE)

        # The "save to text files" option was chosen
        if args.destination == "txt":
            # Let the user know what we are attempting
            print(
                f"Attempting to archive plays from {START_DATE.strftime('%Y-%m-%d')} to {END_DATE.strftime('%Y-%m-%d')} to text files."
            )

            # Import the necessary functions
            from .grrif_archiver import plays_to_txt

            # Create/open the database
            plays_to_txt(BASE_URL, START_DATE, END_DATE)

        # The "output data to stdout" option was chosen
        if args.destination == "print":
            # Let the user know what we are attempting
            print(
                f"Attempting to print plays from {START_DATE.strftime('%Y-%m-%d')} to {END_DATE.strftime('%Y-%m-%d')} to stdout."
            )

            # Import the necessary functions
            from .grrif_archiver import plays_to_stdout

            # Create/open the database
            plays_to_stdout(BASE_URL, START_DATE, END_DATE)

    # Stats was passed !
    if args.command == "stats":
        # Import the necessary functions
        from .grrif_stats import topofthepop

        if args.stats_command == "artists":
            if args.topofthepop == "top10":
                topofthepop("artist", "10", START_DATE, END_DATE)
            if args.topofthepop == "top25":
                topofthepop("artist", "25", START_DATE, END_DATE)
            if args.topofthepop == "top100":
                topofthepop("artist", "100", START_DATE, END_DATE)

        if args.stats_command == "tracks":
            if args.topofthepop == "top10":
                topofthepop("artist, title", "10", START_DATE, END_DATE)
            if args.topofthepop == "top25":
                topofthepop("artist, title", "25", START_DATE, END_DATE)
            if args.topofthepop == "top100":
                topofthepop("title", "100", START_DATE, END_DATE)

    # Scrobble was passed !
    if args.command == "scrobble":

        if args.scrobble_command == "settings":
            if args.API_KEY is not None and args.API_SECRET is not None and args.SESSION_KEY is not None:
                # Write the settings to file
                import os
                current_path = os.path.dirname(os.path.abspath(__file__))
                settings_path = os.path.join(current_path, "grrif_secrets.py")
                settings_content = f"API_KEY = '{args.API_KEY}'\nAPI_SECRET = '{args.API_SECRET}'\nSESSION_KEY = '{args.SESSION_KEY}'\n"
                with open(settings_path, "w") as settings_file:
                    settings_file.write(settings_content)
            else:
                print("Invalid number of arguments passed, API Key, API Secret and Session Key are needed.")

        if args.scrobble_command == "start":
            from .grrif_scrobbler import start_scrobbling
            start_scrobbling("0")

    # Play was passed !
    if args.command == "play":
        from .grrif_player import start_playback
        start_playback(args.quality)
 