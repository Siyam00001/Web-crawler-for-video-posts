import requests
from bs4 import BeautifulSoup
import os
import time
import re
import json
from urllib.parse import urlparse, urlsplit, urljoin

# Main page URL
main_url = 'mail-url-here-kindly'

# Directory to save videos
base_dir = 'downloaded_videos'
os.makedirs(base_dir, exist_ok=True)

# Progress file to track last page and post
progress_file = 'progress.json'

# Headers for requests
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
}

# Function to sanitize folder/file names
def sanitize(name):
    name = re.sub(r'[^\w-]', '_', name.strip())
    return name if name else 'unnamed'

# Function to extract folder name from URL
def extract_folder_name(url):
    parsed = urlparse(url)
    path = parsed.path.strip('/')
    folder_name = path.split('/')[-1] if path else 'home'
    return sanitize(folder_name)

# Function to get file extension from URL
def get_extension(url):
    path = urlsplit(url).path
    ext = path.split('.')[-1].lower() if '.' in path else 'mp4'
    return ext if ext in ['mp4', 'webm', 'm3u8'] else 'mp4'

# Function to save progress
def save_progress(page_url, post_url=None):
    progress = {
        'last_page': page_url,
        'last_post': post_url
    }
    with open(progress_file, 'w') as f:
        json.dump(progress, f, indent=2)

# Function to load progress
def load_progress():
    if os.path.exists(progress_file):
        with open(progress_file, 'r') as f:
            return json.load(f)
    return {'last_page': main_url, 'last_post': None}

# Function to download a video
def download_video(video_url, save_path):
    # Check if file already exists
    if os.path.exists(save_path):
        print(f'Skipped {save_path} (already downloaded)')
        return
    try:
        response = requests.get(video_url, headers=headers, stream=True, timeout=10)
        response.raise_for_status()
        with open(save_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f'Downloaded {save_path}')
    except requests.RequestException as e:
        print(f'Error downloading {video_url}: {e}')

# Function to get post links from a single page
def get_post_links(page_url):
    try:
        response = requests.get(page_url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        post_links = []
        skip_paths = ['contact-us', 'privacy-policy', 'dmca', 'category']
        for link in soup.find_all('a', href=True):
            url = link['href']
            if not url.startswith('http'):
                url = main_url.rstrip('/') + '/' + url.lstrip('/')
            if (urlparse(url).netloc == urlparse(main_url).netloc and
                '/post/' in url and
                not any(skip in url for skip in skip_paths) and
                'tango' not in url.lower()):
                post_links.append(url)
        return list(set(post_links)), soup
    except requests.RequestException as e:
        print(f'Error fetching page {page_url}: {e}')
        return [], None

# Function to extract video URLs from an individual post page
def get_video_urls(page_url, use_selenium=True):
    video_urls = []
    if use_selenium:
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            options = Options()
            options.headless = True
            options.add_argument('--no-sandbox')
            options.add_argument('--enable-webgl')  # Enable WebGL
            options.add_argument('--use-gl=desktop')  # Use desktop OpenGL
            options.add_argument('--log-level=3')  # Suppress warnings
            options.add_experimental_option('excludeSwitches', ['enable-logging'])  # Suppress devtools logging
            driver = webdriver.Chrome(options=options)
            driver.get(page_url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body'))
            )
            # Attempt to close popups
            try:
                close_buttons = driver.find_elements(By.XPATH, "//button[contains(@class, 'close') or contains(text(), 'Close') or contains(text(), 'X')]")
                for button in close_buttons:
                    button.click()
            except:
                pass

            # Find and process iframes
            iframes = driver.find_elements(By.TAG_NAME, 'iframe')
            for iframe in iframes:
                try:
                    iframe_src = iframe.get_attribute('src')
                    driver.switch_to.frame(iframe)
                    WebDriverWait(driver, 5).until(
                        EC.presence_of_element_located((By.TAG_NAME, 'video'))
                    )
                    video_element = driver.find_element(By.TAG_NAME, 'video')
                    src = video_element.get_attribute('src')
                    if src:
                        if not src.startswith('http'):
                            src = urljoin(iframe_src, src)
                        video_urls.append(src)
                    else:
                        sources = video_element.find_elements(By.TAG_NAME, 'source')
                        for source in sources:
                            src = source.get_attribute('src')
                            if src:
                                if not src.startswith('http'):
                                    src = urljoin(iframe_src, src)
                                video_urls.append(src)
                    driver.switch_to.default_content()
                except Exception as e:
                    print(f'Error processing iframe at {iframe_src}: {e}')
                    driver.switch_to.default_content()
            driver.quit()
        except Exception as e:
            print(f'Error processing page {page_url} with Selenium: {e}')
    else:
        try:
            response = requests.get(page_url, headers=headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            for video in soup.find_all('video'):
                src = video.get('src')
                if src and any(src.endswith(ext) for ext in ['.mp4', '.webm', '.m3u8']):
                    video_urls.append(src)
            for source in soup.find_all('source'):
                src = source.get('src')
                if src and any(src.endswith(ext) for ext in ['.mp4', '.webm', '.m3u8']):
                    video_urls.append(src)
        except requests.RequestException as e:
            print(f'Error fetching page {page_url} with requests: {e}')
    return list(set(video_urls))

# Main process
try:
    # Load progress
    progress = load_progress()
    current_page = progress['last_page']
    last_post = progress['last_post']
    skip_posts = bool(last_post)  # Flag to skip posts until last_post is reached

    page_number = 1 if current_page == main_url else int(current_page.split('/page/')[-1]) if '/page/' in current_page else 1

    while current_page:
        print(f'Fetching page: {current_page}')
        post_links, soup = get_post_links(current_page)
        if not post_links and not soup:
            print(f'No post links found on {current_page}. Moving to next page.')
        else:
            for post_url in post_links:
                # Skip posts until reaching the last processed post
                if skip_posts and post_url != last_post:
                    continue
                # Reset skip_posts after reaching the last processed post
                if skip_posts and post_url == last_post:
                    skip_posts = False
                    continue

                folder_name = extract_folder_name(post_url)
                save_dir = os.path.join(base_dir, folder_name)
                os.makedirs(save_dir, exist_ok=True)

                print(f'Processing post: {post_url}')
                video_urls = get_video_urls(post_url, use_selenium=True)

                if not video_urls:
                    print(f'No videos found on {post_url}')
                else:
                    for i, video_url in enumerate(video_urls, 1):
                        ext = get_extension(video_url)
                        file_name = f"{i:02d}_video.{ext}"
                        save_path = os.path.join(save_dir, file_name)
                        download_video(video_url, save_path)
                        time.sleep(1)

                # Save progress after processing each post
                save_progress(current_page, post_url)
                time.sleep(1)

        # Find next page
        next_page = None
        if soup:
            next_link = soup.find('a', text=re.compile(r'next|older', re.I))
            if next_link and next_link.get('href'):
                next_page = next_link['href']
                if not next_page.startswith('http'):
                    next_page = main_url.rstrip('/') + '/' + next_page.lstrip('/')
            else:
                page_number += 1
                next_page = f'{main_url.rstrip("/")}/page/{page_number}'
                try:
                    response = requests.head(next_page, headers=headers, timeout=5)
                    if response.status_code != 200:
                        next_page = None
                except requests.RequestException:
                    next_page = None

        # Save progress before moving to next page
        save_progress(current_page)
        current_page = next_page
        time.sleep(2)

    print('Download process completed successfully.')
except KeyboardInterrupt:
    print('Script interrupted by user. Progress saved.')
    # Progress is already saved after each post/page
except Exception as e:
    print(f'An unexpected error occurred: {e}')
    print('Progress saved. Please verify the script and website details.')
finally:
    # Clean up progress file if all pages are processed
    if not current_page and os.path.exists(progress_file):
        os.remove(progress_file)
        print(f'Progress file {progress_file} removed as download completed.')