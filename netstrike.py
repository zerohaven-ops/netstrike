#!/usr/bin/env python3
"""
NETSTRIKE FRAMEWORK v3.0 ULTIMATE
by ZEROHAVEN SECURITY
Modern Wireless Security Suite
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
\033[1;32m
╔══════════════════════════════════════════════════════════════════╗
║  ███╗   ██╗███████╗████████╗███████╗████████╗██████╗ ██╗██╗  ██╗  ║
║  ████╗  ██║██╔════╝╚══██╔══╝██╔════╝╚══██╔══╝██╔══██╗██║██║  ██║  ║
║  ██╔██╗ ██║█████╗     ██║   █████╗     ██║   ██████╔╝██║███████║  ║
║  ██║╚██╗██║██╔══╝     ██║   ██╔══╝     ██║   ██╔══██╗██║╚════██║  ║
║  ██║ ╚████║███████╗   ██║   ███████╗   ██║   ██║  ██║██║     ██║  ║
║  ╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝     ╚═╝  ║
║                                                                  ║
║                🚀 MODERN WIRELESS SECURITY SUITE                ║
║                      DARK CINEMATIC v3.0                        ║
║                      ZEROHAVEN SECURITY                         ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
\033[0m
        """)

    def cinematic_animation(self):
        messages = [
            "🔍 Initializing security protocols...",
            "🛡️  Establishing encrypted channels...", 
            "🌐 Bypassing network restrictions...",
            "📡 Activating stealth mode...",
            "⚡ Powering attack vectors...",
            "✅ System ready for operation"
        ]
        for msg in messages:
            print(f"\033[1;36m[→] \033[1;35m{msg}\033[0m")
            time.sleep(0.6)

    def main_menu(self):
        while True:
            os.system('clear')
            self.display_banner()
            
            print("\033[1;35m╔══════════════════════════════════════════════════════════════════╗\033[0m")
            print("\033[1;35m║                    🎯 SECURITY OPERATIONS MENU                   ║\033[0m")
            print("\033[1;35m╠══════════════════════════════════════════════════════════════════╣\033[0m")
            print("\033[1;35m║                                                                  ║\033[0m")
            print("\033[1;35m║ \033[1;36m1\033[0m) \033[1;31m📶 SINGLE WIFI JAMMING\033[0m       - Target specific network        \033[1;35m║\033[0m")
            print("\033[1;35m║ \033[1;36m2\033[0m) \033[1;31m🌐 MASS WIFI JAMMING\033[0m         - Disable all networks          \033[1;35m║\033[0m")
            print("\033[1;35m║ \033[1;36m3\033[0m) \033[1;33m🔓 PASSWORD CRACKING\033[0m         - Multiple attack methods       \033[1;35m║\033[0m")
            print("\033[1;35m║ \033[1;36m4\033[0m) \033[1;34m👥 ADVANCED EVIL TWIN\033[0m        - Professional AP cloning       \033[1;35m║\033[0m")
            print("\033[1;35m║ \033[1;36m5\033[0m) \033[1;32m📡 NETWORK SCANNER\033[0m           - Advanced detection           \033[1;35m║\033[0m")
            print("\033[1;35m║ \033[1;36m6\033[0m) \033[1;31m💀 ROUTER DESTROYER\033[0m          - Hardware stress test         \033[1;35m║\033[0m")
            print("\033[1;35m║ \033[1;36m7\033[0m) \033[1;37m🚪 EXIT & CLEAN\033[0m              - Secure termination           \033[1;35m║\033[0m")
            print("\033[1;35m║                                                                  ║\033[0m")
            print("\033[1;35m╚══════════════════════════════════════════════════════════════════╝\033[0m")
            print("\033[1;36m[💡] TIP: Use Ctrl+C to stop any running operation immediately\033[0m")
            
            choice = input("\n\033[1;36m[?] Select operation (1-7): \033[0m").strip()
            
            if choice == "1":
                self.attacker.single_target_attack()
            elif choice == "2":
                self.attacker.mass_destruction()
            elif choice == "3":
                self.crack_menu()
            elif choice == "4":
                self.attacker.advanced_evil_twin()
            elif choice == "5":
                self.scan_menu()
            elif choice == "6":
                self.attacker.router_destroyer()
            elif choice == "7":
                self.cleanup()
            else:
                print("\033[1;31m[✘] Invalid selection\033[0m")
                input("\033[1;33m[!] Press Enter to continue...\033[0m")

    def crack_menu(self):
        while True:
            os.system('clear')
            self.display_banner()
            print("\033[1;35m╔══════════════════════════════════════════════════════════════════╗\033[0m")
            print("\033[1;35m║                     🔓 CRACKING OPERATIONS                      ║\033[0m")
            print("\033[1;35m╠══════════════════════════════════════════════════════════════════╣\033[0m")
            print("\033[1;35m║                                                                  ║\033[0m")
            print("\033[1;35m║ \033[1;36m1\033[0m) \033[1;33m⚡ AUTO CRACKING\033[0m            - All methods automatically    \033[1;35m║\033[0m")
            print("\033[1;35m║ \033[1;36m2\033[0m) \033[1;33m🔍 WPA/WPA2 CRACKING\033[0m        - Handshake capture           \033[1;35m║\033[0m")
            print("\033[1;35m║ \033[1;36m3\033[0m) \033[1;33m📡 WPS PIN ATTACK\033[0m           - WPS vulnerability           \033[1;35m║\033[0m")
            print("\033[1;35m║ \033[1;36m4\033[0m) \033[1;37m↩️  BACK TO MAIN\033[0m                                      \033[1;35m║\033[0m")
            print("\033[1;35m║                                                                  ║\033[0m")
            print("\033[1;35m╚══════════════════════════════════════════════════════════════════╝\033[0m")
            
            choice = input("\n\033[1;36m[?] Select attack vector: \033[0m").strip()
            
            if choice == "1":
                self.cracker.auto_crack_attack()
            elif choice == "2":
                target = self.select_target_for_cracking()
                if target:
                    self.cracker.handshake_capture_auto(target)
            elif choice == "3":
                self.cracker.wps_pin_attack()
            elif choice == "4":
                break
            else:
                print("\033[1;31m[✘] Invalid selection\033[0m")
            
            input("\n\033[1;33m[!] Press Enter to continue...\033[0m")

    def scan_menu(self):
        while True:
            os.system('clear')
            self.display_banner()
            print("\033[1;35m╔══════════════════════════════════════════════════════════════════╗\033[0m")
            print("\033[1;35m║                     📡 SCANNING OPERATIONS                      ║\033[0m")
            print("\033[1;35m╠══════════════════════════════════════════════════════════════════╣\033[0m")
            print("\033[1;35m║                                                                  ║\033[0m")
            print("\033[1;35m║ \033[1;36m1\033[0m) \033[1;32m📶 QUICK NETWORK SCAN\033[0m        - Fast network discovery       \033[1;35m║\033[0m")
            print("\033[1;35m║ \033[1;36m2\033[0m) \033[1;32m🔍 DEEP NETWORK SCAN\033[0m         - Detailed network analysis    \033[1;35m║\033[0m")
            print("\033[1;35m║ \033[1;36m3\033[0m) \033[1;32m📊 CLIENT DETECTION\033[0m          - Connected device discovery   \033[1;35m║\033[0m")
            print("\033[1;35m║ \033[1;36m4\033[0m) \033[1;37m↩️  BACK TO MAIN\033[0m                                      \033[1;35m║\033[0m")
            print("\033[1;35m║                                                                  ║\033[0m")
            print("\033[1;35m╚══════════════════════════════════════════════════════════════════╝\033[0m")
            
            choice = input("\n\033[1;36m[?] Select scan type: \033[0m").strip()
            
            if choice == "1":
                print("\033[1;36m[→] Starting quick network scan...\033[0m")
                if self.scanner.wifi_scan(10):
                    self.scanner.display_scan_results()
            elif choice == "2":
                print("\033[1;36m[→] Starting deep network analysis...\033[0m")
                if self.scanner.wifi_scan(20):
                    self.scanner.display_detailed_scan_results()
            elif choice == "3":
                print("\033[1;36m[→] Scanning for connected clients...\033[0m")
                self.scanner.client_detection_scan()
            elif choice == "4":
                break
            else:
                print("\033[1;31m[✘] Invalid selection\033[0m")
            
            input("\n\033[1;33m[!] Press Enter to continue...\033[0m")

    def select_target_for_cracking(self):
        """Select target for cracking operations"""
        print("\033[1;36m[→] Scanning for available networks...\033[0m")
        if self.scanner.wifi_scan():
            return self.scanner.select_target()
        return None

    def cleanup(self):
        print("\n\033[1;35m[→] Initiating secure termination protocol...\033[0m")
        self.core.nuclear_cleanup()

    def run(self):
        try:
            # Set up signal handler
            signal.signal(signal.SIGINT, self.core.signal_handler)
            
            # Initialization
            print("\033[1;35m[→] Initializing NetStrike Framework v3.0...\033[0m")
            self.cinematic_animation()
            
            # Check root and install tools
            if not self.core.check_root():
                return
            
            # Select wireless interface
            if not self.core.select_interface():
                print("\033[1;31m[✘] No interface selected - exiting\033[0m")
                return
            
            self.installer.install_required_tools()
            self.core.save_original_config()
            
            if self.core.setup_monitor_mode():
                self.core.start_advanced_spoofing()
                print("\033[1;32m[✓] NetStrike Framework v3.0 ready\033[0m")
                print("\033[1;32m[✓] Stealth mode: ACTIVE\033[0m")
                print(f"\033[1;32m[✓] Monitor interface: {self.core.mon_interface}\033[0m")
                print("\033[1;32m[✓] Advanced spoofing: ENABLED\033[0m")
                input("\n\033[1;36m[!] Press Enter to continue to main menu...\033[0m")
                self.main_menu()
            else:
                print("\033[1;31m[✘] Framework deployment failed\033[0m")
                self.cleanup()
                
        except Exception as e:
            print(f"\033[1;31m[✘] Unexpected error: {e}\033[0m")
            self.cleanup()

if __name__ == "__main__":
    netstrike = NetStrike()
    netstrike.run()
