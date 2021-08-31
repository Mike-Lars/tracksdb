import xml.etree.ElementTree as ET
import sqlite3

# Establish connection to db
conn = sqlite3.connect('tracksdb.sqlite')
cur = conn.cursor()

# Configure db
cur.executescript('''
DROP TABLE IF EXISTS Artist;
DROP TABLE IF EXISTS Album;
DROP TABLE IF EXISTS Track;

CREATE TABLE Artist (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    name TEXT UNIQUE
);

CREATE TABLE Album (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    title TEXT UNIQUE,
    artist_id INTEGER
);

CREATE TABLE Track (
    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    title TEXT UNIQUE,
    album_id INTEGER,
    rating INTEGER,
    len INTEGER,
    count INTEGER
);
''')

# Read iTunes XML file
fname = input('Enter a file name: ')
if len(fname) < 1: fname = 'Library.xml'

# Define function to lookup specific keys in each dictionary (done for variable assignment in for loop below)
def lookup(d, key):
    found = False
    for child in d:
        if found: return child.text
        if child.tag == 'key' and child.text == key:
            found = True
    return None

# Create an XML ElementTree object and find the dictionaries that represent individual tracks
stuff = ET.parse(fname)
all = stuff.findall('dict/dict/dict')
print('Dict count:', len(all))

# Iterate through tracks, assign key information to variables, and continue past tracks with no name, artist, or album
for entry in all:
    if lookup(entry, 'Track ID') is None: continue
    
    name = lookup(entry, 'Name')
    artist = lookup(entry, 'Artist')
    album = lookup(entry, 'Album')
    count = lookup(entry, 'Play Count')
    rating = lookup(entry, 'Rating')
    length = lookup(entry, 'Total Time')

    if name is None or artist is None or album is None: continue
    
    print(name, artist, album, count, rating, length)
    
    # Populate the Artist, Album, and Track tables with INSERT statements
    cur.execute('''INSERT OR IGNORE INTO Artist (name) VALUES (?)''', (artist,))
    cur.execute('''SELECT id FROM Artist WHERE name = ?''', (artist,))
    artist_id = cur.fetchone()[0]
    
    cur.execute('''INSERT OR IGNORE INTO Album (title, artist_id) VALUES (?, ?)''', (album, artist_id))
    cur.execute('''SELECT id FROM Album WHERE title = ?''', (album,))
    album_id = cur.fetchone()[0]
    
    cur.execute('''INSERT OR REPLACE INTO Track (title, album_id, len, rating, count) VALUES (?,?,?,?,?)''', (name, album_id, length, rating, count))
    
    # Save to disk after each track
    conn.commit()
    
    
    
### SELECT Statement to view the user's TOP 10 tracks ###

# SELECT Track.title, Artist.name, Album.title, Track.count
# FROM Track JOIN Album JOIN Artist
# ON Track.album_id=Album.id AND Album.Artist_id=Artist.id
# ORDER BY Track.count DESC LIMIT 10
