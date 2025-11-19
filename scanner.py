#!/usr/bin/env python3

import os
import time
import subprocess
import threading
import re

class NetworkScanner:
    def __init__(self, core):
        self.core = core
        self.networks = {}
        self.clients = {}
        self.scan_process = None
        self.scanning = False

    def wifi_scan(self, duration=15):
        """Wifite-style reliable scanning"""
        print("\033[1;36m[→] Starting reliable network scan...\033[0m")
        
        if not self.core.mon_interface:
            print("\033[1;31m[✘] No monitor interface available\033[0m")
            return False
        
        # Always reset data
        self.networks = {}
        self.clients = {}
        
        # Kill any existing scans
        self.stop_scan()
        time.sleep(2)
        
        return self.real_time_scan(duration)

    def real_time_scan(self, duration):
        """Real-time scanning like Wifite"""
        try:
            scan_file = f"/tmp/netstrike_scan_{int(time.time())}"
            
            # Build airodump command
            cmd = [
                "airodump-ng",
                self.core.mon_interface,
                "--output-format", "csv",
                "-w", scan_file,
                "--write-interval", "2"
            ]
            
            print("\033[1;32m[✓] Scan started\033[0m")
            
            # Start airodump
            self.scan_process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # Monitor scan progress
            start_time = time.time()
            networks_found = 0
            
            while time.time() - start_time < duration:
                elapsed = int(time.time() - start_time)
                remaining = duration - elapsed
                
                # Parse current results
                current_networks = self.parse_scan_file(f"{scan_file}-01.csv")
                if current_networks:
                    networks_found = len(current_networks)
                    self.show_scan_progress(current_networks, elapsed, duration, networks_found)
                
                time.sleep(3)
            
            # Stop scanning
            self.stop_scan()
            
            # Final parse
            self.networks = self.parse_scan_file(f"{scan_file}-01.csv")
            
            if self.networks:
                print(f"\033[1;32m[✓] Scan complete: {len(self.networks)} networks found\033[0m")
                return True
            else:
                print("\033[1;31m[✘] No networks found\033[0m")
                return False
                
        except Exception as e:
            print(f"\033[1;31m[✘] Scan error: {e}\033[0m")
            self.stop_scan()
            return False

    def parse_scan_file(self, csv_file):
        """Parse airodump CSV file"""
        networks = {}
        if not os.path.exists(csv_file):
            return {}
        
        try:
            with open(csv_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            lines = content.split('\n')
            count = 0
            in_networks = True
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                if 'Station MAC' in line:
                    in_networks = False
                    continue
                    
                if not in_networks:
                    continue
                    
                if 'BSSID' in line:
                    continue
                
                # Parse CSV line
                parts = [p.strip() for p in line.split(',')]
                if len(parts) >= 14:
                    bssid = parts[0]
                    if self.is_valid_bssid(bssid):
                        count += 1
                        
                        # Extract data with better error handling
                        channel = parts[3] if len(parts) > 3 else "1"
                        speed = parts[4] if len(parts) > 4 else "?"
                        encryption = parts[5] if len(parts) > 5 else "OPN"
                        power = parts[8] if len(parts) > 8 else "-1"
                        essid = parts[13].replace('"', '') if len(parts) > 13 else "HIDDEN"
                        
                        if not essid or essid in ["", "--"]:
                            essid = "HIDDEN"
                        
                        networks[count] = {
                            'bssid': bssid,
                            'channel': channel,
                            'power': power,
                            'encryption': encryption,
                            'essid': essid,
                            'speed': speed
                        }
            
            return networks
            
        except Exception:
            return {}

    def show_scan_progress(self, networks, elapsed, total, count):
        """Show scan progress"""
        os.system('clear')
        print("\033[1;35m")
        print("╔══════════════════════════════════════════════════════════════════╗")
        print("║                       NETWORK SCAN IN PROGRESS                  ║")
        print("╚══════════════════════════════════════════════════════════════════╝")
        print("\033[0m")
        
        progress = int((elapsed / total) * 50)
        bar = "[" + "█" * progress + "▒" * (50 - progress) + "]"
        print(f"\033[1;36m[⏳] Progress: {bar} {elapsed}/{total}s\033[0m")
        print(f"\033[1;32m[📶] Networks found: {count}\033[0m")
        print()
        
        if networks:
            print("\033[1;35m┌────┬──────────────────────┬────┬─────┬───────────┬──────────────────────────┐\033[0m")
            print("\033[1;35m│ \033[1;37m#  │ MAC Address           │ CH │ PWR │ ENCRYPTION │ NETWORK NAME\033[1;35m             │\033[0m")
            print("\033[1;35m├────┼──────────────────────┼────┼─────┼───────────┼──────────────────────────┤\033[0m")
            
            for idx, net_info in list(networks.items())[:8]:
                bssid = net_info['bssid']
                channel = net_info['channel']
                power = net_info['power']
                encryption = net_info['encryption']
                essid = net_info['essid']
                
                # Format display
                if essid == "HIDDEN":
                    display_name = "\033[1;31m🚫 HIDDEN\033[0m"
                else:
                    display_name = f"\033[1;37m{essid:.20}\033[0m" + ("..." if len(essid) > 20 else "")
                
                # Encryption icon
                if "WPA2" in encryption:
                    enc_icon = "🔒"
                    enc_color = "\033[1;31m"
                elif "WPA" in encryption:
                    enc_icon = "🔐"
                    enc_color = "\033[1;35m"
                elif "WEP" in encryption:
                    enc_icon = "🗝️"
                    enc_color = "\033[1;36m"
                else:
                    enc_icon = "🔓"
                    enc_color = "\033[1;33m"
                
                enc_display = f"{enc_icon} {encryption.split()[0] if ' ' in encryption else encryption}"
                
                print(f"\033[1;35m│ \033[1;36m{idx:2d}\033[0m \033[1;32m{bssid}\033[0m \033[1;33m{channel:>3}\033[0m \033[1;31m{power:>3}\033[0m {enc_color}{enc_display:10}\033[0m {display_name:24} \033[1;35m│\033[0m")
            
            print("\033[1;35m└────┴──────────────────────┴────┴─────┴───────────┴──────────────────────────┘\033[0m")
            
            if len(networks) > 8:
                print(f"\033[1;33m[📶] ... and {len(networks) - 8} more networks\033[0m")
        
        print(f"\033[1;36m[🔍] Scanning... Press Ctrl+C to cancel\033[0m")

    def stop_scan(self):
        """Stop any running scan"""
        if self.scan_process:
            self.scan_process.terminate()
            self.scan_process.wait()
        self.core.run_command("killall airodump-ng 2>/dev/null")

    def is_valid_bssid(self, bssid):
        """Validate BSSID format"""
        if not bssid or len(bssid) != 17:
            return False
        if bssid.count(':') != 5:
            return False
        if bssid == '00:00:00:00:00:00':
            return False
        return True

    def display_scan_results(self):
        """Display scan results"""
        if not self.networks:
            print("\033[1;31m[✘] No networks to display\033[0m")
            return
        
        print("\033[1;35m")
        print("╔══════════════════════════════════════════════════════════════════╗")
        print("║                       NETWORK DISCOVERY REPORT                  ║")
        print("╚══════════════════════════════════════════════════════════════════╝")
        print("\033[0m")
        
        print(f"\033[1;32m[✅] Networks found: {len(self.networks)}\033[0m")
        print()
        
        print("\033[1;35m┌────┬──────────────────────┬────┬─────┬───────────┬──────────────────────────┐\033[0m")
        print("\033[1;35m│ \033[1;37m#  │ MAC Address           │ CH │ PWR │ ENCRYPTION │ NETWORK NAME\033[1;35m             │\033[0m")
        print("\033[1;35m├────┼──────────────────────┼────┼─────┼───────────┼──────────────────────────┤\033[0m")
        
        for idx, net_info in self.networks.items():
            bssid = net_info['bssid']
            channel = net_info['channel']
            power = net_info['power']
            encryption = net_info['encryption']
            essid = net_info['essid']
            
            if essid == "HIDDEN":
                display_name = "\033[1;31m🚫 HIDDEN NETWORK\033[0m"
            else:
                display_name = f"\033[1;37m🎯 {essid:.18}\033[0m" + ("..." if len(essid) > 18 else "")
            
            if "WPA2" in encryption:
                enc_icon = "🔒"
                enc_color = "\033[1;31m"
            elif "WPA" in encryption:
                enc_icon = "🔐"
                enc_color = "\033[1;35m"
            elif "WEP" in encryption:
                enc_icon = "🗝️"
                enc_color = "\033[1;36m"
            else:
                enc_icon = "🔓"
                enc_color = "\033[1;33m"
            
            enc_display = f"{enc_icon} {encryption.split()[0] if ' ' in encryption else encryption}"
            
            print(f"\033[1;35m│ \033[1;36m{idx:2d}\033[0m \033[1;32m{bssid}\033[0m \033[1;33m{channel:>3}\033[0m \033[1;31m{power:>3}\033[0m {enc_color}{enc_display:10}\033[0m {display_name:24} \033[1;35m│\033[0m")
        
        print("\033[1;35m└────┴──────────────────────┴────┴─────┴───────────┴──────────────────────────┘\033[0m")

    def select_target(self):
        """Select target network"""
        if not self.networks:
            print("\033[1;31m[✘] No networks available\033[0m")
            return None
        
        try:
            selection = input("\n\033[1;36m[?] Select target (1-{}): \033[0m".format(len(self.networks)))
            idx = int(selection)
            
            if 1 <= idx <= len(self.networks):
                target = self.networks[idx]
                print(f"\033[1;32m[✅] Target: {target['essid']}\033[0m")
                return target
            else:
                print("\033[1;31m[✘] Invalid selection\033[0m")
                return None
                
        except ValueError:
            print("\033[1;31m[✘] Invalid input\033[0m")
            return None

    def client_detection_scan(self):
        """Client detection scan"""
        print("\033[1;36m[→] Client detection requires a target network\033[0m")
        if self.wifi_scan(10):
            self.display_scan_results()

    def display_detailed_scan_results(self):
        """Detailed scan results"""
        self.display_scan_results()
