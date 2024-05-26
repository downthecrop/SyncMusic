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

shared_folder_url = "https://ln5.sync.com/dl/eb1076650/dwaa5qe5-dmthb8bm-j2jcjc2c-z4i868ti"
download_directory = "downloads"
max_items_to_collect = 100000000000

if not os.path.exists(download_directory):
    os.makedirs(download_directory)

# Global variable for the Chrome driver
driver = None

def initialize_driver():
    global driver
    if driver is None:
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
    return driver

def fetch_items_in_directory(url, remaining_items, current_path, stack):
    driver = initialize_driver()
    print(f"Fetching items in directory: {url}")
    next_page = True
    page_number = 1
    valid_extensions = {'.mp3', '.m4a', '.wav', '.opus'}

    try:
        while remaining_items > 0 and next_page:
            if page_number > 1:
                if "sync_id=" in url:
                    base_url = url.split("&page=")[0].split("?sync_id=")[0]
                    sync_id = url.split("?sync_id=")[1].split("&")[0]
                    current_url = f"{base_url}?sync_id={sync_id}&page={page_number}"
                else:
                    current_url = f"{url}?page={page_number}"
            else:
                current_url = url

            print(f"Navigating to: {current_url}")
            driver.get(current_url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "list-table"))
            )
            
            rows = driver.find_elements(By.CSS_SELECTOR, "table.list-table tbody tr")
            print(f"Found {len(rows)} rows on page {page_number} of directory")

            for row in rows:
                result = process_row(row, current_url, current_path, valid_extensions)
                if result is not None:
                    if isinstance(result, SongInfo):
                        insert_song(result)
                        remaining_items -= 1
                        print(f"Collected song: {result.name} (remaining items: {remaining_items})")
                        if remaining_items <= 0:
                            break
                    elif isinstance(result, tuple):
                        stack.append(result)
                        print(f"Found directory: {result[1][-1]}, adding to stack.")

            current_page, max_page = extract_current_and_max_from_pagination(driver)
            next_page = current_page < max_page if current_page and max_page else False
            page_number += 1

    except Exception as e:
        print(f"An error occurred while fetching items in directory: Path: {current_path} Remaining Items: {remaining_items} URL: {url} Page: {page_number} {e}")
        print(f"Stacktrace: {e.__traceback__}")

    return remaining_items

def process_row(row, current_url, current_path, valid_extensions):
    try:
        file_name_element = row.find_element(By.CSS_SELECTOR, "td.table-filename span")
        file_type_element = row.find_element(By.TAG_NAME, "img")
        file_id = row.get_attribute("id").replace("sync-id-", "")
        file_name = file_name_element.text
        file_src = file_type_element.get_attribute("src")

        if "sync_id=" in current_url:
            base_url = current_url.split("?sync_id=")[0]
            file_url = f"{base_url}?sync_id={file_id}"
        else:
            file_url = f"{shared_folder_url}/view/default/{file_id}"
        
        if file_src.endswith("mime-audio.svg") or file_src.endswith("mime-unknown.svg"):
            if any(file_name.lower().endswith(ext) for ext in valid_extensions):
                print(f"Found audio file: {file_name} @ url {file_url}")
                return SongInfo(name=file_name, page_url=file_url, path="/".join(current_path))
        elif file_src.endswith("dir.svg"):
            if "sync_id=" in current_url:
                nested_folder_url = f"{base_url}?sync_id={file_id}"
            else:
                nested_folder_url = f"{shared_folder_url}?sync_id={file_id}"
            print(f"Found directory: {file_name}, adding to stack.")
            return (nested_folder_url, current_path + [file_name])
    except Exception as e:
        print(f"Error processing row: {e}")
        print(f"Stacktrace: {e.__traceback__}")
    
    return None

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
        print(f"Stacktrace: {e.__traceback__}")
        return None, None

def gather_all_song_names():
    print("Gathering all song names...")
    song_count = get_song_count()

    if song_count > 0:
        print(f"Song count already at {song_count}, no need to gather more.")
        return
    
    stack = [(shared_folder_url, [])]
    remaining_items = max_items_to_collect

    while stack and remaining_items > 0:
        current_url, current_path = stack.pop()
        print(f"Popped URL from stack: {current_url}")
        remaining_items = fetch_items_in_directory(current_url, remaining_items, current_path, stack)

    print("Finished gathering songs.")

def wait_for_downloads(download_dir):
    print("Waiting for downloads to complete...")
    time.sleep(2)
    while any([filename.endswith('.crdownload') for filename in os.listdir(download_dir)]):
        time.sleep(1)
    print("Downloads complete.")

def download_file(file_name):
    driver = initialize_driver()
    print(f"Downloading file: {file_name}")

    if file_name.endswith('.mp3'):
        # MP3 files have a different page
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[class='col-md-4 col-lg-3'] a[class='showhand tool syncblue']"))
        )
        dlButton = driver.find_element(By.CSS_SELECTOR, "div[class='col-md-4 col-lg-3'] a[class='showhand tool syncblue']")
        dlButton.click()
    else:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "sync-preview-menu[class='hidden-xs'] a[class='showhand tool syncblue']"))
        )
        dlButton = driver.find_element(By.CSS_SELECTOR, "sync-preview-menu[class='hidden-xs'] a[class='showhand tool syncblue']")
        dlButton.click()

    wait_for_downloads(download_directory)
    file_path = os.path.join(download_directory, file_name)
    print(f"Downloaded file to: {file_path}")
    return file_path

def get_song_url(song_index, callback):
    print(f"Getting song URL for index: {song_index}")
    song_info = get_song_by_index(song_index)

    if not song_info:
        print(f"No song found at index: {song_index}")
        callback(None)
        return
    
    song_url = None
    try:
        driver = initialize_driver()
        driver.get(song_info.page_url)
        
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "showhand"))
        )
        
        song_url = download_file(song_info.name)
            
    except Exception as e:
        print(f"An error occurred while getting song URL: {e}")
        print(f"Stacktrace: {e.__traceback__}")
    
    callback(song_url)
