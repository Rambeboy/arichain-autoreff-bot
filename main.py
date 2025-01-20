import requests
import random
import re
import time
import os
import string
import names
from colorama import Fore, Style, init
from datetime import datetime

init()

ANDROID_USER_AGENTS = [
    'Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 13; SM-A536B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 13; SM-A346B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 13; SM-A236B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 12; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 13; M2101K6G) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 12; moto g(30)) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 12; CPH2211) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36',
    'Mozilla/5.0 (Linux; Android 13; V2169) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36'
]

def get_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def log(message, color=Fore.WHITE, current=None, total=None):
    timestamp = f"[{Fore.LIGHTBLACK_EX}{get_timestamp()}{Style.RESET_ALL}]"
    progress = f"[{Fore.LIGHTBLACK_EX}{current}/{total}{Style.RESET_ALL}]" if current is not None and total is not None else ""
    print(f"{timestamp} {progress} {color}{message}{Style.RESET_ALL}")

def ask(message):
    return input(f"{Fore.YELLOW}{message}{Style.RESET_ALL}")

def load_proxies():
    try:
        with open("proxies.txt", "r") as file:
            proxies = [line.strip() for line in file if line.strip()]
        print(f"{Fore.GREEN}\nLoaded {len(proxies)} proxies{Style.RESET_ALL}")
        return proxies
    except FileNotFoundError:
        print(f"{Fore.RED}\nFile proxies.txt not found{Style.RESET_ALL}")
        return []

def get_random_proxy(proxies):
    return random.choice(proxies) if proxies else None

def generate_keyword():
    vowels = 'aeiou'
    consonants = ''.join(set(string.ascii_lowercase) - set(vowels))
    return random.choice(consonants) + random.choice(vowels)

def get_random_domain(proxy_dict, current=None, total=None):
    keyword = generate_keyword()
    url = f"https://generator.email/search.php?key={keyword}"
    
    try:
        headers = {'User-Agent': random.choice(ANDROID_USER_AGENTS)}
        resp = requests.get(url, proxies=proxy_dict, headers=headers, timeout=120)
        resp.raise_for_status()
        domains = resp.json()
        
        valid_domains = [
            domain for domain in domains 
            if domain.count('.') == 1 and domain.encode('utf-8')
        ]
        
        if not valid_domains:
            log("No valid domains found", Fore.YELLOW, current, total)
            return None
            
        return random.choice(valid_domains)
        
    except Exception as e:
        log(f"Error fetching domain: {str(e)}", Fore.RED, current, total)
        return None

def generate_username():
    first_name = names.get_first_name().lower()
    last_name = names.get_last_name().lower()
    separator = random.choice(['', '.'])
    random_numbers = ''.join(random.choices(string.digits, k=3))
    return f"{first_name}{separator}{last_name}{random_numbers}"

def generate_password():
    word = ''.join(random.choices(string.ascii_letters, k=5))
    numbers = ''.join(random.choices(string.digits, k=3))
    return f"{word.capitalize()}@{numbers}#"

def generate_email(proxy_dict, current=None, total=None):
    domain = get_random_domain(proxy_dict, current, total)
    if not domain:
        return None
    username = generate_username()
    return f"{username}@{domain}"

def send_otp(email, proxy_dict, headers, current=None, total=None):
    url = "https://arichain.io/api/email/send_valid_email"
    payload = {
        'blockchain': "testnet",
        'email': email,
        'lang': "en",
        'device': "app",
        'is_mobile': "Y"
    }
    try:
        response = requests.post(url, data=payload, headers=headers, proxies=proxy_dict, timeout=120)
        response.raise_for_status()
        log(f"OTP code sent to {email}", Fore.YELLOW, current, total)
        return True
    except requests.RequestException as e:
        log(f"Failed to send OTP: {e}", Fore.RED, current, total)
        return False

def check_inbox(email, proxy_dict, retries=9, current=None, total=None):
    email_username, email_domain = email.split('@')
    
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'cookie': f'embx=%5B%{email}%40{email_domain}%22%2C%{email}%40{email_domain}%22%5D; surl={email_domain}/{email_username}',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'user-agent': random.choice(ANDROID_USER_AGENTS)
    }

    pattern = r'<b style="letter-spacing: 16px; color: #fff; font-size: 40px; font-weight: 600;[^>]*>(\d{6})</b>'
    
    log("Checking inboxes for OTP code...", Fore.CYAN, current, total)
    
    for inbox_num in range(1, retries + 1):
        try:
            log(f"Checking inbox {inbox_num}...", Fore.CYAN, current, total)
            url = f"https://generator.email/inbox{inbox_num}/"
            
            response = requests.get(url, headers=headers, proxies=proxy_dict, timeout=120)
            response.raise_for_status()
            
            match = re.search(pattern, response.text)
            if match:
                code = match.group(1)
                log(f"Found OTP: {code}", Fore.YELLOW, current, total)
                return code
            
        except requests.RequestException as e:
            log(f"Failed to check inbox {inbox_num}: {e}", Fore.RED, current, total)
    
    log("No OTP code found in any inbox", Fore.YELLOW, current, total)
    return None

def verify_otp(email, valid_code, password, proxy_dict, invite_code, headers, current=None, total=None):
    url = "https://arichain.io/api/account/signup_mobile"
    payload = {
        'blockchain': "testnet",
        'email': email,
        'valid_code': valid_code,
        'pw': password,
        'pw_re': password,
        'invite_code': invite_code,
        'lang': "en",
        'device': "app",
        'is_mobile': "Y"
    }

    try:
        response = requests.post(url, data=payload, headers=headers, proxies=proxy_dict, timeout=120)
        response.raise_for_status()
        result = response.json()
        log(f"Success Register with referral code {invite_code}", Fore.GREEN, current, total)

        with open("accounts.txt", "a") as file:
            file.write(f"{result['result']['session_code']}|{email}|{password}|{result['result']['address']}|{result['result']['master_key']}\n")

        return result['result']['address']

    except requests.RequestException as e:
        log(f"Failed to verify OTP: {e}", Fore.RED, current, total)
        return None

def daily_claim(address, proxy_dict, headers, current=None, total=None):
    url = "https://arichain.io/api/event/checkin"
    payload = {
        'blockchain': "testnet",
        'address': address,
        'lang': "en",
        'device': "app",
        'is_mobile': "Y"
    }

    try:
        response = requests.post(url, data=payload, headers=headers, proxies=proxy_dict, timeout=120)
        response.raise_for_status()
        data = response.json()

        if data.get('status') == 'success':
            log("Success claim Daily", Fore.GREEN, current, total)
            return True
        log("Daily claim failed", Fore.RED, current, total)
        return False
    except requests.exceptions.RequestException as e:
        log(f"Daily claim error: {str(e)}", Fore.RED, current, total)
        return False

def auto_send(email, to_address, password, proxy_dict, headers, current=None, total=None):
    url = "https://arichain.io/api/wallet/transfer_mobile"
    
    payload = {
        'blockchain': "testnet",
        'symbol': "ARI",
        'email': email,
        'to_address': to_address,
        'pw': password,
        'amount': "60",
        'memo': "",
        'valid_code': "",
        'lang': "en",
        'device': "app",
        'is_mobile': "Y"
    }

    try:
        response = requests.post(url, data=payload, headers=headers, proxies=proxy_dict, timeout=120)
        response.raise_for_status()
        result = response.json()
        
        if result.get("status") == "success" and result.get("result") == "success":
            log(f"Success sent 60 ARI to {to_address}", Fore.GREEN, current, total)
            return True
        else:
            log(f"Failed to send: {result}", Fore.RED, current, total)
            return False
            
    except requests.RequestException as e:
        log(f"Auto-send failed: {e}", Fore.RED, current, total)
        return False

def print_banner():
    print(Fore.CYAN + """
╔═══════════════════════════════════════════╗
║        Ari Wallet Auto Referral           ║
║          Author : Nofan Rambe             ║
╚═══════════════════════════════════════════╝
    """ + Style.RESET_ALL)

def get_referral_count():
    while True:
        try:
            count = int(ask('Enter desired number of referrals: '))
            if count > 0:
                return count
            log('Please enter a positive number.', Fore.YELLOW)
        except ValueError:
            log('Please enter a valid number.', Fore.RED)

def get_target_address():
    while True:
        address = ask('Enter target address for auto-send: ').strip()
        if address:
            return address
        log('Please enter a valid address.', Fore.YELLOW)

def get_referral_code():
    while True:
        code = ask('Enter your referral code: ').strip()
        if code:
            return code
        log('Please enter a valid referral code.', Fore.YELLOW)

def process_single_referral(index, total_referrals, proxy_dict, target_address, ref_code, headers):
    while True:
        print(f"{Fore.CYAN}\nStarting new referral process\n{Style.RESET_ALL}")

        email = generate_email(proxy_dict, index, total_referrals)
        if not email:
            log("Failed to generate email. Retrying...", Fore.RED, index, total_referrals)
            continue

        password = generate_password()
        log(f"Generated account: {email}:{password}", Fore.CYAN, index, total_referrals)

        if not send_otp(email, proxy_dict, headers, index, total_referrals):
            log("Failed to send OTP. Retrying...", Fore.RED, index, total_referrals)
            continue

        valid_code = check_inbox(email, proxy_dict, 9, index, total_referrals)
        if not valid_code:
            log("Failed to get OTP code. Starting with new email...", Fore.RED, index, total_referrals)
            continue

        address = verify_otp(email, valid_code, password, proxy_dict, ref_code, headers, index, total_referrals)
        if not address:
            log("Failed to verify OTP. Starting with new email...", Fore.RED, index, total_referrals)
            continue

        daily_claim(address, proxy_dict, headers, index, total_referrals)
        auto_send(email, target_address, password, proxy_dict, headers, index, total_referrals)
        
        log(f"Referral #{index} success!", Fore.YELLOW, index, total_referrals)
        return True

def main():
    print_banner()
    
    ref_code = get_referral_code()
    if not ref_code:
        return

    total_referrals = get_referral_count()
    if not total_referrals:
        return
        
    target_address = get_target_address()
    if not target_address:
        return

    proxies = load_proxies()
    headers = {
        'Accept': "application/json",
        'Accept-Encoding': "gzip",
        'User-Agent': random.choice(ANDROID_USER_AGENTS)
    }
    
    for index in range(1, total_referrals + 1):
        proxy = get_random_proxy(proxies)
        proxy_dict = {"http": proxy, "https": proxy} if proxy else None
        
        while not process_single_referral(index, total_referrals, proxy_dict, target_address, ref_code, headers):
            log(f"Retrying referral #{index}", Fore.YELLOW, index, total_referrals)
            proxy = get_random_proxy(proxies)
            proxy_dict = {"http": proxy, "https": proxy} if proxy else None

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"{Fore.YELLOW}\nScript terminated by user{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}\nAn unexpected error occurred: {str(e)}{Style.RESET_ALL}")
    finally:
        print(f"{Fore.CYAN}\nAll Process completed{Style.RESET_ALL}")
