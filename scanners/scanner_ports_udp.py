import socket
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

target_ip = input("What is the target IP ?:")
port_start = int(input("What is the first port to scan ?:"))
port_end = int(input("What is the last port to scan ?:"))


def test_udp(target_ip, port_start, port_end):
    open_ports = []
    debut = datetime.now()
    
    #Test one port to do multithreading 
    def test_one_port(port):
        #Create a socket and set a response 's time
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.settimeout(0.1)
        
        #Connection attempt
        resultat = sock.sendto(b"", (target_ip, port))
        
       
        try:
            #Listening for the server's answer 
            sock.recvfrom(1024)
   
            ouvert = True
        except socket.timeout:
            ouvert = True   
        except:
            ouvert = False 
        
        #The socket is closed after each test to free up resources
        sock.close()
          
        if ouvert:
            try:
                service = socket.getservbyport(port, "udp")
                open_ports.append((port, service))
                print(f"Le port /udp {port} ({service}) est ouvert")
            
            except OSError:
                pass   
    
    with ThreadPoolExecutor(max_workers=100) as executor:
        #Use the function test_one_port for each selected port in order to test 100 ports at a time with ThreadPoolExecutor
        executor.map(test_one_port, range(port_start, port_end + 1))
    
    
    #Final summary
    print(f"Scan terminé. {len(open_ports)} port(s) ouvert(s) : {open_ports}")       
    fin = datetime.now()       
    print(f"Durée : {fin - debut}")
        
#If the IP address is invalid, the script returns an error message
try:
    test_udp(target_ip, port_start, port_end)
except socket.gaierror:
    print("Erreur : adresse IP invalide")   
