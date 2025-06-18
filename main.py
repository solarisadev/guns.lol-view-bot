import concurrent.futures
import random
import colorama
import cloudscraper
import logging
from queue import Queue
from threading import Lock

# Initialize colorama and logging
colorama.init()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Get username
url = input("Your guns.lol username > ")

# Headers configuration
headers = {
    "accept": "*/*",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "no-cache",
    "content-length": "0",
    "origin": "https://guns.lol",
    "pragma": "no-cache",
    "priority": "u=1, i",
    "referer": f"https://guns.lol/{url}",
    "sec-ch-ua": '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
    "sec-ch-ua-arch": '"x86"',
    "sec-ch-ua-bitness": '"64"',
    "sec-ch-ua-full-version": '"126.0.6478.127"',
    "sec-ch-ua-full-version-list": '"Not/A)Brand";v="8.0.0.0", "Chromium";v="126.0.6478.127", "Google Chrome";v="126.0.6478.127"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-model": '""',
    "sec-ch-ua-platform": '"Windows"',
    "sec-ch-ua-platform-version": '"15.0.0"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "username": url
}

class ViewBot:
    def __init__(self):
        self.views = 0
        self.views_lock = Lock()
        self.proxy_queue = Queue()
        self.load_proxies()

    def load_proxies(self):
        """Load proxies from file into queue"""
        try:
            with open("proxies.txt", "r") as f:
                proxies = [f"http://{proxy.strip()}" for proxy in f if proxy.strip()]
                random.shuffle(proxies)
                for proxy in proxies:
                    self.proxy_queue.put(proxy)
            logging.info(f"Loaded {self.proxy_queue.qsize()} proxies")
        except FileNotFoundError:
            logging.error("proxies.txt not found.")
            raise
        except Exception as e:
            logging.error(f"Error loading proxies: {e}")
            raise

    def send_view(self):
        """Send view request using a proxy"""
        scraper = cloudscraper.create_scraper(delay=10)
        while not self.proxy_queue.empty():
            proxy = self.proxy_queue.get()
            proxy_dict = {"http": proxy, "https": proxy}
            try:
                response = scraper.post(
                    f"https://guns.lol/api/view/{url}",
                    headers=headers,
                    proxies=proxy_dict,
                    timeout=10
                )
                if response.status_code == 200:
                    with self.views_lock:
                        self.views += 1
                    logging.info(f"View sent successfully. Total views: {self.views}")
                else:
                    logging.warning(f"Failed request with status {response.status_code}")
                self.proxy_queue.put(proxy)  # Recycle working proxy
            except Exception as e:
                logging.debug(f"Request failed with proxy {proxy}: {str(e)}")
            finally:
                self.proxy_queue.task_done()

def main():
    bot = ViewBot()
    max_workers = min(50, bot.proxy_queue.qsize())  # Adjust based on proxy count
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(bot.send_view) for _ in range(max_workers)]
        try:
            concurrent.futures.wait(futures)
        except KeyboardInterrupt:
            logging.info("Shutting down gracefully.")
            executor._threads.clear()
            concurrent.futures.thread._threads_queues.clear()

if __name__ == "__main__":
    main()
