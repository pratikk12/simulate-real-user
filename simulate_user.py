"""
Simulate realistic user browsing sessions while connected to Surfshark VPN.
Each session corresponds to one region — user manually switches VPN location before session starts.
"""

import time
import random
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import WebDriverException
from urllib.parse import urlparse

# ---------- CONFIG ----------
ALL_URLS_FILE = "all_urls.txt"
LOG_FILE = "simulate_user_log.txt"
CHROME_DRIVER_PATH = "chromedriver"  # if in PATH

# Regions to simulate (order matters)
REGIONS = ["india", "usa", "philippines"]

PAGES_PER_SESSION = 30
MIN_READ_SECONDS = 10
MAX_READ_SECONDS = 60
MIN_SESSION_MINUTES = 20
MAX_SESSION_MINUTES = 40

MIN_DELAY_BETWEEN_PAGES = 2
MAX_DELAY_BETWEEN_PAGES = 6

USE_MOUSE_MOVE = True
CLICK_INTERNAL_LINKS_PROB = 0.3
ACCEPT_COOKIES = True
MAX_PAGES_PER_RUN = 2000

# ----------------------------

logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format="%(asctime)s %(message)s")
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger("").addHandler(console)

def read_urls(file_path):
    urls = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            u = line.strip()
            if u:
                urls.append(u)
    return urls

def make_options(user_agent=None):
    opts = Options()
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--start-maximized")
    if user_agent:
        opts.add_argument(f"--user-agent={user_agent}")
    return opts

def random_user_agent():
    uas = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16 Safari/605.1.15",
        "Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119 Mobile Safari/537.36",
    ]
    return random.choice(uas)

def move_mouse_random(driver):
    try:
        actions = ActionChains(driver)
        actions.move_by_offset(random.randint(50, 300), random.randint(50, 300)).perform()
        time.sleep(random.uniform(0.2, 0.8))
    except Exception:
        pass

def try_accept_cookies(driver):
    if not ACCEPT_COOKIES:
        return
    try:
        btns = driver.find_elements(By.XPATH, "//button[contains(., 'Accept') or contains(., 'Agree') or contains(., 'Allow')]")
        if btns:
            btns[0].click()
            logging.info("Clicked cookie button")
            time.sleep(1)
    except Exception:
        pass

def get_internal_links_on_page(driver, domain):
    links = []
    try:
        elems = driver.find_elements(By.XPATH, f"//a[contains(@href, '{domain}')]")
        for e in elems:
            href = e.get_attribute("href")
            if href and href.startswith("http"):
                links.append(href)
    except Exception:
        pass
    return list(dict.fromkeys(links))

def visit_pages_with_browser(urls, session_minutes):
    opts = make_options(random_user_agent())
    try:
        driver = webdriver.Chrome(CHROME_DRIVER_PATH, options=opts)
    except WebDriverException as e:
        logging.error(f"Chrome start failed: {e}")
        return 0, len(urls)

    visited = 0
    failures = 0
    domain = urlparse(urls[0]).netloc if urls else None
    end_time = time.time() + (session_minutes * 60)

    try:
        for url in urls:
            if time.time() > end_time:
                logging.info("Session time finished.")
                break

            try:
                logging.info(f"Opening: {url}")
                driver.get(url)
                time.sleep(random.uniform(2, 4))
                try_accept_cookies(driver)

                if USE_MOUSE_MOVE:
                    move_mouse_random(driver)

                for _ in range(random.randint(2, 6)):
                    driver.execute_script("window.scrollBy(0, window.innerHeight * 0.6);")
                    time.sleep(random.uniform(1, 3))

                if random.random() < CLICK_INTERNAL_LINKS_PROB:
                    links = get_internal_links_on_page(driver, domain)
                    if links:
                        pick = random.choice(links)
                        logging.info(f"Clicking internal link: {pick}")
                        driver.get(pick)
                        time.sleep(random.uniform(3, 6))
                        driver.back()

                read_t = random.uniform(MIN_READ_SECONDS, MAX_READ_SECONDS)
                logging.info(f"Reading for {read_t:.1f}s")
                time.sleep(read_t)
                visited += 1

            except Exception as e:
                logging.error(f"Failed visiting {url}: {e}")
                failures += 1

            time.sleep(random.uniform(MIN_DELAY_BETWEEN_PAGES, MAX_DELAY_BETWEEN_PAGES))

            if visited + failures >= MAX_PAGES_PER_RUN:
                logging.info("Reached MAX_PAGES_PER_RUN, stopping.")
                break
    finally:
        driver.quit()

    elapsed = int((session_minutes * 60) - (end_time - time.time()))
    logging.info(f"Session done: visited={visited}, failures={failures}, duration≈{elapsed}s")
    return visited, failures

def partition_urls(urls, chunk_size):
    return [urls[i:i + chunk_size] for i in range(0, len(urls), chunk_size)]

def main():
    all_urls = read_urls(ALL_URLS_FILE)
    if not all_urls:
        logging.error("No URLs found.")
        return

    random.shuffle(all_urls)
    chunks = partition_urls(all_urls, PAGES_PER_SESSION)

    for region in REGIONS:
        print(f"\n🌍 Connect Surfshark VPN to region: {region.upper()}")
        input("Press Enter once connected... ")

        urls = chunks.pop(0) if chunks else []
        session_minutes = random.uniform(MIN_SESSION_MINUTES, MAX_SESSION_MINUTES)
        logging.info(f"Starting session for {region} (~{session_minutes:.1f} min, {len(urls)} pages)")
        visit_pages_with_browser(urls, session_minutes)

        wait = random.uniform(30, 120)
        logging.info(f"Sleeping {wait:.1f}s before next region...")
        time.sleep(wait)

    logging.info("All VPN region sessions finished.")

if __name__ == "__main__":
    main()
