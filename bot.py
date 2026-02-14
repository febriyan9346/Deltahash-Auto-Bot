import os
import time
import requests
import sys
import json
import random
from datetime import datetime
import pytz
from colorama import Fore, Style, init
import warnings

warnings.filterwarnings('ignore')

init(autoreset=True)

UA_LIBRARY = {
    "computer": [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edg/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0"
    ],
    "mac": [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15"
    ],
    "android": [
        "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.6261.64 Mobile Safari/537.36",
        "Mozilla/5.0 (Linux; Android 13; SM-A536B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.144 Mobile Safari/537.36"
    ],
    "ios": [
        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
        "Mozilla/5.0 (iPad; CPU OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1"
    ]
}

class DeltaHashBot:
    def __init__(self):
        self.base_url = "https://portal.deltahash.ai"
        self.cookie_file = "cookies.json"
        self.headers_template = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "content-type": "application/json",
            "origin": "https://portal.deltahash.ai",
            "referer": "https://portal.deltahash.ai/mining",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin"
        }
        self.cookie_store = self.load_cookie_store()

    def get_wib_time(self):
        wib = pytz.timezone('Asia/Jakarta')
        return datetime.now(wib).strftime('%H:%M:%S')

    def print_banner(self):
        os.system('clear' if os.name == 'posix' else 'cls')
        banner = f"""
{Fore.CYAN}DELTAHASH AUTO BOT{Style.RESET_ALL}
{Fore.WHITE}By: FEBRIYAN{Style.RESET_ALL}
{Fore.CYAN}============================================================{Style.RESET_ALL}
"""
        print(banner)

    def log(self, message, level="INFO"):
        time_str = self.get_wib_time()
        
        if level == "INFO":
            color = Fore.CYAN
            symbol = "[INFO]"
        elif level == "SUCCESS":
            color = Fore.GREEN
            symbol = "[SUCCESS]"
        elif level == "ERROR":
            color = Fore.RED
            symbol = "[ERROR]"
        elif level == "WARNING":
            color = Fore.YELLOW
            symbol = "[WARNING]"
        elif level == "CYCLE":
            color = Fore.MAGENTA
            symbol = "[CYCLE]"
        else:
            color = Fore.WHITE
            symbol = "[LOG]"
        
        print(f"[{time_str}] {color}{symbol} {message}{Style.RESET_ALL}")

    def load_file(self, filename):
        try:
            with open(filename, 'r') as f:
                return [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            self.log(f"File {filename} not found!", "ERROR")
            return []

    def load_cookie_store(self):
        if not os.path.exists(self.cookie_file):
            return {}
        try:
            with open(self.cookie_file, 'r') as f:
                return json.load(f)
        except:
            return {}

    def save_cookie_store(self):
        try:
            with open(self.cookie_file, 'w') as f:
                json.dump(self.cookie_store, f, indent=4)
        except:
            pass

    def get_user_agent(self, cookie, force_device=None):
        if not force_device and cookie in self.cookie_store:
            return self.cookie_store[cookie].get("user_agent")
        
        device_type = force_device if force_device else "computer"
        new_ua = random.choice(UA_LIBRARY.get(device_type, UA_LIBRARY["computer"]))
        
        self.cookie_store[cookie] = {
            "user_agent": new_ua,
            "device": device_type
        }
        self.save_cookie_store()
        return new_ua

    def show_menu(self):
        print(f"{Fore.CYAN}============================================================{Style.RESET_ALL}")
        print(f"{Fore.CYAN}Select Mode:{Style.RESET_ALL}")
        print(f"{Fore.GREEN}1. Run with proxy")
        print(f"2. Run without proxy{Style.RESET_ALL}")
        print(f"{Fore.CYAN}============================================================{Style.RESET_ALL}")
        
        while True:
            try:
                choice = input(f"{Fore.GREEN}Enter your choice (1/2): {Style.RESET_ALL}").strip()
                if choice in ['1', '2']:
                    return choice
                else:
                    print(f"{Fore.RED}Invalid choice! Please enter 1 or 2.{Style.RESET_ALL}")
            except KeyboardInterrupt:
                exit(0)

    def countdown(self, seconds):
        for i in range(seconds, 0, -1):
            hours = i // 3600
            minutes = (i % 3600) // 60
            secs = i % 60
            print(f"\r[COUNTDOWN] Next cycle in: {hours:02d}:{minutes:02d}:{secs:02d} ", end="", flush=True)
            time.sleep(1)
        print("\r" + " " * 60 + "\r", end="", flush=True)

    def check_user(self, cookie, proxy):
        url = f"{self.base_url}/api/auth/me"
        user_agent = self.get_user_agent(cookie)
        
        headers = self.headers_template.copy()
        headers["cookie"] = cookie
        headers["user-agent"] = user_agent
        
        try:
            response = requests.get(url, headers=headers, proxies=proxy, timeout=30)
            if response.status_code == 200:
                data = response.json()
                user = data.get("user", {})
                return user
            return None
        except:
            return None

    def connect_mining(self, cookie, proxy, retry_count=0):
        if retry_count > 1:
            return None 

        url = f"{self.base_url}/api/mining/connect"
        user_agent = self.get_user_agent(cookie)
        
        headers = self.headers_template.copy()
        headers["cookie"] = cookie
        headers["user-agent"] = user_agent
        
        try:
            response = requests.post(url, json={}, headers=headers, proxies=proxy, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            
            try:
                error_msg = response.text.lower()
                if "registered with" in error_msg:
                    detected_device = "computer"
                    if "android" in error_msg:
                        detected_device = "android"
                    elif "ios" in error_msg or "iphone" in error_msg or "ipad" in error_msg:
                        detected_device = "ios"
                    elif "mac" in error_msg:
                        detected_device = "mac"
                    elif "linux" in error_msg:
                        detected_device = "computer"
                    
                    self.log(f"Device Mismatch! Switching to {detected_device}...", "WARNING")
                    self.get_user_agent(cookie, force_device=detected_device)
                    return self.connect_mining(cookie, proxy, retry_count + 1)
            except:
                pass
                
            return None
        except:
            return None

    def send_heartbeat(self, cookie, proxy):
        url = f"{self.base_url}/api/mining/heartbeat"
        user_agent = self.get_user_agent(cookie)
        
        headers = self.headers_template.copy()
        headers["cookie"] = cookie
        headers["user-agent"] = user_agent
        
        try:
            response = requests.post(url, headers=headers, proxies=proxy, timeout=30)
            if response.status_code == 200:
                return response.json()
            return None
        except:
            return None

    def run(self):
        self.print_banner()
        
        choice = self.show_menu()
        use_proxy = choice == '1'
        
        accounts = self.load_file("accounts.txt")
        proxies = self.load_file("proxy.txt") if use_proxy else []
        
        if not accounts:
            self.log("No accounts found in accounts.txt", "ERROR")
            return

        self.log(f"Loaded {len(accounts)} accounts", "INFO")
        
        print(f"\n{Fore.CYAN}============================================================{Style.RESET_ALL}\n")
        
        cycle = 1
        while True:
            self.log(f"Cycle #{cycle} Started", "CYCLE")
            print(f"{Fore.CYAN}------------------------------------------------------------{Style.RESET_ALL}")
            
            for i, cookie in enumerate(accounts):
                proxy_config = None
                proxy_str = "No Proxy"
                
                if use_proxy and proxies:
                    proxy_url = proxies[i % len(proxies)]
                    proxy_config = {"http": proxy_url, "https": proxy_url}
                    proxy_str = proxy_url

                self.log(f"Account #{i+1}/{len(accounts)}", "INFO")
                if use_proxy:
                    self.log(f"Proxy: {proxy_str}", "INFO")

                user = self.check_user(cookie, proxy_config)
                
                if user:
                    username = user.get("username", "Unknown")
                    balance = user.get("balance", 0)
                    self.log(f"User: {username} | Balance: {balance}", "SUCCESS")
                    
                    mining_data = self.connect_mining(cookie, proxy_config)
                    if mining_data and mining_data.get("success"):
                        epoch = mining_data.get("epochNumber", 0)
                        self.log(f"Mining Connected | Epoch: {epoch}", "SUCCESS")
                        
                        time.sleep(1)
                        
                        heartbeat_data = self.send_heartbeat(cookie, proxy_config)
                        if heartbeat_data and heartbeat_data.get("success"):
                            earned = heartbeat_data.get("tokensEarned", 0)
                            new_balance = heartbeat_data.get("newBalance", 0)
                            self.log(f"Heartbeat Success | Earned: {earned} | New Balance: {new_balance}", "SUCCESS")
                        else:
                            self.log("Heartbeat Failed", "ERROR")
                    else:
                        self.log("Mining Connection Failed", "ERROR")
                else:
                    self.log("Login Failed / Invalid Cookie", "ERROR")
                
                if i < len(accounts) - 1:
                    print(f"{Fore.WHITE}............................................................{Style.RESET_ALL}")
                    time.sleep(2)
            
            print(f"{Fore.CYAN}------------------------------------------------------------{Style.RESET_ALL}")
            self.log(f"Cycle #{cycle} Complete", "CYCLE")
            print(f"{Fore.CYAN}============================================================{Style.RESET_ALL}\n")
            
            cycle += 1
            self.countdown(30)

if __name__ == "__main__":
    try:
        bot = DeltaHashBot()
        bot.run()
    except KeyboardInterrupt:
        sys.exit()
