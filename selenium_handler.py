from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import os
import time

from database import insert_song, get_song_count, get_song_by_index, SongInfo, initialize_database


# "https://ln5.sync.com/dl/b3a6f5250/x4cguzja-4n3zaxuh-7dyny46b-x2atc84i" # Full
# "https://ln5.sync.com/dl/a1c3340a0/f9gaxei5-da69twwu-3wxx9hay-8yxcnu79" # iPhone
shared_folder_url = "https://ln5.sync.com/dl/a1c3340a0/f9gaxei5-da69twwu-3wxx9hay-8yxcnu79"
download_directory = "downloads"
max_items_to_collect = 1000
driver = None

mime_audio = "images/icons/mime-audio.svg"
mime_directory = "images/icons/dir.svg"

if not os.path.exists(download_directory):
    os.makedirs(download_directory)

def initialize_driver():
    global driver
    print("Initializing the Chrome driver...")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--mute-audio")
    chrome_options.add_argument("--log-level=3")
    prefs = {
        "download.default_directory": os.path.abspath(download_directory),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    chrome_options.add_experimental_option("prefs", prefs)
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    print("Chrome driver initialized.")

class Item:
    def __init__(self, name, type, url, path):
        self.name = name
        self.type = type
        self.url = url
        self.path = path

def fetch_items_in_directory(url, remaining_items, current_path):
    global driver
    items = []
    next_page = True
    page_number = 0

    try:
        while remaining_items > 0 and next_page:
            current_url = f"{url}?page={page_number}" if page_number > 0 else url
            print(f"Navigating to directory: {current_url}")
            driver.get(current_url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "list-table"))
            )
            
            rows = driver.find_elements(By.CSS_SELECTOR, "table.list-table tbody tr")

            current_page, max_page = extract_current_and_max_from_pagination(driver)

            print(f"Found {len(rows)} rows on page {page_number} total elements in directory {max_page}")

            for index in range(len(rows)):
                if remaining_items <= 0:
                    print("Reached max items to collect, breaking.")
                    break

                try:
                    print(f"Fetching row {index + 1} of {len(rows)}")
                    rows = driver.find_elements(By.CSS_SELECTOR, "table.list-table tbody tr")
                    row = rows[index]
                    
                    file_name_element = row.find_element(By.CSS_SELECTOR, "td.table-filename span")
                    file_type_element = row.find_element(By.TAG_NAME, "img")
                    file_name = file_name_element.text
                    file_src = file_type_element.get_attribute("src")
                    
                    print(f"Found file: {file_name}")
                    
                    driver.execute_script("arguments[0].focus();", file_name_element)
                    driver.execute_script("arguments[0].click();", file_name_element)
                    
                    file_url = driver.current_url
                    items.append(Item(file_name, file_src, file_url, current_path))
                    
                    print(f"Fetched file URL: {file_url}")
                    
                    driver.get(current_url)
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "list-table"))
                    )

                except Exception as e:
                    print(f"Error fetching item at index {index}: {e}")
                    continue

            # Check if there are more pages
            current_page, max_page = extract_current_and_max_from_pagination(driver)
            next_page = current_page < max_page if current_page and max_page else False
            page_number += 1

    except Exception as e:
        print(f"An error occurred while fetching items in directory: {e}")

    return items

def depth_first_search(url):
    print(f"Starting depth-first search from URL: {url}")
    stack = [(url, [])]
    song_data = []
    valid_extensions = {'.mp3', '.m4a', '.wav'}
    remaining_items = max_items_to_collect

    while stack and remaining_items > 0:
        current_url, current_path = stack.pop()
        print(f"Popped URL from stack: {current_url}")
        items = fetch_items_in_directory(current_url, remaining_items, current_path)

        for item in items:
            if item.type.endswith(mime_audio):
                if any(item.name.lower().endswith(ext) for ext in valid_extensions):
                    print(f"Found audio file: {item.name}")
                    song_data.append(SongInfo(name=item.name, page_url=item.url, path="/".join(current_path)))
                    remaining_items -= 1
                    if remaining_items <= 0:
                        print("Reached max items to collect, breaking.")
                        break
            elif item.type.endswith(mime_directory):
                print(f"Found directory: {item.name}, adding to stack.")
                stack.append((item.url, current_path + [item.name]))

    return song_data

def get_song_url(song_index, callback):
    global driver
    print(f"Getting song URL for index: {song_index}")
    song_info = get_song_by_index(song_index)

    if not song_info:
        print(f"No song found at index: {song_index}")
        callback(None)
        return
    
    song_url = None
    try:
        driver.get(song_info.page_url)
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "showhand"))
        )
        
        if song_info.name.lower().endswith('.mp3'):
            song_url = download_mp3(song_info.name)
        
        elif song_info.name.lower().endswith('.m4a'):
            song_url = download_m4a(song_info.name)
            
    except Exception as e:
        print(f"An error occurred while getting song URL: {e}")
    
    callback(song_url)

def wait_for_downloads(download_dir):
    print("Waiting for downloads to complete...")
    time.sleep(2)
    while any([filename.endswith('.crdownload') for filename in os.listdir(download_dir)]):
        time.sleep(1)
    print("Downloads complete.")

def extract_current_and_max_from_pagination(driver):
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "sync-display-pagination"))
        )
        
        pagination_element = driver.find_element(By.CSS_SELECTOR, "sync-display-pagination")
        spans = pagination_element.find_elements(By.CSS_SELECTOR, "span span")
        
        numbers = [span.text for span in spans if span.text.isdigit()]
        
        max_value = numbers[-1] if numbers else None
        current = numbers[-2] if len(numbers) > 1 else max_value
        
        return int(current), int(max_value)
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return None, None

def download_m4a(file_name):
    global driver
    print(f"Downloading M4A file: {file_name}")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "sync-preview-menu[class='hidden-xs'] a[class='showhand tool syncblue']"))
    )
    dlButton = driver.find_element(By.CSS_SELECTOR, "sync-preview-menu[class='hidden-xs'] a[class='showhand tool syncblue']")
    dlButton.click()
    wait_for_downloads(download_directory)
    file_path = os.path.join(download_directory, file_name)
    print(f"Downloaded M4A file to: {file_path}")
    return file_path

def download_mp3(file_name):
    global driver
    print(f"Downloading MP3 file: {file_name}")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "div[class='col-md-4 col-lg-3'] a[class='showhand tool syncblue']"))
    )
    dlButton = driver.find_element(By.CSS_SELECTOR, "div[class='col-md-4 col-lg-3'] a[class='showhand tool syncblue']")
    dlButton.click()
    wait_for_downloads(download_directory)
    file_path = os.path.join(download_directory, file_name)
    print(f"Downloaded MP3 file to: {file_path}")
    return file_path

def gather_all_song_names():
    print("Gathering all song names...")
    song_count = get_song_count()

    if song_count > 0:
        print(f"Song count already at {song_count}, no need to gather more.")
        return
    
    song_data = depth_first_search(shared_folder_url)

    for song in song_data:
        insert_song(song)
        song_count += 1
        print(f"Inserted song: {song.name}, total count: {song_count}")
        if song_count >= max_items_to_collect:
            print("Reached maximum items to collect, stopping.")
            break
    print("Finished gathering songs.")
    print(song_data)
