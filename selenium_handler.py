from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import math
import os
import time

from database import insert_song, get_song_count, get_song_by_index, SongInfo

shared_folder_url = "https://ln5.sync.com/dl/a1c3340a0/f9gaxei5-da69twwu-3wxx9hay-8yxcnu79"
download_directory = "downloads"
max_items_to_collect = 100
driver = None

if not os.path.exists(download_directory):
    os.makedirs(download_directory)

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
    song_count = get_song_count()
    
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
            insert_song(song)
            song_count += 1
            if song_count >= max_items_to_collect:
                break
        print(f"Indexing page {page}: total files collected {song_count}")

def wait_for_downloads(download_dir):
    time.sleep(2)
    while any([filename.endswith('.crdownload') for filename in os.listdir(download_dir)]):
        time.sleep(1)

def download_m4a(file_name):
    global driver
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "sync-preview-menu[class='hidden-xs'] a[class='showhand tool syncblue']"))
    )
    dlButton = driver.find_element(By.CSS_SELECTOR, "sync-preview-menu[class='hidden-xs'] a[class='showhand tool syncblue']")
    dlButton.click()
    wait_for_downloads(download_directory)
    file_path = os.path.join(download_directory, file_name)
    return file_path

def download_mp3(file_name):
    global driver
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div[class='col-md-4 col-lg-3'] a[class='showhand tool syncblue']"))
    )
    dlButton = driver.find_element(By.CSS_SELECTOR, "div[class='col-md-4 col-lg-3'] a[class='showhand tool syncblue']")
    dlButton.click()
    wait_for_downloads(download_directory)
    file_path = os.path.join(download_directory, file_name)
    return file_path


def get_song_url(song_index, callback):
    global driver
    song_info = get_song_by_index(song_index)

    if not song_info:
        callback(None)
        return
    
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
                    song_url = download_mp3(song_info.name)
                
                elif song_info.name.lower().endswith('.m4a'):
                    song_url = download_m4a(song_info.name)
                break
    except Exception as e:
        print(f"An error occurred while getting song URL: {e}")
    
    callback(song_url)
