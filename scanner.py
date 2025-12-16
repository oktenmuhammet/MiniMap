import socket
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import platform
import subprocess
import json


BANNER = r"""
 __  __ _       _ __  __           
|  \/  (_)_ __ (_)  \/  | __ _ ___ 
| |\/| | | '_ \| | |\/| |/ _` / __|
| |  | | | | | | | |  | | (_| \__ \
|_|  |_|_|_| |_|_|_|  |_|\__,_|___/

MiniMap v1.0
Simple Port & Network Scanner
"""
print(BANNER)






# colorama varsa renkli çıktı kullan; yoksa sorunsuz devam et
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    COLOR_OK = True
except ImportError:
    COLOR_OK = False


# Küçük servis sözlüğü
SERVICES = {
    20: "FTP (data)", 21: "FTP (ctrl)", 22: "SSH", 23: "Telnet",
    25: "SMTP", 53: "DNS", 67: "DHCP", 68: "DHCP",
    80: "HTTP", 110: "POP3", 143: "IMAP", 161: "SNMP",
    194: "IRC", 443: "HTTPS", 445: "SMB", 993: "IMAPS",
    995: "POP3S", 3306: "MySQL", 3389: "RDP", 5900: "VNC",
    8080: "HTTP-alt"}
def get_service_name(port):
    # Önce kendi sözlüğümüze bak
    if port in SERVICES:
        return SERVICES[port]

    # Yoksa sistemden dene
    try:
        return socket.getservbyport(port)
    except:
        return ""

# -----------------------------------------
# PING FONKSİYONU (Windows / Linux Otomatik)
# -----------------------------------------
def ping_ip(ip):
    system = platform.system().lower()

    if system == "windows":
        cmd = ["ping", "-n", "1", "-w", "1000", ip]
    else:
        cmd = ["ping", "-c", "1", "-W", "1", ip]

    try:
        result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return result.returncode == 0
    except:
        return False


# -------------------------
# IP RANGE PARSE FONKSİYONU
# -------------------------
def parse_ip_range(ip_input):
    if "-" in ip_input:
        try:
            base, end_range = ip_input.split("-")
            parts = base.split(".")
            start_ip = int(parts[-1])
            end_ip = int(end_range)

            base_prefix = ".".join(parts[:-1])

            ip_list = []
            for last in range(start_ip, end_ip + 1):
                ip_list.append(f"{base_prefix}.{last}")

            return ip_list
        except:
            print("Hatalı IP aralığı formatı! Örn: 192.168.1.1-254")
            exit(1)
    else:
        return [ip_input]


# -------------------------
# PORT TARAMA FONKSİYONU
# -------------------------
def scan_port(ip, port, timeout=0.5):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        result = sock.connect_ex((ip, port))
        return result == 0
    except:
        return False
    finally:
        sock.close()


# -------------------------
# PORT RANGE TARAYICI
# -------------------------
def scan_range(ip, start_port, end_port, max_workers=50, timeout=0.5):
    print(f"\n----------------------------")
    print(f"Tarama Başladı: {ip}")
    print(f"Port Aralığı: {start_port}-{end_port}  |  Threads: {max_workers}")
    print(f"----------------------------\n")

    open_ports = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(scan_port, ip, port, timeout): port
            for port in range(start_port, end_port + 1)
        }
        for future in as_completed(futures):
            port = futures[future]
            service = ""  # KRİTİK SATIR

            try:
                if future.result():
                    service = get_service_name(port)
                    open_ports.append((port, service))

                    if COLOR_OK:
                        print(
                            f"{Fore.GREEN}[+] Port açık: {port} "
                            f"{Fore.CYAN}{'(' + service + ')' if service else ''}"
                        )
                    else:
                        print(
                            f"[+] Port açık: {port} "
                            f"{'(' + service + ')' if service else ''}"
                        )

            except Exception as e:
                print(f"[!] Tarama hatası (port {port}): {e}")

  


    print("\nTarama tamamlandı!")

    if open_ports:
        print("Açık Portlar:", [p for p, s in open_ports])
    else:
        print("Herhangi bir açık port bulunamadı.")

    return open_ports


def parse_ports(port_range):
    try:
        start, end = port_range.split("-")
        return int(start), int(end)
    except:
        print("Hatalı port aralığı! Örn: 1-1024")
        exit(1)


def save_results(filename, ip, start_port, end_port, open_ports):
    with open(filename, "a", encoding="utf-8") as f:
        f.write(f"\nHedef: {ip}\n")
        f.write(f"Port Aralığı: {start_port}-{end_port}\n")
        if open_ports:
            for port, service in open_ports:
                f.write(f"- {port} {('('+service+')') if service else ''}\n")
        else:
            f.write("- Hiçbir açık port yok.\n")


# -------------------------
# MAIN PROGRAM
# -------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Mini Nmap - Port & Ağ Tarayıcı")
    parser.add_argument("-ip", "--ip", required=True, help="Hedef IP veya IP aralığı")
    parser.add_argument("-p", "--ports", required=True, help="Port aralığı (örn: 1-1000)")
    parser.add_argument("--scan-mode", choices=["ping", "full"], default="full",
                        help="Tarama modu: 'ping' = önce canlı IP bulur, 'full' = tüm IP'leri tarar")
    parser.add_argument("-t", "--threads", type=int, default=50, help="Thread sayısı")
    parser.add_argument("-o", "--output", help="Çıktı dosyası (örn: sonuc.txt)")
    parser.add_argument("--timeout", type=float, default=0.5, help="Port timeout süresi")

    args = parser.parse_args()

    # IP listesi
    targets = parse_ip_range(args.ip)
    start_port, end_port = parse_ports(args.ports)

    # TARAMA MODU
    if args.scan_mode == "ping":
        print("\n[+] Ping taraması başlatılıyor...\n")
        alive_hosts = []
        for ip in targets:
            if ping_ip(ip):
                print(f"[ALIVE] {ip} aktif")
                alive_hosts.append(ip)
            else:
                print(f"[DEAD]  {ip} yanıt vermedi")

        print(f"\n[+] Canlı IP sayısı: {len(alive_hosts)}\n")
        targets = alive_hosts  # sadece canlıları tarayacağız

    # PORT TARAMASI
    for target_ip in targets:
        results = scan_range(target_ip, start_port, end_port,
                             max_workers=args.threads, timeout=args.timeout)

        if args.output:
            save_results(args.output, target_ip, start_port, end_port, results)
            print(f"[+] {target_ip} için sonuçlar kaydedildi.\n")
