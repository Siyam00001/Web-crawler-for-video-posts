# Video Downloader Script

## Description
This Python script automates the process of scraping and downloading videos from a specified website. It navigates through the website's pages, extracts video URLs from individual posts, and saves the videos to organized directories. The script includes progress tracking to resume downloads and handles both static and dynamic content using requests and Selenium.

> **Note:** This tool is intended for educational purposes only. Ensure compliance with the website's terms of service and applicable laws before using it.

## Features
- **Web Scraping:** Extracts video URLs using BeautifulSoup for static content and Selenium for dynamic content.
- **Progress Tracking:** Saves the last processed page and post to a JSON file, allowing resumption of downloads.
- **Organized Storage:** Saves videos in directories named based on post URLs, with sanitized folder and file names.
- **Error Handling:** Robust handling of network errors, missing videos, and interruptions, with progress saved on exit.
- **Customizable:** Easily configurable main URL, save directory, and headers.

## Requirements
- **Python Version:** Python 3.8+
- **Required Python Packages:** `requests`, `beautifulsoup4`, `selenium` (install via `pip install -r requirements.txt`)
- **Selenium WebDriver:** Requires ChromeDriver compatible with your installed Chrome browser.
- **Google Chrome:** Must be installed for Selenium to work.

## Installation
```sh
# Clone the repository
git clone https://github.com/your-username/video-downloader.git
cd video-downloader

# Install dependencies
pip install -r requirements.txt
```

### Ensure ChromeDriver is Installed
1. Download ChromeDriver matching your Chrome version from [here](https://chromedriver.chromium.org/downloads).
2. Add ChromeDriver to your system PATH or place it in the project directory.

### Update the Main URL in the Script
Replace `'mail-url-here-kindly'` with the target website URL.

## Usage
```sh
python video_downloader.py
```

### Script Actions
- Creates a `downloaded_videos` directory to store videos.
- Navigates through the website's pages, extracts video URLs, and downloads videos.
- Saves progress to `progress.json` for resumption after interruptions.
- Automatically removes `progress.json` upon completion.

### Interrupting the Script
Press `Ctrl+C` to stop execution. Progress is saved automatically.

## Configuration
- **Main URL:** Set `main_url` to the website's homepage or starting page.
- **Save Directory:** Modify `base_dir` to change where videos are stored.
- **Headers:** Update `headers` for custom User-Agent or other HTTP headers.
- **Selenium:** Set `use_selenium=False` in `get_video_urls` to disable Selenium (for static sites only).

## File Structure
```
video-downloader/
├── video_downloader.py  # Main script
├── downloaded_videos/   # Directory for downloaded videos
├── progress.json        # Temporary file for progress tracking
├── requirements.txt     # Python dependencies
└── README.md            # This file
```

## Notes
- **Dynamic Content:** Selenium handles JavaScript-rendered content. Ensure Chrome and ChromeDriver compatibility.
- **Website Structure:** Assumes posts contain `/post/` in URLs and videos are in `<video>` tags or iframes. Modify parsing logic if necessary.
- **Rate Limiting:** Includes `time.sleep` to avoid overwhelming the server. Adjust delays if needed.
- **Legal Considerations:** Ensure compliance with the website's terms of service and applicable laws before downloading content.

## Troubleshooting
- **Selenium Errors:** Verify ChromeDriver version matches Chrome. Check PATH or specify ChromeDriver path in the script.
- **No Videos Found:** Ensure the website uses `<video>` tags or iframes for videos. Disable Selenium for static sites.
- **Network Issues:** Check internet connection or increase timeout values in `requests.get`.
- **Progress Not Resuming:** Verify `progress.json` exists and contains valid JSON.


## Disclaimer
This script is for **educational purposes only**. Respect website terms of service and copyright laws when downloading content. The author is not responsible for misuse of this tool.

