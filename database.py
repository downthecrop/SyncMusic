import sqlite3

class SongInfo:
    def __init__(self, name, page_url, path):
        self.name = name
        self.page_url = page_url
        self.path = path

def initialize_database():
    conn = sqlite3.connect('songs.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS songs (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            page_url TEXT NOT NULL,
            path TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def insert_song(song_info):
    conn = sqlite3.connect('songs.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO songs (name, page_url, path) VALUES (?, ?, ?)', (song_info.name, song_info.page_url, song_info.path))
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
    cursor.execute('SELECT name, path FROM songs')
    songs_list = [{"name": row[0], "path": row[1], "index": idx} for idx, row in enumerate(cursor.fetchall())]
    conn.close()
    return songs_list

def get_song_by_index(song_index):
    conn = sqlite3.connect('songs.db')
    cursor = conn.cursor()
    cursor.execute('SELECT name, page_url, path FROM songs WHERE id = ?', (song_index + 1,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return SongInfo(name=row[0], page_url=row[1], path=row[2])
    else:
        return None

def is_database_initialized():
    conn = sqlite3.connect('songs.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='songs'")
    table_exists = cursor.fetchone() is not None
    if table_exists:
        cursor.execute('SELECT COUNT(*) FROM songs')
        song_count = cursor.fetchone()[0]
        conn.close()
        return song_count > 0
    conn.close()
    return False
