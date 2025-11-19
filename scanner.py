#!/usr/bin/env python3

import os
import time
import subprocess
import threading
import csv
import re
from typing import Dict, List

class NetworkScanner:
    def __init__(self, core):
        self.core = core
        self.networks = {}
        self.clients = {}
        self.scanning = False

    def wifi_scan(self, duration=15):
        """Advanced WiFi Scan with Hidden SSID Detection"""
        print("\033[1;36m[→] Initiating advanced network reconnaissance...\033[0m")
        
        if not self.core.mon_interface:
            print("\033[1;31m[✘] No monitor interface available\033[0m")
            return False
        
        # Clear previous data
        self.networks = {}
        
        print(f"\033[1;36m[📡] Scanning interface: {self.core.mon_interface}\033[0m")
        print(f"\033[1;36m[⏱️] Scan duration: {duration} seconds\033[0m")
        
        return self.advanced_real_time_scan(duration)

    def advanced_real_time_scan(self, duration):
        """Advanced real-time scanning with hidden SSID detection"""
        try:
            scan_file = "/tmp/netstrike_advanced_scan"
            subprocess.run(f"rm -f {scan_file}* 2>/dev/null", shell=True)
            
            # Enhanced airodump command for better detection
            cmd = [
                "airodump-ng",
                self.core.mon_interface,
                "--output-format", "csv",
                "-w", scan_file,
                "--write-interval", "1",
                "--band", "abg",
                "--showack"
            ]
            
            print("\033[1;32m[✓] Advanced scan initiated\033[0m")
            print("\033[1;36m[🔍] Capturing network data with enhanced detection...\033[0m")
            
            # Start airodump in background
            scan_process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # Show enhanced real-time progress
            start_time = time.time()
            while time.time() - start_time < duration:
                elapsed = int(time.time() - start_time)
                remaining = duration - elapsed
                
                # Update scan file and show progress
                self.update_advanced_display(scan_file, elapsed, duration)
                time.sleep(2)
            
            # Stop scanning
            scan_process.terminate()
            scan_process.wait()
            
            print("\033[1;32m[✓] Advanced scan complete\033[0m")
            return self.finalize_advanced_scan(scan_file)
            
        except Exception as e:
            print(f"\033[1;31m[✘] Scan failed: {e}\033[0m")
            return False

    def update_advanced_display(self, scan_file, elapsed, total):
        """Update advanced live display during scanning"""
        csv_file = f"{scan_file}-01.csv"
        
        if os.path.exists(csv_file) and os.path.getsize(csv_file) > 100:
            networks = self.parse_advanced_scan(csv_file)
            if networks:
                self.show_advanced_results(networks, elapsed, total)

    def parse_advanced_scan(self, csv_file):
        """Parse advanced scan results with hidden SSID detection"""
        networks = {}
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
                    # Parse client data
                    self.parse_client_data(line)
                    continue
                    
                if 'BSSID' in line:
                    continue
                
                parts = line.split(',')
                if len(parts) >= 14:
                    bssid = parts[0].strip()
                    if self.is_valid_bssid(bssid):
                        count += 1
                        
                        # Extract comprehensive network info
                        channel = parts[3].strip() if len(parts) > 3 else "1"
                        speed = parts[4].strip() if len(parts) > 4 else "?"
                        encryption = parts[5].strip() if len(parts) > 5 else "OPN"
                        power = parts[8].strip() if len(parts) > 8 else "-1"
                        beacons = parts[9].strip() if len(parts) > 9 else "0"
                        iv = parts[10].strip() if len(parts) > 10 else "0"
                        essid = parts[13].strip().replace('"', '') if len(parts) > 13 else "HIDDEN_SSID"
                        
                        # Enhanced hidden SSID detection
                        if not essid or essid in ["", "--", " "] or len(essid) == 0:
                            essid = self.detect_hidden_ssid(bssid, channel)
                        
                        # Get connected clients count
                        client_count = self.get_client_count(bssid)
                        
                        networks[count] = {
                            'bssid': bssid,
                            'channel': channel,
                            'power': power,
                            'encryption': encryption,
                            'essid': essid,
                            'speed': speed,
                            'beacons': beacons,
                            'iv': iv,
                            'clients': client_count
                        }
            
            return networks
            
        except Exception as e:
            return {}

    def detect_hidden_ssid(self, bssid, channel):
        """Attempt to detect hidden SSID"""
        try:
            # Set to target channel
            self.core.run_command(f"iwconfig {self.core.mon_interface} channel {channel}")
            time.sleep(0.5)
            
            # Use deauth to trigger SSID broadcast
            result = self.core.run_command(f"aireplay-ng --deauth 1 -a {bssid} {self.core.mon_interface} 2>/dev/null", timeout=5)
            time.sleep(1)
            
            # Quick scan for revealed SSID
            result = self.core.run_command(f"airodump-ng --bssid {bssid} -c {channel} --write /tmp/hidden_scan {self.core.mon_interface} 2>/dev/null", timeout=3)
            
            # Check if SSID was revealed
            if os.path.exists("/tmp/hidden_scan-01.csv"):
                with open("/tmp/hidden_scan-01.csv", 'r') as f:
                    content = f.read()
                    lines = content.split('\n')
                    for line in lines:
                        if bssid in line:
                            parts = line.split(',')
                            if len(parts) > 13:
                                detected_ssid = parts[13].strip().replace('"', '')
                                if detected_ssid and detected_ssid not in ["", "--"]:
                                    return f"HIDDEN[{detected_ssid}]"
            
            return "🚫 HIDDEN_NETWORK"
            
        except:
            return "🚫 HIDDEN_NETWORK"

    def get_client_count(self, bssid):
        """Count clients connected to a network"""
        count = 0
        for client_bssid, client_info in self.clients.items():
            if client_info.get('bssid') == bssid:
                count += 1
        return count

    def parse_client_data(self, line):
        """Parse client/probe data from airodump"""
        parts = line.split(',')
        if len(parts) >= 6:
            client_mac = parts[0].strip()
            if self.is_valid_bssid(client_mac):
                power = parts[3].strip() if len(parts) > 3 else "-1"
                packets = parts[4].strip() if len(parts) > 4 else "0"
                bssid = parts[5].strip() if len(parts) > 5 else "Not Associated"
                
                self.clients[client_mac] = {
                    'power': power,
                    'packets': packets,
                    'bssid': bssid
                }

    def show_advanced_results(self, networks, elapsed, total):
        """Show advanced scanning results"""
        os.system('clear')
        
        # Modern Banner
        print("\033[1;35m")
        print("╔══════════════════════════════════════════════════════════════════╗")
        print("║                   🌐 NETSTRIKE NETWORK SCAN                     ║")
        print("║                   📊 ADVANCED DETECTION ACTIVE                  ║")
        print("╚══════════════════════════════════════════════════════════════════╝")
        print("\033[0m")
        
        # Progress with modern style
        progress = int((elapsed / total) * 50)
        bar = "[" + "█" * progress + "▒" * (50 - progress) + "]"
        print(f"\033[1;36m[⏳] SCAN PROGRESS: {bar} {elapsed}/{total}s\033[0m")
        print(f"\033[1;32m[✅] NETWORKS DETECTED: {len(networks)}\033[0m")
        print(f"\033[1;33m[👥] CLIENTS DETECTED: {len(self.clients)}\033[0m")
        print()
        
        # Display networks with enhanced information
        if networks:
            print("\033[1;35m┌────┬──────────────────────┬────┬─────┬───────────┬──────┬────────┬──────────────────────────┐\033[0m")
            print("\033[1;35m│ \033[1;37m#  │ MAC Address           │ CH │ PWR │ ENCRYPTION │ CLIS │ SPEED  │ NETWORK NAME\033[1;35m             │\033[0m")
            print("\033[1;35m├────┼──────────────────────┼────┼─────┼───────────┼──────┼────────┼──────────────────────────┤\033[0m")
            
            for idx, net_info in list(networks.items())[:10]:  # Show first 10
                bssid = net_info['bssid']
                channel = net_info['channel']
                power = net_info['power']
                encryption = net_info['encryption']
                essid = net_info['essid']
                clients = net_info['clients']
                speed = net_info['speed']
                
                # Modern formatting
                if "HIDDEN" in essid:
                    display_name = f"\033[1;31m{essid:.18}\033[0m" + ("..." if len(essid) > 18 else "")
                else:
                    display_name = f"\033[1;37m{essid:.18}\033[0m" + ("..." if len(essid) > 18 else "")
                
                # Enhanced encryption styling
                enc_icon = "🔓"
                enc_color = "\033[1;33m"
                if "WPA2" in encryption:
                    enc_icon = "🔒"
                    enc_color = "\033[1;31m"
                elif "WPA" in encryption:
                    enc_icon = "🔐"
                    enc_color = "\033[1;35m"
                elif "WEP" in encryption:
                    enc_icon = "🗝️"
                    enc_color = "\033[1;36m"
                
                enc_display = f"{enc_icon} {encryption.split()[0] if ' ' in encryption else encryption}"
                
                # Client count indicator
                client_icon = "👤" if clients == 1 else "👥" if clients > 1 else "👻"
                
                print(f"\033[1;35m│ \033[1;36m{idx:2d}\033[0m \033[1;32m{bssid}\033[0m \033[1;33m{channel:>3}\033[0m \033[1;31m{power:>3}\033[0m {enc_color}{enc_display:10}\033[0m {client_icon} {clients:>2} \033[1;34m{speed:>6}\033[0m {display_name:24} \033[1;35m│\033[0m")
            
            print("\033[1;35m└────┴──────────────────────┴────┴─────┴───────────┴──────┴────────┴──────────────────────────┘\033[0m")
            
            if len(networks) > 10:
                print(f"\033[1;33m[📶] ... and {len(networks) - 10} more networks detected\033[0m")
        
        print(f"\033[1;36m[🔍] Scanning continues... Press Ctrl+C to abort\033[0m")

    def finalize_advanced_scan(self, scan_file):
        """Finalize and display complete scan results"""
        csv_file = f"{scan_file}-01.csv"
        
        if not os.path.exists(csv_file):
            print("\033[1;31m[✘] Scan data not found\033[0m")
            return False
        
        # Parse final results
        self.networks = self.parse_final_scan(csv_file)
        
        if not self.networks:
            print("\033[1;31m[✘] No networks captured\033[0m")
            return False
        
        print(f"\033[1;32m[🎯] Scan mission accomplished: {len(self.networks)} targets acquired\033[0m")
        print(f"\033[1;33m[👥] Connected clients detected: {len(self.clients)}\033[0m")
        return True

    def parse_final_scan(self, csv_file):
        """Parse final scan results"""
        networks = {}
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
                
                parts = line.split(',')
                if len(parts) >= 14:
                    bssid = parts[0].strip()
                    if self.is_valid_bssid(bssid):
                        count += 1
                        
                        channel = parts[3].strip() if len(parts) > 3 else "1"
                        speed = parts[4].strip() if len(parts) > 4 else "?"
                        encryption = parts[5].strip() if len(parts) > 5 else "OPN"
                        power = parts[8].strip() if len(parts) > 8 else "-1"
                        beacons = parts[9].strip() if len(parts) > 9 else "0"
                        iv = parts[10].strip() if len(parts) > 10 else "0"
                        essid = parts[13].strip().replace('"', '') if len(parts) > 13 else "HIDDEN_SSID"
                        
                        if not essid or essid == "--":
                            essid = "🚫 HIDDEN_NETWORK"
                        
                        client_count = self.get_client_count(bssid)
                        
                        networks[count] = {
                            'bssid': bssid,
                            'channel': channel,
                            'power': power,
                            'encryption': encryption,
                            'essid': essid,
                            'speed': speed,
                            'beacons': beacons,
                            'iv': iv,
                            'clients': client_count
                        }
            
            return networks
            
        except Exception as e:
            print(f"\033[1;31m[✘] Final parse error: {e}\033[0m")
            return {}

    def is_valid_bssid(self, bssid):
        """Validate BSSID format"""
        return (len(bssid) == 17 and 
                bssid.count(':') == 5 and 
                bssid != '00:00:00:00:00:00')

    def display_scan_results(self):
        """Display final scan results in modern style"""
        if not self.networks:
            print("\033[1;31m[✘] No targets to display\033[0m")
            return
        
        print("\033[1;35m")
        print("╔══════════════════════════════════════════════════════════════════╗")
        print("║                   📊 NETWORK DISCOVERY REPORT                   ║")
        print("║                   🎯 TARGET ACQUISITION COMPLETE                ║")
        print("╚══════════════════════════════════════════════════════════════════╝")
        print("\033[0m")
        
        print(f"\033[1;32m[✅] TOTAL NETWORKS: {len(self.networks)}\033[0m")
        print(f"\033[1;33m[👥] CONNECTED CLIENTS: {len(self.clients)}\033[0m")
        print()
        
        print("\033[1;35m┌────┬──────────────────────┬────┬─────┬───────────┬──────┬────────┬──────────────────────────┐\033[0m")
        print("\033[1;35m│ \033[1;37m#  │ MAC Address           │ CH │ PWR │ ENCRYPTION │ CLIS │ SPEED  │ NETWORK NAME\033[1;35m             │\033[0m")
        print("\033[1;35m├────┼──────────────────────┼────┼─────┼───────────┼──────┼────────┼──────────────────────────┤\033[0m")
        
        for idx, net_info in self.networks.items():
            bssid = net_info['bssid']
            channel = net_info['channel']
            power = net_info['power']
            encryption = net_info['encryption']
            essid = net_info['essid']
            clients = net_info['clients']
            speed = net_info['speed']
            
            if "HIDDEN" in essid:
                display_name = f"\033[1;31m🚫 {essid:.16}\033[0m" + ("..." if len(essid) > 16 else "")
            else:
                display_name = f"\033[1;37m🎯 {essid:.16}\033[0m" + ("..." if len(essid) > 16 else "")
            
            # Modern encryption styling
            enc_icon = "🔓"
            enc_color = "\033[1;33m"
            if "WPA2" in encryption:
                enc_icon = "🔒"
                enc_color = "\033[1;31m"
            elif "WPA" in encryption:
                enc_icon = "🔐"
                enc_color = "\033[1;35m"
            elif "WEP" in encryption:
                enc_icon = "🗝️"
                enc_color = "\033[1;36m"
            
            enc_display = f"{enc_icon} {encryption.split()[0] if ' ' in encryption else encryption}"
            
            # Client indicator
            client_icon = "👤" if clients == 1 else "👥" if clients > 1 else "👻"
            
            print(f"\033[1;35m│ \033[1;36m{idx:2d}\033[0m \033[1;32m{bssid}\033[0m \033[1;33m{channel:>3}\033[0m \033[1;31m{power:>3}\033[0m {enc_color}{enc_display:10}\033[0m {client_icon} {clients:>2} \033[1;34m{speed:>6}\033[0m {display_name:24} \033[1;35m│\033[0m")
        
        print("\033[1;35m└────┴──────────────────────┴────┴─────┴───────────┴──────┴────────┴──────────────────────────┘\033[0m")
        print("\033[1;32m[✅] Targets ready for security operations\033[0m")

    def display_detailed_scan_results(self):
        """Display detailed scan results with client information"""
        self.display_scan_results()
        
        if self.clients:
            print(f"\n\033[1;35m[👥] DETECTED CLIENTS: {len(self.clients)}\033[0m")
            print("\033[1;35m┌──────────────────────┬─────┬────────┬──────────────────────┐\033[0m")
            print("\033[1;35m│ \033[1;37mCLIENT MAC           │ PWR  │ PACKETS │ ASSOCIATED AP\033[1;35m         │\033[0m")
            print("\033[1;35m├──────────────────────┼─────┼────────┼──────────────────────┤\033[0m")
            
            for client_mac, client_info in list(self.clients.items())[:15]:  # Show first 15
                power = client_info['power']
                packets = client_info['packets']
                ap_bssid = client_info['bssid']
                
                # Find AP SSID if available
                ap_ssid = "Unknown"
                for net_info in self.networks.values():
                    if net_info['bssid'] == ap_bssid:
                        ap_ssid = net_info['essid']
                        break
                
                print(f"\033[1;35m│ \033[1;32m{client_mac}\033[0m \033[1;31m{power:>4}\033[0m \033[1;33m{packets:>7}\033[0m \033[1;36m{ap_ssid:.18}\033[0m \033[1;35m│\033[0m")
            
            print("\033[1;35m└──────────────────────┴─────┴────────┴──────────────────────┘\033[0m")

    def client_detection_scan(self):
        """Perform dedicated client detection scan"""
        print("\033[1;36m[→] Starting client detection scan...\033[0m")
        
        if self.wifi_scan(10):
            self.display_detailed_scan_results()

    def select_target(self):
        """Select target with modern interface"""
        if not self.networks:
            print("\033[1;31m[✘] No targets available\033[0m")
            return None
        
        print("\033[1;36m[🎯] Target selection required\033[0m")
        
        try:
            selection = input("\n\033[1;36m[?] Select target (1-{}): \033[0m".format(len(self.networks)))
            idx = int(selection)
            
            if 1 <= idx <= len(self.networks):
                target = self.networks[idx]
                print(f"\033[1;32m[✅] Target acquired: {target['essid']}\033[0m")
                print(f"\033[1;32m[📡] Target locked: {target['bssid']} | Channel: {target['channel']}\033[0m")
                print(f"\033[1;33m[👥] Connected clients: {target['clients']}\033[0m")
                return target
            else:
                print("\033[1;31m[✘] Invalid target selection\033[0m")
                return None
                
        except ValueError:
            print("\033[1;31m[✘] Invalid input - enter target number\033[0m")
            return None
