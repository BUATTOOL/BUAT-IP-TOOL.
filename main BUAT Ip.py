#!/usr/bin/env python3
"""
BUAT IP Tool
Professional IP Intelligence CLI
"""

import argparse
import concurrent.futures
from datetime import datetime
import ipaddress
import socket
import requests

# Optional WHOIS (not required, kept for future expansion)
try:
    import whois
    WHOIS_AVAILABLE = True
except Exception:
    WHOIS_AVAILABLE = False

# Purple theme
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    PURPLE = Fore.MAGENTA
    DIM = Style.DIM
    BOLD = Style.BRIGHT
    RESET = Style.RESET_ALL
except Exception:
    PURPLE = DIM = BOLD = RESET = ""


def now():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class BUATIPTool:
    def __init__(self):
        self.session = requests.Session()
        self.results = {}

    # ---------------- Banner (Option B Safe) ----------------
    def banner(self):
        logo = r"""
██████╗ ██╗   ██╗ █████╗ ████████╗    ██╗██████╗     ████████╗ ██████╗  ██████╗ ██╗
██╔══██╗██║   ██║██╔══██╗╚══██╔══╝    ██║██╔══██╗    ╚══██╔══╝██╔═══██╗██╔═══██╗██║
██████╔╝██║   ██║███████║   ██║       ██║██████╔╝       ██║   ██║   ██║██║   ██║██║
██╔══██╗██║   ██║██╔══██║   ██║       ██║██╔═══╝        ██║   ██║   ██║██║   ██║██║
██████╔╝╚██████╔╝██║  ██║   ██║       ██║██║            ██║   ╚██████╔╝╚██████╔╝███████╗
╚═════╝  ╚═════╝ ╚═╝  ╚═╝   ╚═╝       ╚═╝╚═╝            ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝
"""
        print(logo)  # NO COLOR inside logo
        print(f"{PURPLE}{BOLD}BUAT IP Tool{RESET}{DIM}  •  Made by buattool on Tikotok  •  {now()}{RESET}\n")

    # ---------------- Helpers ----------------
    def validate_ip(self, ip):
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False

    def resolve_domain(self, domain):
        try:
            return sorted({info[4][0] for info in socket.getaddrinfo(domain, None)})
        except Exception:
            return []

    def reverse_dns(self, ip):
        try:
            host, _, _ = socket.gethostbyaddr(ip)
            return host
        except Exception:
            return None

    # ---------------- Intel Sources ----------------
    def ip_api(self, ip):
        try:
            r = self.session.get(f"http://ip-api.com/json/{ip}", timeout=5)
            if r.status_code == 200:
                data = r.json()
                if data.get("status") == "success":
                    return data
        except Exception:
            pass
        return None

    # ---------------- Display ----------------
    def section(self, title):
        print(f"{PURPLE}{BOLD}{title}{RESET}")
        print(f"{PURPLE}{'-'*len(title)}{RESET}")

    def kv(self, k, v):
        if v is None:
            return
        if isinstance(v, str) and v.strip() == "":
            return
        print(f"{DIM}{k:<18}{RESET} {v}")

    def display(self):
        ip = self.results.get("target")

        self.section("Target Information")
        self.kv("IP Address", ip)
        self.kv("Reverse DNS", self.results.get("reverse_dns"))

        geo = self.results.get("ipapi")
        if geo:
            self.section("Geolocation")
            self.kv("Country", geo.get("country"))
            self.kv("Region", geo.get("regionName"))
            self.kv("City", geo.get("city"))
            self.kv("ISP", geo.get("isp"))
            self.kv("Organization", geo.get("org"))
            self.kv("ASN", geo.get("as"))
            self.kv("Coordinates", f"{geo.get('lat')}, {geo.get('lon')}")

        print()  # spacing

    # ---------------- Core ----------------
    def gather(self, ip):
        self.results = {"target": ip}
        with concurrent.futures.ThreadPoolExecutor() as ex:
            future_geo = ex.submit(self.ip_api, ip)
            self.results["ipapi"] = future_geo.result()
        self.results["reverse_dns"] = self.reverse_dns(ip)


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("target", nargs="?", help="IP or domain")
    args = parser.parse_args()

    tool = BUATIPTool()
    tool.banner()

    # One-shot mode if target provided
    if args.target:
        target = args.target.strip()
        if tool.validate_ip(target):
            tool.gather(target)
            tool.display()
            return
        ips = tool.resolve_domain(target)
        if not ips:
            print("Could not resolve domain.")
            return
        for ip in ips:
            tool.gather(ip)
            tool.display()
        return

    # Interactive loop mode
    while True:
        target = input(f"{PURPLE}{BOLD}Target{RESET}{DIM} (q to quit){RESET}: ").strip()

        # Empty input => reset back to prompt
        if target == "":
            continue

        # Quit keywords
        if target.lower() in {"q", "quit", "exit"}:
            print(f"{PURPLE}{DIM}bye.{RESET}")
            break

        if tool.validate_ip(target):
            tool.gather(target)
            tool.display()
            continue

        ips = tool.resolve_domain(target)
        if not ips:
            print("Could not resolve domain.\n")
            continue

        for ip in ips:
            tool.gather(ip)
            tool.display()


if __name__ == "__main__":
    run()