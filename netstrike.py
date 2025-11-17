#!/usr/bin/env python3
"""
NETSTRIKE FRAMEWORK v2.0 ULTIMATE
by ZEROHAVEN SECURITY
Advanced Wireless Penetration Suite
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

class NetStrike:
    def __init__(self):
        self.core = NetStrikeCore()
        self.scanner = NetworkScanner(self.core)
        self.attacker = AttackManager(self.core, self.scanner)
        self.cracker = PasswordCracker(self.core, self.scanner)
        self.installer = ToolInstaller(self.core)
        
    def display_banner(self):
        print("""
\033[1;31m
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║    ███╗   ██╗███████╗████████╗███████╗████████╗██████╗ ██╗██╗   ║
║    ████╗  ██║██╔════╝╚══██╔══╝██╔════╝╚══██╔══╝██╔══██╗██║██║   ║
║    ██╔██╗ ██║█████╗     ██║   █████╗     ██║   ██████╔╝██║██║   ║
║    ██║╚██╗██║██╔══╝     ██║   ██╔══╝     ██║   ██╔══██╗██║██║   ║
║    ██║ ╚████║███████╗   ██║   ███████╗   ██║   ██║  ██║██║███████╗
║    ╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝╚══════╝
║                                                                  ║
║    ██████╗ ███████╗██████╗  ██████╗                             ║
║    ██╔══██╗██╔════╝██╔══██╗██╔═══██╗                            ║
║    ██████╔╝█████╗  ██████╔╝██║   ██║                            ║
║    ██╔══██╗██╔══╝  ██╔══██╗██║   ██║                            ║
║    ██║  ██║███████╗██║  ██║╚██████╔╝                            ║
║    ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝ ╚═════╝                             ║
║                                                                  ║
║              🚀 ZEROHAVEN SECURITY PRESENTS                     ║
║                 N E T S T R I K E   v 2.0 ULTIMATE              ║
║           U L T I M A T E   W I R E L E S S   S U I T E         ║
║               C O M P L E T E   A N O N Y M I T Y               ║
║                    N U C L E A R   P O W E R                    ║
║                    R O U T E R   D E S T R O Y E R              ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
\033[0m
        """)

    def hacker_animation(self):
        messages = [
            "🛡️   ESTABLISHING SECURE CONNECTION...",
            "🔒   ENCRYPTING DATA STREAMS...", 
            "🌐   BYPASSING SECURITY PROTOCOLS...",
            "📡   ACTIVATING ANONYMOUS TUNNEL...",
            "🔄   WIPING DIGITAL FOOTPRINTS...",
            "✅   SECURE SESSION ESTABLISHED"
        ]
        for msg in messages:
            print(f"\033[1;36m[⚡] \033[1;32m{msg}\033[0m")
            time.sleep(0.8)

    def main_menu(self):
        while True:
            self.display_banner()
            print("\033[1;31m╔══════════════════════════════════════════════════════════════════╗\033[0m")
            print("\033[1;31m║                  🚀 NETSTRIKE ULTIMATE MENU                     ║\033[0m")
            print("\033[1;31m╠══════════════════════════════════════════════════════════════════╣\033[0m")
            print("\033[1;31m║                                                                  ║\033[0m")
            print("\033[1;31m║ \033[1;33m1\033[0m) \033[1;31m💀 FREEZE WI-FI & BLUETOOTH\033[0m   - Complete network freezing  \033[1;31m║\033[0m")
            print("\033[1;31m║ \033[1;33m2\033[0m) \033[1;36m🔓 CRACK WI-FI\033[0m               - Password extraction         \033[1;31m║\033[0m")
            print("\033[1;31m║ \033[1;33m3\033[0m) \033[1;35m👥 ADVANCED EVIL TWIN\033[0m        - Perfect replica + capture  \033[1;31m║\033[0m")
            print("\033[1;31m║ \033[1;33m4\033[0m) \033[1;34m📡 NETWORK SCANNER\033[0m           - Advanced detection         \033[1;31m║\033[0m")
            print("\033[1;31m║ \033[1;33m5\033[0m) \033[1;32m🚪 EXIT & CLEAN\033[0m              - No-existence mode          \033[1;31m║\033[0m")
            print("\033[1;31m║                                                                  ║\033[0m")
            print("\033[1;31m╚══════════════════════════════════════════════════════════════════╝\033[0m")
            print("\033[1;33m[💡] TIP: Press Ctrl+C during attacks to stop current operation only\033[0m")
            
            choice = input("\n\033[1;33m[?] SELECT NETSTRIKE OPTION: \033[0m").strip()
            
            if choice == "1":
                self.freeze_menu()
            elif choice == "2":
                self.crack_menu()
            elif choice == "3":
                self.attacker.advanced_evil_twin()
            elif choice == "4":
                self.scan_menu()
            elif choice == "5":
                self.cleanup()
            else:
                print("\033[1;31m[✘] INVALID OPTION\033[0m")
                input("\033[1;33m[!] PRESS ENTER TO CONTINUE...\033[0m")

    def freeze_menu(self):
        while True:
            self.display_banner()
            print("\033[1;31m╔══════════════════════════════════════════════════════════════════╗\033[0m")
            print("\033[1;31m║                  ☢️  NETSTRIKE FREEZE WEAPONS                   ║\033[0m")
            print("\033[1;31m╠══════════════════════════════════════════════════════════════════╣\033[0m")
            print("\033[1;31m║                                                                  ║\033[0m")
            print("\033[1;31m║ \033[1;33m1\033[0m) \033[1;31m💣 SINGLE TARGET FREEZE\033[0m      - Ultra-heavy single network \033[1;31m║\033[0m")
            print("\033[1;31m║ \033[1;33m2\033[0m) \033[1;31m🌪️  MASS NETWORK FREEZE\033[0m      - Freeze ALL found networks   \033[1;31m║\033[0m")
            print("\033[1;31m║ \033[1;33m3\033[0m) \033[1;31m💀 ULTRA MASS DESTRUCTION\033[0m    - Total WiFi annihilation    \033[1;31m║\033[0m")
            print("\033[1;31m║ \033[1;33m4\033[0m) \033[1;31m🔥 ROUTER DESTROYER\033[0m          - Permanent router damage    \033[1;31m║\033[0m")
            print("\033[1;31m║ \033[1;33m5\033[0m) \033[1;31m📱 BLUETOOTH ANNIHILATION\033[0m    - Destroy Bluetooth devices  \033[1;31m║\033[0m")
            print("\033[1;31m║ \033[1;33m6\033[0m) \033[1;35m👥 ADVANCED EVIL TWIN\033[0m        - Perfect replica + capture  \033[1;31m║\033[0m")
            print("\033[1;31m║ \033[1;33m7\033[0m) \033[1;32m↩️  BACK TO MAIN MENU\033[0m                                   \033[1;31m║\033[0m")
            print("\033[1;31m║                                                                  ║\033[0m")
            print("\033[1;31m╚══════════════════════════════════════════════════════════════════╝\033[0m")
            
            choice = input("\n\033[1;33m[?] SELECT WEAPON: \033[0m").strip()
            
            if choice == "1":
                self.attacker.single_target_attack()
            elif choice == "2":
                self.attacker.mass_destruction()
            elif choice == "3":
                self.attacker.ultra_mass_destruction()
            elif choice == "4":
                self.attacker.router_destroyer()
            elif choice == "5":
                self.attacker.bluetooth_attack()
            elif choice == "6":
                self.attacker.advanced_evil_twin()
            elif choice == "7":
                break
            else:
                print("\033[1;31m[✘] INVALID SELECTION\033[0m")
            
            input("\n\033[1;33m[!] PRESS ENTER TO CONTINUE...\033[0m")

    def crack_menu(self):
        while True:
            self.display_banner()
            print("\033[1;31m╔══════════════════════════════════════════════════════════════════╗\033[0m")
            print("\033[1;31m║                   ☢️  NETSTRIKE CRACKING SUITE                  ║\033[0m")
            print("\033[1;31m╠══════════════════════════════════════════════════════════════════╣\033[0m")
            print("\033[1;31m║                                                                  ║\033[0m")
            print("\033[1;31m║ \033[1;33m1\033[0m) \033[1;36m⚡ AUTO CRACKING\033[0m           - All methods automatically  \033[1;31m║\033[0m")
            print("\033[1;31m║ \033[1;33m2\033[0m) \033[1;36m🔓 WPA/WPA2 CRACKING\033[0m     - Handshake capture & crack   \033[1;31m║\033[0m")
            print("\033[1;31m║ \033[1;33m3\033[0m) \033[1;36m📡 WPS PIN ATTACK\033[0m        - WPS vulnerability exploit   \033[1;31m║\033[0m")
            print("\033[1;31m║ \033[1;33m4\033[0m) \033[1;32m↩️  BACK TO MAIN MENU\033[0m                                   \033[1;31m║\033[0m")
            print("\033[1;31m║                                                                  ║\033[0m")
            print("\033[1;31m╚══════════════════════════════════════════════════════════════════╝\033[0m")
            
            choice = input("\n\033[1;33m[?] SELECT ATTACK VECTOR: \033[0m").strip()
            
            if choice == "1":
                self.cracker.auto_crack_attack()
            elif choice == "2":
                self.cracker.handshake_capture_auto(None)
            elif choice == "3":
                self.cracker.wps_pin_attack()
            elif choice == "4":
                break
            else:
                print("\033[1;31m[✘] INVALID SELECTION\033[0m")
            
            input("\n\033[1;33m[!] PRESS ENTER TO CONTINUE...\033[0m")

    def scan_menu(self):
        while True:
            self.display_banner()
            print("\033[1;31m╔══════════════════════════════════════════════════════════════════╗\033[0m")
            print("\033[1;31m║                   📡 NETSTRIKE SCANNING SUITE                   ║\033[0m")
            print("\033[1;31m╠══════════════════════════════════════════════════════════════════╣\033[0m")
            print("\033[1;31m║                                                                  ║\033[0m")
            print("\033[1;31m║ \033[1;33m1\033[0m) \033[1;34m📶 WI-FI NETWORK SCAN\033[0m      - Discover all WiFi networks  \033[1;31m║\033[0m")
            print("\033[1;31m║ \033[1;33m2\033[0m) \033[1;34m📱 BLUETOOTH DEVICE SCAN\033[0m   - Discover Bluetooth devices  \033[1;31m║\033[0m")
            print("\033[1;31m║ \033[1;33m3\033[0m) \033[1;32m↩️  BACK TO MAIN MENU\033[0m                                   \033[1;31m║\033[0m")
            print("\033[1;31m║                                                                  ║\033[0m")
            print("\033[1;31m╚══════════════════════════════════════════════════════════════════╝\033[0m")
            
            choice = input("\n\033[1;33m[?] SELECT SCAN TYPE: \033[0m").strip()
            
            if choice == "1":
                print("\033[1;33m[!] INITIATING ADVANCED WI-FI SCAN...\033[0m")
                if self.scanner.wifi_scan():
                    self.scanner.display_scan_results()
            elif choice == "2":
                print("\033[1;33m[!] INITIATING BLUETOOTH RECONNAISSANCE...\033[0m")
                devices = self.scanner.bluetooth_scan()
                if devices:
                    self.scanner.display_bluetooth_results(devices)
                else:
                    print("\033[1;31m[✘] NO BLUETOOTH DEVICES FOUND\033[0m")
            elif choice == "3":
                break
            else:
                print("\033[1;31m[✘] INVALID SELECTION\033[0m")
            
            input("\n\033[1;33m[!] PRESS ENTER TO CONTINUE...\033[0m")

    def cleanup(self):
        print("\n\033[1;31m[☢️] INITIATING NO-EXISTENCE PROTOCOL...\033[0m")
        self.core.nuclear_cleanup()

    def run(self):
        try:
            # Set up signal handler
            signal.signal(signal.SIGINT, self.core.signal_handler)
            
            # Initialization
            print("\033[1;31m[☢️] INITIALIZING NETSTRIKE FRAMEWORK ULTIMATE...\033[0m")
            self.hacker_animation()
            
            # Check root and install tools
            if not self.core.check_root():
                return
            
            # Select wireless interface
            if not self.core.select_interface():
                print("\033[1;31m[✘] NO INTERFACE SELECTED - EXITING\033[0m")
                return
            
            self.installer.install_required_tools()
            self.core.save_original_config()
            
            if self.core.setup_monitor_mode():
                self.core.start_nuclear_spoofing()
                print("\033[1;32m[✓] NETSTRIKE FRAMEWORK ULTIMATE READY\033[0m")
                print("\033[1;32m[✓] ANONYMITY MODE: ACTIVE\033[0m")
                print(f"\033[1;32m[✓] MONITOR MODE: {self.core.mon_interface}\033[0m")
                print("\033[1;32m[✓] ULTRA DESTRUCTION WEAPONS: ARMED\033[0m")
                self.main_menu()
            else:
                print("\033[1;31m[✘] NETSTRIKE DEPLOYMENT FAILED\033[0m")
                self.cleanup()
                
        except Exception as e:
            print(f"\033[1;31m[✘] UNEXPECTED ERROR: {e}\033[0m")
            self.cleanup()

if __name__ == "__main__":
    netstrike = NetStrike()
    netstrike.run()
