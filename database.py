import sqlite3

class SongInfo:
    def __init__(self, name, page):
        self.name = name
        self.page = page

def initialize_database():
    conn = sqlite3.connect('songs.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS songs (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            page INTEGER NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def insert_song(song_info):
    conn = sqlite3.connect('songs.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO songs (name, page) VALUES (?, ?)', (song_info.name, song_info.page))
    conn.commit()
    conn.close()

def get_song_count():
    conn = sqlite3.connect('songs.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM songs')
    song_count = cursor.fetchone()[0]
    conn.close()
    return song_count

def get_all_songs():
    conn = sqlite3.connect('songs.db')
    cursor = conn.cursor()
    cursor.execute('SELECT name FROM songs')
    songs_list = [{"name": row[0], "index": idx} for idx, row in enumerate(cursor.fetchall())]
    conn.close()
    return songs_list

def get_song_by_index(song_index):
    conn = sqlite3.connect('songs.db')
    cursor = conn.cursor()
    cursor.execute('SELECT name, page FROM songs WHERE id = ?', (song_index + 1,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return SongInfo(name=row[0], page=row[1])
    else:
        return None
