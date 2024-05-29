from flask import Flask, request, Response, render_template, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
import requests
import os
from mutagen import File
from mutagen.mp4 import MP4
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TALB, TPE1, TDRC
from mutagen.oggopus import OggOpus
from io import BytesIO
from urllib.parse import unquote
import webbrowser

from database import initialize_database, get_all_songs
from selenium_handler import initialize_driver, gather_all_song_names, get_song_url

url = "http://localhost:5000"
template_dir = os.path.abspath('./templates2')
app = Flask(__name__, template_folder=template_dir)
socketio = SocketIO(app, async_mode='threading')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/songs')
def songs():
    songs_list = get_all_songs()
    return jsonify(songs=songs_list)

@app.route('/stream')
def stream():
    url = request.args.get('url')
    format = 'audio/mpeg'
    if not url:
        return "URL parameter is missing", 400
    
    print(f"url requested: {url}")

    if url.endswith('.m4a'):
        format = 'audio/mp4'
    elif url.endswith('.opus'):
        format = 'audio/ogg'

    filename = unquote(os.path.basename(url))

    def generate():
        with requests.get(url, stream=True) as r:
            total_size = int(r.headers.get('Content-Length', 0))
            range_header = request.headers.get('Range', None)
            
            temp_file = BytesIO()
            for chunk in r.iter_content(chunk_size=1024):
                temp_file.write(chunk)
            
            temp_file.seek(0)
            audio_file = File(temp_file)

            if isinstance(audio_file, MP3):
                title = audio_file.tags.get('TIT2', filename).text[0] if 'TIT2' in audio_file else filename
                album = audio_file.tags.get('TALB', 'Unknown Album').text[0] if 'TALB' in audio_file else 'Unknown Album'
                artist = audio_file.tags.get('TPE1', 'Unknown Artist').text[0] if 'TPE1' in audio_file else 'Unknown Artist'
                year = audio_file.tags.get('TDRC', 'Unknown Year').text[0] if 'TDRC' in audio_file else 'Unknown Year'
            elif isinstance(audio_file, MP4):
                title = audio_file.tags.get('\xa9nam', [filename])[0]
                album = audio_file.tags.get('\xa9alb', ['Unknown Album'])[0]
                artist = audio_file.tags.get('\xa9ART', ['Unknown Artist'])[0]
                year = audio_file.tags.get('\xa9day', ['Unknown Year'])[0]
            elif isinstance(audio_file, OggOpus):
                title = audio_file.get('title', [filename])[0]
                album = audio_file.get('album', ['Unknown Album'])[0]
                artist = audio_file.get('artist', ['Unknown Artist'])[0]
                year = audio_file.get('date', ['Unknown Year'])[0]
            else:
                title, album, artist, year = filename, 'Unknown Album', 'Unknown Artist', 'Unknown Year'

            metadata = {
                'title': title,
                'album': album,
                'artist': artist,
                'year': year
            }

            if not range_header:
                headers = {
                    'Content-Type': format,
                    'X-Metadata-Title': metadata['title'].encode('utf-8'),
                    'X-Metadata-Album': metadata['album'].encode('utf-8'),
                    'X-Metadata-Artist': metadata['artist'].encode('utf-8'),
                    'X-Metadata-Year': metadata['year'].encode('utf-8')
                }
                return Response(temp_file.getvalue(), headers={k: v.decode('utf-8') for k, v in headers.items()})
            
            start, end = range_header.replace('bytes=', '').split('-')
            start = int(start)
            end = int(end) if end else total_size - 1
            length = end - start + 1
            
            headers = {
                'Content-Type': format,
                'Content-Range': f'bytes {start}-{end}/{total_size}',
                'Accept-Ranges': 'bytes',
                'Content-Length': str(length),
                'X-Metadata-Title': metadata['title'].encode('utf-8'),
                'X-Metadata-Album': metadata['album'].encode('utf-8'),
                'X-Metadata-Artist': metadata['artist'].encode('utf-8'),
                'X-Metadata-Year': metadata['year'].encode('utf-8')
            }

            print("Sending Headers")
            print(headers)
            
            temp_file.seek(start)
            return Response(temp_file.read(length), headers=headers, status=206)

    return generate()

@app.route('/downloads/<filename>')
def serve_file(filename):
    directory = os.path.join(app.root_path, 'downloads')
    return send_from_directory(directory, filename)

def background_task(song_index):
    def callback(song_url):
        if song_url:
            song_url = f"{url}/downloads/{os.path.basename(song_url)}"
        socketio.emit('play_song', {'url': song_url})
    
    get_song_url(song_index, callback)

@socketio.on('play_song')
def handle_play_song(data):
    print("Received play_song event")
    song_index = data['index']
    
    socketio.start_background_task(background_task, song_index)

if __name__ == '__main__':
    initialize_database()
    gather_all_song_names()
    webbrowser.open(url, new=0, autoraise=True)
    socketio.run(app, debug=False)
