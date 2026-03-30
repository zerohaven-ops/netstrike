#!/usr/bin/env python3
"""
NETSTRIKE v4.0 - PHANTOM EDITION
Professional Wireless Security Testing Suite
For authorized lab use only.
"""

import os
import sys
import time
import signal
from core import NetStrikeCore
from scanner import NetworkScanner
from attacker import AttackManager
from cracker import PasswordCracker
from installer import ToolInstaller

BANNER = """\033[1;35m
╔══════════════════════════════════════════════════════════════════╗
║  ███╗   ██╗███████╗████████╗███████╗████████╗██████╗ ██╗██╗  ██╗║
║  ████╗  ██║██╔════╝╚══██╔══╝██╔════╝╚══██╔══╝██╔══██╗██║██║ ██╔╝║
║  ██╔██╗ ██║█████╗     ██║   ███████╗   ██║   ██████╔╝██║█████╔╝ ║
║  ██║╚██╗██║██╔══╝     ██║   ╚════██║   ██║   ██╔══██╗██║██╔═██╗ ║
║  ██║ ╚████║███████╗   ██║   ███████║   ██║   ██║  ██║██║██║  ██╗║
║  ╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝╚═╝  ╚═╝║
║                                                                  ║
║     ⚡  B E A S T   E D I T I O N   v 5 . 0   ⚡               ║
║       Professional Wireless Security Testing Suite              ║
║    GPU Cracking | 3-Engine Deauth | Auto-Install | Evil Twin    ║
║  ⚠  AUTHORIZED PENETRATION TESTING AND LAB USE ONLY  ⚠         ║
╚══════════════════════════════════════════════════════════════════╝
\033[0m"""


class NetStrike:
    def __init__(self):
        self.core    = NetStrikeCore()
        self.scanner = NetworkScanner(self.core)
        self.attacker = AttackManager(self.core, self.scanner)
        self.cracker  = PasswordCracker(self.core, self.scanner)

    # ─────────────────────────────────────────────
    # MAIN MENU
    # ─────────────────────────────────────────────

    def _get_stats(self):
        nets  = len(self.scanner.networks) if self.scanner.networks else 0
        creds = 0
        try:
            if os.path.exists("/tmp/ns_cracked.txt"):
                with open("/tmp/ns_cracked.txt") as f:
                    creds = sum(1 for l in f if l.strip())
        except Exception:
            pass
        return nets, creds

    def main_menu(self):
        while True:
            os.system('clear')
            print(BANNER)
            mon  = self.core.mon_interface or "none"
            nets, creds = self._get_stats()
            print("\033[1;35m╔══════════════════════════════════════════════════════════════════╗\033[0m")
            print("\033[1;35m║                    ⚡  OPERATIONS CENTER                         ║\033[0m")
            print("\033[1;35m╠══════════════════════════════════════════════════════════════════╣\033[0m")
            print("\033[1;35m║                                                                  ║\033[0m")
            print("\033[1;35m║  \033[1;36m1\033[0m)  \033[1;31m📶 SINGLE DEAUTH\033[0m          Normal / Stealth mode        \033[1;35m║\033[0m")
            print("\033[1;35m║  \033[1;36m2\033[0m)  \033[1;31m🌐 MASS DEAUTH (SKIP)\033[0m     3-engine, no survivor mode   \033[1;35m║\033[0m")
            print("\033[1;35m║  \033[1;36m3\033[0m)  \033[1;31m💢 FULL SPECTRUM JAMMING\033[0m  All channels, all networks   \033[1;35m║\033[0m")
            print("\033[1;35m║  \033[1;36m4\033[0m)  \033[1;33m🔓 PASSWORD CRACKING\033[0m      GPU + masks + PMKID + WPS    \033[1;35m║\033[0m")
            print("\033[1;35m║  \033[1;36m5\033[0m)  \033[1;34m🎭 EVIL TWIN AP\033[0m           CHAMELEON phishing engine   \033[1;35m║\033[0m")
            print("\033[1;35m║  \033[1;36m6\033[0m)  \033[1;32m📡 NETWORK SCANNER\033[0m        Recon + vendor detection     \033[1;35m║\033[0m")
            print("\033[1;35m║  \033[1;36m7\033[0m)  \033[1;31m💀 ROUTER STRESS TEST\033[0m     6-vector hardware attack     \033[1;35m║\033[0m")
            print("\033[1;35m║  \033[1;36m8\033[0m)  \033[1;35m📻 BEACON FLOOD\033[0m           Fake AP storm / WIDS test    \033[1;35m║\033[0m")
            print("\033[1;35m║  \033[1;36m9\033[0m)  \033[1;32m💾 VIEW RESULTS\033[0m           Show saved credentials      \033[1;35m║\033[0m")
            print("\033[1;35m║  \033[1;36mA\033[0m)  \033[1;31m⚡ AUTO BEAST MODE\033[0m        Scan → auto pick → attack    \033[1;35m║\033[0m")
            print("\033[1;35m║  \033[1;36mP\033[0m)  \033[1;31m💣 PROBE+EAPOL FLOOD\033[0m      3-type management flood      \033[1;35m║\033[0m")
            print("\033[1;35m║  \033[1;36m0\033[0m)  \033[1;37m🚪 EXIT & CLEANUP\033[0m         Restore MAC + kill procs     \033[1;35m║\033[0m")
            print("\033[1;35m║                                                                  ║\033[0m")
            print(f"\033[1;35m║  \033[1;32m📡 {mon:<10}\033[0m \033[1;33m🎯 Nets:{nets:<4}\033[0m \033[1;31m🔑 Creds:{creds:<3}\033[0m \033[1;35mCtrl+C=stop  ║\033[0m")
            print("\033[1;35m╚══════════════════════════════════════════════════════════════════╝\033[0m")

            choice = input("\n\033[1;36m[?] Select (0-9): \033[0m").strip()

            actions = {
                "1": self.attacker.single_target_attack,
                "2": self.attacker.mass_deauth_with_skip,
                "3": self.attacker.mass_destruction,
                "4": self.crack_menu,
                "5": self.attacker.advanced_evil_twin,
                "6": self.scan_menu,
                "7": self.attacker.router_destroyer,
                "8": self.attacker.beacon_flood,
                "9": self.view_results,
                "a": self.auto_beast_mode,
                "p": self.attacker.probe_eapol_flood,
                "0": self.core.nuclear_cleanup,
            }

            fn = actions.get(choice.lower())
            if fn:
                try:
                    fn()
                except KeyboardInterrupt:
                    print()
                    self.core.stop_all_attacks()
                    self.core.clear_current_operation()
                except Exception as e:
                    print(f"\033[1;31m[✘] Error: {e}\033[0m")
                if choice != "0":
                    input("\n\033[1;33m[!] Press Enter to continue...\033[0m")
            else:
                print("\033[1;31m[✘] Invalid selection\033[0m")
                time.sleep(0.5)

    # ─────────────────────────────────────────────
    # CRACK SUBMENU
    # ─────────────────────────────────────────────

    def crack_menu(self):
        while True:
            os.system('clear')
            print(BANNER)
            print("\033[1;35m╔══════════════════════════════════════════════════════════════════╗\033[0m")
            print("\033[1;35m║                   🔓  CRACKING OPERATIONS                        ║\033[0m")
            print("\033[1;35m╠══════════════════════════════════════════════════════════════════╣\033[0m")
            print("\033[1;35m║  \033[1;36m1\033[0m) \033[1;33m⚡ AUTO CASCADE\033[0m      PMKID → WPS → Handshake           \033[1;35m║\033[0m")
            print("\033[1;35m║  \033[1;36m2\033[0m) \033[1;33m🤝 HANDSHAKE\033[0m         Force capture + crack              \033[1;35m║\033[0m")
            print("\033[1;35m║  \033[1;36m3\033[0m) \033[1;33m📡 WPS ATTACK\033[0m        Pixie Dust via bully/reaver        \033[1;35m║\033[0m")
            print("\033[1;35m║  \033[1;36m4\033[0m) \033[1;36m🗝️  WEP CRACK\033[0m         IV collection + aircrack-ng        \033[1;35m║\033[0m")
            print("\033[1;35m║  \033[1;36m5\033[0m) \033[1;37m↩  BACK\033[0m                                                 \033[1;35m║\033[0m")
            print("\033[1;35m╚══════════════════════════════════════════════════════════════════╝\033[0m")

            choice = input("\n\033[1;36m[?] Select: \033[0m").strip()
            if choice == "1":
                self.cracker.auto_crack_attack()
            elif choice == "2":
                self.cracker.handshake_capture_menu()
            elif choice == "3":
                self.cracker.wps_pin_attack()
            elif choice == "4":
                self.cracker.wep_crack_menu()
            elif choice == "5":
                break
            else:
                print("\033[1;31m[✘] Invalid\033[0m")
            if choice not in ("5",):
                input("\n\033[1;33m[!] Press Enter...\033[0m")

    # ─────────────────────────────────────────────
    # SCAN SUBMENU
    # ─────────────────────────────────────────────

    def scan_menu(self):
        while True:
            os.system('clear')
            print(BANNER)
            print("\033[1;35m╔══════════════════════════════════════════════════════════════════╗\033[0m")
            print("\033[1;35m║                   📡  SCANNER                                    ║\033[0m")
            print("\033[1;35m╠══════════════════════════════════════════════════════════════════╣\033[0m")
            print("\033[1;35m║  \033[1;36m1\033[0m) \033[1;32m⚡ QUICK SCAN\033[0m     10 seconds                           \033[1;35m║\033[0m")
            print("\033[1;35m║  \033[1;36m2\033[0m) \033[1;32m🔍 DEEP SCAN\033[0m      30 seconds                           \033[1;35m║\033[0m")
            print("\033[1;35m║  \033[1;36m3\033[0m) \033[1;32m👥 CLIENT SCAN\033[0m    Detect connected devices             \033[1;35m║\033[0m")
            print("\033[1;35m║  \033[1;36m4\033[0m) \033[1;37m↩  BACK\033[0m                                              \033[1;35m║\033[0m")
            print("\033[1;35m╚══════════════════════════════════════════════════════════════════╝\033[0m")

            choice = input("\n\033[1;36m[?] Select: \033[0m").strip()
            if choice == "1":
                if self.scanner.wifi_scan(10):
                    self.scanner.display_scan_results()
            elif choice == "2":
                if self.scanner.wifi_scan(30):
                    self.scanner.display_scan_results()
            elif choice == "3":
                self.scanner.client_detection_scan()
            elif choice == "4":
                break
            else:
                print("\033[1;31m[✘] Invalid\033[0m")
            if choice != "4":
                input("\n\033[1;33m[!] Press Enter...\033[0m")

    # ─────────────────────────────────────────────
    # AUTO BEAST MODE
    # ─────────────────────────────────────────────

    def auto_beast_mode(self):
        """
        Scan → auto-rank targets by exploitability → fire best attack.
        Priority: OPN (instant) → WEP (IV crack) → WPS-enabled → WPA2 cascade.
        """
        print("\033[1;31m╔══════════════════════════════════════════════════════════════════╗\033[0m")
        print("\033[1;31m║             ⚡  AUTO BEAST MODE — INITIALIZING                   ║\033[0m")
        print("\033[1;31m╚══════════════════════════════════════════════════════════════════╝\033[0m")

        print("\033[1;36m[→] Scanning for targets (20 s)...\033[0m")
        if not self.scanner.wifi_scan(20):
            print("\033[1;31m[✘] No networks found\033[0m")
            return

        nets = list(self.scanner.networks.values())
        if not nets:
            print("\033[1;31m[✘] No networks found\033[0m")
            return

        def vuln_score(n):
            enc = n.get('encryption', '')
            if 'OPN' in enc or enc.strip() == '':
                return 100
            if 'WEP' in enc and 'WPA' not in enc:
                return 80
            # WPS-capable check (fast scan)
            r = self.core.run_command(
                f"timeout 5 wash -i {self.core.mon_interface} -s -C 2>/dev/null"
            )
            if r and n['bssid'] in (r.stdout or ''):
                return 60
            if 'WPA2' in enc:
                return 20
            return 10

        print("\033[1;36m[→] Ranking targets by exploitability...\033[0m")
        ranked = sorted(nets, key=vuln_score, reverse=True)

        print()
        print("\033[1;35m┌────┬──────────────────────┬──────────────────────────┬────────────┐\033[0m")
        print("\033[1;35m│ #  │ SSID                  │ BSSID                    │ REASON     │\033[0m")
        print("\033[1;35m├────┼──────────────────────┼──────────────────────────┼────────────┤\033[0m")
        for i, n in enumerate(ranked[:5], 1):
            enc = n.get('encryption', '')
            if 'OPN' in enc or enc.strip() == '':
                reason = "OPEN"
            elif 'WEP' in enc and 'WPA' not in enc:
                reason = "WEP"
            elif 'WPA2' in enc:
                reason = "WPA2"
            else:
                reason = enc[:8]
            print(f"\033[1;35m│ \033[1;36m{i:2d}\033[0m \033[1;37m{n['essid'][:20]:<20}\033[0m \033[1;32m{n['bssid']}\033[0m \033[1;31m{reason:<10}\033[0m\033[1;35m│\033[0m")
        print("\033[1;35m└────┴──────────────────────┴──────────────────────────┴────────────┘\033[0m")

        target = ranked[0]
        enc    = target.get('encryption', '')
        print(f"\n\033[1;31m[⚡] AUTO TARGET: {target['essid']} ({target['bssid']})\033[0m")

        if 'OPN' in enc or enc.strip() == '':
            print("\033[1;33m[→] Open network — launching Evil Twin immediately\033[0m")
            self.attacker.router_brand = self.attacker._brand(target['bssid'])
            self.attacker._start_evil_twin(target, None)

        elif 'WEP' in enc and 'WPA' not in enc:
            print("\033[1;33m[→] WEP detected — launching IV crack\033[0m")
            self.cracker.wep_attack(target)

        else:
            print("\033[1;33m[→] WPA2 detected — launching PMKID → WPS → Handshake cascade\033[0m")
            self.cracker._cascade(target)

    # ─────────────────────────────────────────────
    # VIEW SAVED RESULTS
    # ─────────────────────────────────────────────

    def view_results(self):
        print("\033[1;35m╔══════════════════════════════════════════════════════════════════╗\033[0m")
        print("\033[1;35m║                   💾  SAVED CREDENTIALS                          ║\033[0m")
        print("\033[1;35m╚══════════════════════════════════════════════════════════════════╝\033[0m")

        # Collect from both sources — persistent first, then temp
        session_file = os.path.expanduser("~/netstrike/cracked.txt")
        temp_file    = "/tmp/ns_cracked.txt"

        lines = set()
        for path in [session_file, temp_file]:
            if os.path.exists(path):
                try:
                    with open(path) as f:
                        for l in f:
                            l = l.strip()
                            if l:
                                lines.add(l)
                except Exception:
                    pass

        if lines:
            print(f"\033[1;32m[✓] {len(lines)} credential(s) found:\033[0m\n")
            for l in sorted(lines):
                print(f"\033[1;32m  {l}\033[0m")
            print(f"\n\033[1;34m[📁] Persistent file: {session_file}\033[0m")
        else:
            print("\033[1;33m[!] No saved credentials yet\033[0m")

    # ─────────────────────────────────────────────
    # STARTUP
    # ─────────────────────────────────────────────

    def run(self):
        try:
            signal.signal(signal.SIGINT, self.core.signal_handler)
            os.system('clear')
            print(BANNER)

            if not self.core.check_root():
                return

            # Auto-install all dependencies — no user action needed
            installer = ToolInstaller(self.core)
            installer.install_required_tools()

            self.core.check_dependencies()

            if not self.core.select_interface():
                print("\033[1;31m[✘] No interface selected\033[0m")
                return

            self.core.save_original_config()

            if self.core.setup_monitor_mode():
                self.core.start_advanced_spoofing()
                print(f"\033[1;32m[✓] Ready  |  Monitor: {self.core.mon_interface}\033[0m")
                input("\n\033[1;36m[!] Press Enter to enter operations center...\033[0m")
                self.main_menu()
            else:
                print("\033[1;31m[✘] Monitor mode setup failed\033[0m")
                self.core.nuclear_cleanup()

        except Exception as e:
            print(f"\033[1;31m[✘] Fatal: {e}\033[0m")
            self.core.nuclear_cleanup()


if __name__ == "__main__":
    NetStrike().run()
