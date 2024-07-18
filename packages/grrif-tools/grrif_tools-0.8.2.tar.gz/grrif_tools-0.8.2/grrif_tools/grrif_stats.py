"""
GRRIF Stats helper functions
"""

import os
import sqlite3
from .grrif_archiver import database_handler

# connect to the SQLite database
database_path = database_handler()
conn = sqlite3.connect(database_path)


def topofthepop(category, ntop, start_date, end_date):
    # Let's cook up a nice query
    query = f"""
    SELECT {category}, COUNT(*) as plays
    FROM plays
    WHERE date BETWEEN ? AND ?
    GROUP BY {category}
    ORDER BY plays DESC
    LIMIT {ntop}
    """
    params = (start_date, end_date)
    results = conn.execute(query, params)

    # print the results for artists
    if category == "artist":
        for row in results:
            print(f"{row[0]} ({row[1]})")
    elif category == "artist, title":
        for row in results:
            print(f"{row[0]} - {row[1]} ({row[2]})")
    # close the database connection
    conn.close()
