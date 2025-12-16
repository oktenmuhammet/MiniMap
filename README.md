# MiniMap

MiniMap is a simple and fast port & network scanner written in Python.
It is designed as a lightweight alternative to tools like Nmap.

---

## Features
- Multi-threaded TCP port scanning
- IP range scanning
- Ping sweep (alive host detection)
- Dynamic service name detection
- TXT report output
- Cross-platform (Windows / Linux)

---

## Requirements
- Python 3.8+
- Optional: colorama (for colored output)

```bash
pip install colorama

Usage

Basic scan:

python scanner.py -ip 127.0.0.1 -p 1-1000


IP range scan:

python scanner.py -ip 192.168.1.1-10 -p 80-100


Ping sweep:

python scanner.py -ip 192.168.1.1-10 -p 1-1000 --scan-mode ping


Save results:

python scanner.py -ip 127.0.0.1 -p 1-1000 -o report.txt

Disclaimer

This project is for educational and authorized security testing purposes only.

Author

GitHub: https://github.com/oktenmuhammet