# VPN User Browsing Simulator

Simulate realistic user browsing sessions while connected to **Surfshark VPN**. Each session corresponds to one region — the user manually switches VPN location before the session starts. This script is useful for testing, analytics, or web traffic simulation.

---

## **Features**

- Reads a list of URLs from `all_urls.txt`.  
- Shuffles URLs and partitions them into session chunks.  
- Opens a visible Chrome browser using Selenium.  
- Simulates realistic user behavior:  
  - Scrolls randomly  
  - Moves the mouse slightly  
  - Accepts cookie banners automatically  
  - Reads pages for random durations  
  - Occasionally clicks 1–2 internal links per page  
- Supports multiple regions via manual VPN switching.  
- Logs all activity into `simulate_user_log.txt`.

---

## **Setup**

### 1. Install Python & Libraries

Make sure Python 3.10+ is installed.

```bash
pip install selenium
2. Download ChromeDriver
Check your Chrome version (e.g., 141.0.7390.77).

Download the matching ChromeDriver from Chrome for Testing or your version link.

Extract chromedriver.exe to a folder, e.g., C:\tools\chromedriver.

3. Add ChromeDriver to System PATH (Windows)
Press Win + S, type Environment Variables, click “Edit the system environment variables”.

In System Properties → Advanced → Environment Variables, select Path → Edit → New.

Enter the folder path (e.g., C:\tools\chromedriver).

Open a new terminal and run:

bash
Copy code
chromedriver --version
You should see the version printed.

4. Surfshark VPN
Install Surfshark VPN.

Before each region session, connect manually to the correct region (india, usa, philippines).

Usage
Prepare a file all_urls.txt with one URL per line.

Run the script:

bash
Copy code
python simulate_user.py
Follow the prompts to switch VPN for each region.

Logs will be written to simulate_user_log.txt.

Configuration
REGIONS: List of regions (order matters).

PAGES_PER_SESSION: Number of pages per session.

MIN_READ_SECONDS, MAX_READ_SECONDS: Simulated reading time per page.

MIN_SESSION_MINUTES, MAX_SESSION_MINUTES: Random session duration.

CLICK_INTERNAL_LINKS_PROB: Probability of clicking internal links.

MAX_PAGES_PER_RUN: Safety cap to prevent excessive visits.

How It Works
Shuffles and partitions URLs into session chunks.

For each region:

Prompt user to connect Surfshark VPN.

Launch Chrome via Selenium.

Visit URLs in the chunk while simulating realistic browsing.

Repeat for all regions.

Estimated Runtime
Each session (~30 pages): 20–40 minutes.

Three regions: ~1–1.5 hours, plus VPN switching.

Requirements
Windows or Linux machine

Google Chrome installed

Matching ChromeDriver in PATH

Python 3.10+

Selenium (pip install selenium)

Surfshark VPN account

Contributors / Review
This repository is ready for review. Please check:

Correct setup instructions

Script functionality and safety

Logging and error handling