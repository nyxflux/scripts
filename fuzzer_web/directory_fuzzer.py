import requests 
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from functools import partial
import uuid
import threading
from colorama import Fore, init

target_url = input("What is the target URL ?:").rstrip("/")
session = requests.Session()
TIMEOUT =1 
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/114.0.0.0 Safari/537.36"
}
session.headers.update(headers)
MAX_WORKERS = int(input("Number of threads (default 20): ") or 20)
ROUND_PRECISION = 2
lock = threading.Lock()
tested = 0
found = 0
errors = 0
init(autoreset=True)
found_color = Fore.GREEN
error_color = Fore.RED
progress_color = Fore.CYAN




def get_wordlist():
    wordlist = []
    with open("wordlist.txt", "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()  
            if line:
                wordlist.append(line)
    return wordlist



def detect_wildcard(target_url):
    random_path = str(uuid.uuid4())
    url = f"{target_url}/{random_path}"

    response = session.get(url, timeout = TIMEOUT)
    wildcard_signature = (response.status_code, len(response.content))
    return wildcard_signature
wildcard = detect_wildcard(target_url)


def fuzz_directory(target_url, wildcard, directory):
    url = f"{target_url}/{directory}" 
    global tested, found, errors

    try:
        response = session.get(url, timeout = TIMEOUT)
        current_signature = (response.status_code, len(response.content))
        if response.status_code == 404:
            return
        if current_signature == wildcard:
            return
        else:
            with lock:
                print(
                    f"{found_color}{response.status_code:<4}"
                    f"{Fore.WHITE}{len(response.content):<8}"
                    f"{Fore.YELLOW}{round(response.elapsed.total_seconds()*1000, 2):<8}ms "
                    f"{Fore.GREEN}{url}",
                    end="\r"
                )
                found += 1
                results_file.write(
                    f"{response.status_code:<4}"
                    f"{len(response.content):<8}"
                    f"{round(response.elapsed.total_seconds()*1000, 2):<8}ms "
                    f"{url}\n"
                )        
    except requests.RequestException as e:
        with lock:
            print(f"{error_color}An error occurred: {e}", end="\r")
            errors += 1
    finally:
        with lock:
            tested += 1
            progress = tested / TOTAL
            
            filled = int(progress * BAR_LENGTH)
            empty = BAR_LENGTH - filled
            bar = "█" * filled + "-" * empty

            print(
                f"\r{progress_color}[{bar}] "
                f"{progress*100:6.2f}% "
                f"{Fore.WHITE}Tested:{tested:>5}/{TOTAL:<5} "
                f"{found_color}Found:{found:<3} "
                f"{error_color}Errors:{errors:<3} "
                f"{Fore.WHITE}Testing: {directory:<30}",
                end="",
                flush=True
            )



wordlist = get_wordlist()
TOTAL = len(wordlist)
BAR_LENGTH = 30
worker = partial(fuzz_directory, target_url, wildcard)
debut = datetime.now()

with open("results.txt", "w", encoding="utf-8") as results_file:
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        executor.map(worker, wordlist)
fin = datetime.now()    

duration = (fin - debut).total_seconds()
speed = tested / duration if duration > 0 else 0
print()
print("\n========== Scan completed successfully! ==========")
print("Results saved to: results.txt")
print(f"Wildcard signature: {wildcard}")
print(f"{Fore.CYAN}Directories tested : {tested}")
print(f"{Fore.GREEN}Directories found  : {found}")
print(f"{Fore.RED}Errors             : {errors}")
print(f"{Fore.YELLOW}Duration           : {round(duration, ROUND_PRECISION)} s")
print(f"{Fore.MAGENTA}Speed              : {round(speed, ROUND_PRECISION)} req/s")