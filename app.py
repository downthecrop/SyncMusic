from flask import Flask, request, Response, render_template, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import math
import sqlite3
import os
import time

app = Flask(__name__)
socketio = SocketIO(app)

shared_folder_url = "https://ln5.sync.com/dl/a1c3340a0/f9gaxei5-da69twwu-3wxx9hay-8yxcnu79"
driver = None
max_items_to_collect = 100
download_directory = "downloads"

if not os.path.exists(download_directory):
    os.makedirs(download_directory)

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

def fetch_total_items():
    global driver
    try:
        driver.get(shared_folder_url)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "sync-display-pagination"))
        )
        total_items_text = driver.find_element(By.XPATH, '//sync-display-pagination//span[contains(@class, "hide")]')
        number = driver.execute_script("return arguments[0].innerText;", total_items_text)
        total_items = int(number)
        return total_items
    except Exception as e:
        print(f"An error occurred while fetching total items: {e}")
        return 0

def fetch_song_names(page):
    global driver
    song_data = []
    valid_extensions = {'.mp3', '.m4a', '.wav'}

    try:
        url = shared_folder_url if page == 0 else f"{shared_folder_url}?page={page}"
        driver.get(url)
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "list-table"))
        )
        
        rows = driver.find_elements(By.CSS_SELECTOR, "table.list-table tbody tr")
        
        for row in rows:
            if len(song_data) >= max_items_to_collect:
                return song_data
            try:
                file_name_element = row.find_element(By.CSS_SELECTOR, "td.table-filename span")
                file_name = file_name_element.text
                if any(file_name.lower().endswith(ext) for ext in valid_extensions):
                    song_data.append(SongInfo(name=file_name, page=page))
            except Exception as e:
                print(f"Error fetching song name: {e}")
                continue
    except Exception as e:
        print(f"An error occurred while fetching song names on page {page}: {e}")
    
    return song_data

def gather_all_song_names():
    conn = sqlite3.connect('songs.db')
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM songs')
    song_count = cursor.fetchone()[0]
    
    if song_count > 0:
        return

    total_items = fetch_total_items()
    items_per_page = 50
    total_pages = math.ceil(total_items / items_per_page)
    
    for page in range(total_pages + 1):
        if song_count >= max_items_to_collect:
            break
        songs = fetch_song_names(page)
        for song in songs:
            cursor.execute('INSERT INTO songs (name, page) VALUES (?, ?)', (song.name, song.page))
            song_count += 1
            if song_count >= max_items_to_collect:
                break
        conn.commit()
        print(f"Indexing page {page}: total files collected {song_count}")

    conn.close()

def initialize_driver():
    global driver
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--mute-audio")
    prefs = {
        "download.default_directory": os.path.abspath(download_directory),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

def wait_for_downloads(download_dir):
    while any([filename.endswith('.crdownload') for filename in os.listdir(download_dir)]):
        time.sleep(1)

def download_m4a(file_name):
    global driver
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "sync-preview-menu[class='hidden-xs'] a[class='showhand tool syncblue']"))
    )
    dlButton = driver.find_element(By.CSS_SELECTOR, "sync-preview-menu[class='hidden-xs'] a[class='showhand tool syncblue']")
    time.sleep(1)
    dlButton.click()
    time.sleep(1)
    wait_for_downloads(download_directory)
    file_path = os.path.join(download_directory, file_name)
    time.sleep(1)
    return file_path

def get_song_url(song_index, callback):
    global driver
    conn = sqlite3.connect('songs.db')
    cursor = conn.cursor()

    cursor.execute('SELECT name, page FROM songs WHERE id = ?', (song_index + 1,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        callback(None)
        return
    
    song_info = SongInfo(name=row[0], page=row[1])
    
    song_url = None
    try:
        url = shared_folder_url if song_info.page == 0 else f"{shared_folder_url}?page={song_info.page}"
        driver.get(url)
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "list-table"))
        )
        
        rows = driver.find_elements(By.CSS_SELECTOR, "table.list-table tbody tr")
        
        for row in rows:
            file_name_element = row.find_element(By.CSS_SELECTOR, "td.table-filename span")
            if file_name_element.text == song_info.name:
                driver.execute_script("arguments[0].scrollIntoView();", file_name_element)
                file_name_element.click()
                
                if song_info.name.lower().endswith('.mp3'):
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, "video"))
                    )
                    
                    video_element = driver.find_element(By.TAG_NAME, "video")
                    song_url = video_element.get_attribute("src")
                
                elif song_info.name.lower().endswith('.m4a'):
                    song_url = download_m4a(song_info.name)
                
                driver.execute_script("window.history.go(-1)")
                
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "list-table"))
                )
                break
    except Exception as e:
        print(f"An error occurred while getting song URL: {e}")
    
    callback(song_url)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/songs')
def songs():
    conn = sqlite3.connect('songs.db')
    cursor = conn.cursor()

    cursor.execute('SELECT name FROM songs')
    songs_list = [{"name": row[0], "index": idx} for idx, row in enumerate(cursor.fetchall())]
    
    conn.close()
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

    def generate():
        with requests.get(url, stream=True) as r:
            total_size = int(r.headers.get('Content-Length', 0))
            range_header = request.headers.get('Range', None)
            if not range_header:
                headers = {'Content-Type': format}
                return Response(r.iter_content(chunk_size=1024), headers=headers)
            
            start, end = range_header.replace('bytes=', '').split('-')
            start = int(start)
            end = int(end) if end else total_size - 1
            length = end - start + 1
            
            headers = {
                'Content-Type': format,
                'Content-Range': f'bytes {start}-{end}/{total_size}',
                'Accept-Ranges': 'bytes',
                'Content-Length': str(length)
            }
            
            r = requests.get(url, headers={'Range': f'bytes={start}-{end}'}, stream=True)
            return Response(r.iter_content(chunk_size=1024), headers=headers, status=206)

    return generate()



@app.route('/downloads/<filename>')
def serve_file(filename):
    directory = os.path.join(app.root_path, 'downloads')
    return send_from_directory(directory, filename)


def background_task(song_index):
    def callback(song_url):
        if song_url and song_url.endswith('.m4a'):
            song_url = f"http://localhost:5000/downloads/{os.path.basename(song_url)}"
        socketio.emit('play_song', {'url': song_url})
    
    get_song_url(song_index, callback)



@socketio.on('play_song')
def handle_play_song(data):
    print("Received play_song event")
    song_index = data['index']
    
    socketio.start_background_task(background_task, song_index)

if __name__ == '__main__':
    initialize_database()
    initialize_driver()
    gather_all_song_names()
    socketio.run(app, debug=True)
