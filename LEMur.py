import socket
from colorama import init, Fore, Style
import datetime

init(autoreset=True)

LOG_FILE = "LEMur_log.txt"

def log_message(direction, ip, message):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"[{time}] {direction} {ip}: {message}\n")

def print_banner():
    print(Fore.CYAN + Style.BRIGHT + r"""
  _      ______  __  __ 
 | |    |  ____||  \/  |
 | |    | |__   | \  / |
 | |    |  __|  | |\/| |
 | |____| |____ | |  | |
 |______|______||_|  |_|
                        
      LEMur - Komunikator
""")

def xor_crypt(data, key):
    return bytes([b ^ key for b in data])

def send_message():
    print(Fore.GREEN + "\n-- Tryb NADAWANIA --")
    ip = input("Podaj IP odbiorcy: ")
    port = int(input("Podaj port: "))
    key = 42
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(2)  # timeout 2 sekundy
    
    # Wyślij zaszyfrowane PING
    ping_msg = xor_crypt(b"PING", key)
    sock.sendto(ping_msg, (ip, port))
    
    try:
        data, addr = sock.recvfrom(1024)
        if addr[0] == ip and xor_crypt(data, key) == b"PONG":
            print(Fore.GREEN + "Odebrano potwierdzenie PONG — możesz wysłać wiadomość.")
            message = input("Wpisz wiadomość do wysłania: ")
            encrypted = xor_crypt(message.encode(), key)
            sock.sendto(encrypted, (ip, port))
            print(Fore.GREEN + "Wiadomość wysłana!")
            log_message("Wysłano do", ip, message)
        else:
            print(Fore.RED + "Otrzymano niepoprawną odpowiedź.")
    except socket.timeout:
        print(Fore.RED + "Brak odpowiedzi — prawdopodobnie nikt nie nasłuchuje na tym IP i porcie.")
    finally:
        sock.close()

def receive_message():
    print(Fore.YELLOW + "\n-- Tryb ODBIORU --")
    port = int(input("Podaj port do nasłuchiwania: "))
    key = 42
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(('', port))
    print(Fore.YELLOW + f'LEMur nasłuchuje na porcie {port}...')
    print(Fore.YELLOW + "Aby zakończyć odbiór, wciśnij Ctrl+C")
    try:
        while True:
            data, addr = sock.recvfrom(1024)
            decrypted = xor_crypt(data, key)
            if decrypted == b"PING":
                pong_msg = xor_crypt(b"PONG", key)
                sock.sendto(pong_msg, addr)
            else:
                print(Fore.MAGENTA + f'\nWiadomość od {addr}: {decrypted.decode()}')
                log_message("Odebrano od", addr[0], decrypted.decode())
    except KeyboardInterrupt:
        print(Fore.RED + "\nOdbiór zakończony.")
    finally:
        sock.close()

def main():
    while True:
        print_banner()
        print(Fore.CYAN + "1. Nadaj wiadomość")
        print(Fore.CYAN + "2. Odbierz wiadomość")
        print(Fore.CYAN + "3. Wyjdź")
        choice = input(Fore.WHITE + "Wybierz opcję (1/2/3): ")
        
        if choice == '1':
            send_message()
        elif choice == '2':
            receive_message()
        elif choice == '3':
            print(Fore.RED + "Do zobaczenia!")
            break
        else:
            print(Fore.RED + "Nieznana opcja, spróbuj jeszcze raz.")

if __name__ == '__main__':
    main()
