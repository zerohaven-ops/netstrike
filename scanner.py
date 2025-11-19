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
        self.current_scan_file = ""

    def wifi_scan(self, duration=15):
        """advanced-style continuous scanning with fresh data"""
        print("\033[1;36m[→] Initializing advanced-style network reconnaissance...\033[0m")
        
        if not self.core.mon_interface:
            print("\033[1;31m[✘] No monitor interface available\033[0m")
            return False
        
        # CRITICAL: Always reset scan data for fresh scan (advanced behavior)
        self.networks = {}
        self.clients = {}
        
        # Generate unique scan file for this session
        self.current_scan_file = f"/tmp/netstrike_scan_{int(time.time())}"
        
        print(f"\033[1;36m[📡] Scanning interface: {self.core.mon_interface}\033[0m")
        print(f"\033[1;36m[⏱️] Scan duration: {duration} seconds\033[0m")
        
        return self.advanced_style_continuous_scan(duration)

    def advanced_style_continuous_scan(self, duration):
        """advanced-style continuous scanning implementation"""
        try:
            # Clean up previous scan files
            subprocess.run(f"rm -f {self.current_scan_file}* 2>/dev/null", shell=True)
            
            # advanced-style airodump command
            cmd = [
                "airodump-ng",
                self.core.mon_interface,
                "--output-format", "csv",
                "-w", self.current_scan_file,
                "--write-interval", "1",
                "--band", "abg"
            ]
            
            print("\033[1;32m[✓] Continuous scan initiated (advanced-style)\033[0m")
            print("\033[1;36m[🔍] Actively discovering networks...\033[0m")
            
            # Kill any existing airodump processes
            self.core.run_command("killall airodump-ng 2>/dev/null")
            time.sleep(2)
            
            # Start airodump in background
            scan_process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # Continuous scanning with live updates (advanced behavior)
            start_time = time.time()
            last_network_count = 0
            
            while time.time() - start_time < duration:
                elapsed = int(time.time() - start_time)
                remaining = duration - elapsed
                
                # Update display with fresh data
                current_networks = self.parse_live_scan_data()
                current_count = len(current_networks)
                
                # Only update if network count changed (advanced optimization)
                if current_count != last_network_count:
                    self.show_advanced_style_results(current_networks, elapsed, duration)
                    last_network_count = current_count
                
                time.sleep(2)
            
            # Stop scanning
            scan_process.terminate()
            scan_process.wait()
            
            print("\033[1;32m[✓] Continuous scan complete\033[0m")
            return self.finalize_scan_results()
            
        except Exception as e:
            print(f"\033[1;31m[✘] Scan failed: {e}\033[0m")
            return False

    def parse_live_scan_data(self):
        """Parse live scan data from airodump CSV (advanced method)"""
        csv_file = f"{self.current_scan_file}-01.csv"
        networks = {}
        
        if not os.path.exists(csv_file) or os.path.getsize(csv_file) < 100:
            return networks
        
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
                    self.parse_client_data(line)
                    continue
                    
                if 'BSSID' in line:
                    continue
                
                parts = line.split(',')
                if len(parts) >= 14:
                    bssid = parts[0].strip()
                    if self.is_valid_bssid(bssid):
                        count += 1
                        
                        # Extract network information
                        channel = parts[3].strip() if len(parts) > 3 else "1"
                        speed = parts[4].strip() if len(parts) > 4 else "?"
                        encryption = parts[5].strip() if len(parts) > 5 else "OPN"
                        power = parts[8].strip() if len(parts) > 8 else "-1"
                        beacons = parts[9].strip() if len(parts) > 9 else "0"
                        essid = parts[13].strip().replace('"', '') if len(parts) > 13 else "HIDDEN_SSID"
                        
                        # Handle hidden networks
                        if not essid or essid in ["", "--", " "]:
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
                            'clients': client_count
                        }
            
            return networks
            
        except Exception:
            return {}

    def show_advanced_style_results(self, networks, elapsed, total):
        """Show advanced-style scanning results"""
        os.system('clear')
        
        print("\033[1;35m")
        print("╔══════════════════════════════════════════════════════════════════╗")
        print("║                   🌐 NETSTRIKE NETWORK SCAN                     ║")
        print("║                   📊 advanced-STYLE SCANNING                     ║")
        print("╚══════════════════════════════════════════════════════════════════╝")
        print("\033[0m")
        
        # Progress with advanced style
        progress = int((elapsed / total) * 50)
        bar = "[" + "█" * progress + "▒" * (50 - progress) + "]"
        print(f"\033[1;36m[⏳] SCAN PROGRESS: {bar} {elapsed}/{total}s\033[0m")
        print(f"\033[1;32m[✅] NETWORKS DETECTED: {len(networks)}\033[0m")
        print(f"\033[1;33m[👥] CLIENTS DETECTED: {len(self.clients)}\033[0m")
        print()
        
        # Display networks
        if networks:
            print("\033[1;35m┌────┬──────────────────────┬────┬─────┬───────────┬──────┬──────────────────────────┐\033[0m")
            print("\033[1;35m│ \033[1;37m#  │ MAC Address           │ CH │ PWR │ ENCRYPTION │ CLIS │ NETWORK NAME\033[1;35m             │\033[0m")
            print("\033[1;35m├────┼──────────────────────┼────┼─────┼───────────┼──────┼──────────────────────────┤\033[0m")
            
            for idx, net_info in list(networks.items())[:10]:
                bssid = net_info['bssid']
                channel = net_info['channel']
                power = net_info['power']
                encryption = net_info['encryption']
                essid = net_info['essid']
                clients = net_info['clients']
                
                # Format display name
                if "HIDDEN" in essid:
                    display_name = f"\033[1;31m{essid:.22}\033[0m"
                else:
                    display_name = f"\033[1;37m{essid:.22}\033[0m"
                
                # Encryption styling
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
                
                print(f"\033[1;35m│ \033[1;36m{idx:2d}\033[0m \033[1;32m{bssid}\033[0m \033[1;33m{channel:>3}\033[0m \033[1;31m{power:>3}\033[0m {enc_color}{enc_display:10}\033[0m {client_icon} {clients:>2} {display_name:24} \033[1;35m│\033[0m")
            
            print("\033[1;35m└────┴──────────────────────┴────┴─────┴───────────┴──────┴──────────────────────────┘\033[0m")
            
            if len(networks) > 10:
                print(f"\033[1;33m[📶] ... and {len(networks) - 10} more networks\033[0m")
        
        print(f"\033[1;36m[🔍] Continuous scanning... Press Ctrl+C to abort\033[0m")

    def finalize_scan_results(self):
        """Finalize and store scan results"""
        csv_file = f"{self.current_scan_file}-01.csv"
        
        if not os.path.exists(csv_file):
            print("\033[1;31m[✘] Scan data not found\033[0m")
            return False
        
        # Parse final results
        self.networks = self.parse_final_scan(csv_file)
        
        if not self.networks:
            print("\033[1;31m[✘] No networks captured\033[0m")
            return False
        
        print(f"\033[1;32m[🎯] Scan completed: {len(self.networks)} networks found\033[0m")
        print(f"\033[1;33m[👥] Clients detected: {len(self.clients)}\033[0m")
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
                            'clients': client_count
                        }
            
            return networks
            
        except Exception as e:
            print(f"\033[1;31m[✘] Parse error: {e}\033[0m")
            return {}

    # ... (rest of the methods remain the same as previous version)
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

    def get_client_count(self, bssid):
        """Count clients connected to a network"""
        count = 0
        for client_bssid, client_info in self.clients.items():
            if client_info.get('bssid') == bssid:
                count += 1
        return count

    def is_valid_bssid(self, bssid):
        """Validate BSSID format"""
        return (len(bssid) == 17 and 
                bssid.count(':') == 5 and 
                bssid != '00:00:00:00:00:00')

    def display_scan_results(self):
        """Display final scan results"""
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
        
        print("\033[1;35m┌────┬──────────────────────┬────┬─────┬───────────┬──────┬──────────────────────────┐\033[0m")
        print("\033[1;35m│ \033[1;37m#  │ MAC Address           │ CH │ PWR │ ENCRYPTION │ CLIS │ NETWORK NAME\033[1;35m             │\033[0m")
        print("\033[1;35m├────┼──────────────────────┼────┼─────┼───────────┼──────┼──────────────────────────┤\033[0m")
        
        for idx, net_info in self.networks.items():
            bssid = net_info['bssid']
            channel = net_info['channel']
            power = net_info['power']
            encryption = net_info['encryption']
            essid = net_info['essid']
            clients = net_info['clients']
            
            if "HIDDEN" in essid:
                display_name = f"\033[1;31m🚫 {essid:.20}\033[0m"
            else:
                display_name = f"\033[1;37m🎯 {essid:.20}\033[0m"
            
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
            
            client_icon = "👤" if clients == 1 else "👥" if clients > 1 else "👻"
            
            print(f"\033[1;35m│ \033[1;36m{idx:2d}\033[0m \033[1;32m{bssid}\033[0m \033[1;33m{channel:>3}\033[0m \033[1;31m{power:>3}\033[0m {enc_color}{enc_display:10}\033[0m {client_icon} {clients:>2} {display_name:24} \033[1;35m│\033[0m")
        
        print("\033[1;35m└────┴──────────────────────┴────┴─────┴───────────┴──────┴──────────────────────────┘\033[0m")
        print("\033[1;32m[✅] Targets ready for security operations\033[0m")

    def display_detailed_scan_results(self):
        """Display detailed scan results with client information"""
        self.display_scan_results()
        
        if self.clients:
            print(f"\n\033[1;35m[👥] DETECTED CLIENTS: {len(self.clients)}\033[0m")
            print("\033[1;35m┌──────────────────────┬─────┬────────┬──────────────────────┐\033[0m")
            print("\033[1;35m│ \033[1;37mCLIENT MAC           │ PWR  │ PACKETS │ ASSOCIATED AP\033[1;35m         │\033[0m")
            print("\033[1;35m├──────────────────────┼─────┼────────┼──────────────────────┤\033[0m")
            
            for client_mac, client_info in list(self.clients.items())[:15]:
                power = client_info['power']
                packets = client_info['packets']
                ap_bssid = client_info['bssid']
                
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
