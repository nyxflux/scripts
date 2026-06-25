import socket
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

target_ip = input("What is the target IP ?:")
port_start = int(input("What is the first port to scan ?:"))
port_end = int(input("What is the last port to scan ?:"))


def test_port(target_ip, port_start, port_end):
    open_ports = []
    debut = datetime.now()
    
    #Test one port to do multithreading 
    def test_one_port(port):
        #Create a socket and set a response 's time
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(0.1)
        
        #Connection attempt
        resultat = sock.connect_ex((target_ip, port))
        #The socket is closed after each test to free up resources
        sock.close()
        
        if resultat == 0:
            #Determine the port service
            try:
                service = socket.getservbyport(port)
            except OSError:
                service = "Inconnu"
            
            #Save the answer
            open_ports.append((port, service))
            print(f"Le port /tcp {port} ({service}) est ouvert")
    
    with ThreadPoolExecutor(max_workers=100) as executor:
        #Use the function test_one_port for each selected port in order to test 100 ports at a time with ThreadPoolExecutor
        executor.map(test_one_port, range(port_start, port_end + 1))
    
    
    #Final summary
    print(f"Scan terminé. {len(open_ports)} port(s) ouvert(s) : {open_ports}")       
    fin = datetime.now()       
    print(f"Durée : {fin - debut}")
        
#If the IP address is invalid, the script returns an error message
try:
    test_port(target_ip, port_start, port_end)
except socket.gaierror:
    print("Erreur : adresse IP invalide")   
