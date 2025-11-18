#!/usr/bin/env python3
"""
NETSTRIKE v3.0 ADVANCED SCANNER
Deep Network Intelligence & Hidden SSID Detection
"""

import os
import time
import subprocess
import threading
import json
from ui_animations import CyberUI

class AdvancedScanner:
    def __init__(self, core):
        self.core = core
        self.ui = CyberUI()
        self.networks = {}
        self.clients = {}
        self.scanning = False
        self.scan_thread = None
        
    def deep_network_scan(self, duration=15):
        """Advanced network scanning with hidden SSID detection"""
        self.ui.attack_header("ADVANCED NETWORK SCANNER")
        self.ui.type_effect("🎯 INITIATING DEEP NETWORK INTELLIGENCE...", 0.03)
        
        if not self.core.mon_interface:
            self.ui.error_message("MONITOR MODE NOT ACTIVE")
            return False
            
        self.ui.progress_bar("ACTIVATING SCANNING DRONE", 2)
        
        # Start the advanced scan
        return self._perform_advanced_scan(duration)
        
    def _perform_advanced_scan(self, duration):
        """Perform advanced network scanning"""
        scan_file = f"/tmp/netstrike_deepscan_{int(time.time())}"
        
        try:
            # Start airodump-ng for advanced scanning
            cmd = [
                "airodump-ng",
                self.core.mon_interface,
                "--output-format", "csv",
                "-w", scan_file,
                "--write-interval", "2",
                "--berlin", "10"  # Better signal analysis
            ]
            
            scan_process = self.core.run_command(" ".join(cmd), background=True)
            
            if not scan_process:
                self.ui.error_message("FAILED TO START SCANNER")
                return False
                
            self.ui.type_effect("📡 CAPTURING NETWORK SIGNALS...", 0.03)
            
            # Show real-time scanning progress
            self._display_live_scan(duration, scan_file)
            
            # Stop scanning
            scan_process.terminate()
            scan_process.wait()
            
            # Parse results
            return self._parse_advanced_results(scan_file)
            
        except Exception as e:
            self.ui.error_message(f"SCAN ERROR: {e}")
            return False
            
    def _display_live_scan(self, duration, scan_file):
        """Display live scanning progress"""
        start_time = time.time()
        networks_found = 0
        
        while time.time() - start_time < duration:
            elapsed = int(time.time() - start_time)
            remaining = duration - elapsed
            
            # Update scan results
            current_networks = self._parse_live_scan(scan_file)
            if current_networks:
                networks_found = len(current_networks)
                
            # Display progress
            self._show_scan_progress(elapsed, duration, networks_found, current_networks)
            time.sleep(2)
            
    def _show_scan_progress(self, elapsed, total, count, networks):
        """Show real-time scanning progress"""
        os.system('clear')
        
        # Header
        print("\033[1;36m")
        print("╔══════════════════════════════════════════════════════════════════╗")
        print("║                   📡 LIVE NETWORK SCAN                          ║")
        print("║                   DEEP INTELLIGENCE GATHERING                   ║")
        print("╚══════════════════════════════════════════════════════════════════╝")
        print("\033[0m")
        
        # Progress
        progress = int((elapsed / total) * 50)
        bar = "[" + "█" * progress + "░" * (50 - progress) + "]"
        print(f"\033[1;32m[⌛] SCAN PROGRESS: {bar} {elapsed}/{total}s\033[0m")
        print(f"\033[1;33m[🎯] NETWORKS FOUND: {count}\033[0m")
        print()
        
        if networks:
            print("\033[1;34m┌────┬──────────────────────┬────┬─────┬───────────┬──────────────────────────┐\033[0m")
            print("\033[1;34m│ \033[1;37m#  │ MAC Address           │ CH │ PWR │ ENCRYPTION │ NETWORK NAME\033[1;34m             │\033[0m")
            print("\033[1;34m├────┼──────────────────────┼────┼─────┼───────────┼──────────────────────────┤\033[0m")
            
            for idx, (bssid, info) in enumerate(list(networks.items())[:8], 1):
                essid = info['essid']
                channel = info['channel']
                power = info['power']
                encryption = info['encryption']
                
                # Format display
                if essid == "HIDDEN_SSID":
                    display_name = "\033[1;31m🚫 HIDDEN NETWORK\033[0m"
                else:
                    display_name = f"\033[1;37m{essid:.20}\033[0m" + ("..." if len(essid) > 20 else "")
                
                # Encryption icons
                enc_icon = "🔓"
                if "WPA2" in encryption:
                    enc_icon = "🔒"
                elif "WPA" in encryption:
                    enc_icon = "🔐"
                elif "WEP" in encryption:
                    enc_icon = "🗝️"
                    
                print(f"\033[1;34m│ \033[1;33m{idx:2d} \033[1;32m{bssid} \033[1;36m{channel:>3} \033[1;31m{power:>3} \033[1;35m{enc_icon} {encryption:6} \033[0m{display_name:24} \033[1;34m│\033[0m")
            
            print("\033[1;34m└────┴──────────────────────┴────┴─────┴───────────┴──────────────────────────┘\033[0m")
            
            if len(networks) > 8:
                print(f"\033[1;33m[!] ... AND {len(networks) - 8} MORE NETWORKS\033[0m")
        else:
            print("\033[1;33m[!] SCANNING FOR NETWORKS...\033[0m")
            
        print(f"\033[1;36m[📡] SCANNING FREQUENCIES... {remaining}s REMAINING\033[0m")
        
    def _parse_live_scan(self, scan_file):
        """Parse live scan results"""
        csv_file = f"{scan_file}-01.csv"
        networks = {}
        
        if not os.path.exists(csv_file):
            return networks
            
        try:
            with open(csv_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            lines = content.split('\n')
            count = 0
            
            for line in lines:
                line = line.strip()
                if not line or 'BSSID' in line or 'Station MAC' in line:
                    continue
                    
                parts = [part.strip() for part in line.split(',')]
                if len(parts) >= 14:
                    bssid = parts[0]
                    if self._is_valid_bssid(bssid):
                        count += 1
                        
                        channel = parts[3] if len(parts) > 3 else "1"
                        power = parts[8] if len(parts) > 8 else "-1"
                        encryption = parts[5] if len(parts) > 5 else "OPN"
                        essid = parts[13].replace('"', '') if len(parts) > 13 else "HIDDEN_SSID"
                        
                        if not essid or essid == "--":
                            essid = "HIDDEN_SSID"
                            
                        networks[bssid] = {
                            'bssid': bssid,
                            'channel': channel,
                            'power': power,
                            'encryption': encryption,
                            'essid': essid,
                            'clients': []
                        }
                        
        except Exception as e:
            pass
            
        return networks
        
    def _parse_advanced_results(self, scan_file):
        """Parse final scan results with client information"""
        csv_file = f"{scan_file}-01.csv"
        
        if not os.path.exists(csv_file):
            self.ui.error_message("SCAN DATA NOT FOUND")
            return False
            
        self.networks = self._parse_live_scan(scan_file)
        
        if not self.networks:
            self.ui.error_message("NO NETWORKS DETECTED")
            return False
            
        # Get client information
        self._detect_connected_clients(scan_file)
        
        self.ui.success_message(f"SCAN COMPLETE: {len(self.networks)} NETWORKS DISCOVERED")
        return True
        
    def _detect_connected_clients(self, scan_file):
        """Detect clients connected to networks"""
        try:
            csv_file = f"{scan_file}-01.csv"
            with open(csv_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            lines = content.split('\n')
            in_clients = False
            
            for line in lines:
                line = line.strip()
                if 'Station MAC' in line:
                    in_clients = True
                    continue
                elif 'BSSID' in line and in_clients:
                    break
                    
                if in_clients and line:
                    parts = [part.strip() for part in line.split(',')]
                    if len(parts) >= 6:
                        client_mac = parts[0]
                        bssid = parts[5]
                        
                        if self._is_valid_bssid(bssid) and bssid in self.networks:
                            if 'clients' not in self.networks[bssid]:
                                self.networks[bssid]['clients'] = []
                            self.networks[bssid]['clients'].append(client_mac)
                            
        except Exception:
            pass
            
    def display_scan_results(self):
        """Display comprehensive scan results"""
        if not self.networks:
            self.ui.error_message("NO SCAN DATA AVAILABLE")
            return
            
        self.ui.attack_header("NETWORK INTELLIGENCE REPORT")
        
        print("\033[1;36m")
        print("╔══════════════════════════════════════════════════════════════════╗")
        print("║                   📊 COMPREHENSIVE SCAN RESULTS                 ║")
        print("╚══════════════════════════════════════════════════════════════════╝")
        print("\033[0m")
        
        print(f"\033[1;32m[✓] TOTAL NETWORKS DISCOVERED: {len(self.networks)}\033[0m")
        print()
        
        # Display networks with detailed information
        for idx, (bssid, network) in enumerate(self.networks.items(), 1):
            self._display_network_details(idx, network)
            
        print(f"\033[1;32m[✅] NETWORK INTELLIGENCE GATHERING COMPLETE\033[0m")
        
    def _display_network_details(self, index, network):
        """Display detailed network information"""
        essid = network['essid']
        bssid = network['bssid']
        channel = network['channel']
        power = network['power']
        encryption = network['encryption']
        clients = network.get('clients', [])
        
        # Network header
        if essid == "HIDDEN_SSID":
            header = f"\033[1;31m🚫 HIDDEN NETWORK {index}\033[0m"
        else:
            header = f"\033[1;36m🎯 {essid}\033[0m"
            
        print(f"\n{header}")
        print("\033[1;34m├──────────────────────────────────────────────────────────┤\033[0m")
        print(f"  \033[1;33mMAC:\033[0m \033[1;32m{bssid}\033[0m")
        print(f"  \033[1;33mChannel:\033[0m \033[1;36m{channel}\033[0m")
        print(f"  \033[1;33mSignal:\033[0m \033[1;31m{power} dBm\033[0m")
        print(f"  \033[1;33mSecurity:\033[0m \033[1;35m{encryption}\033[0m")
        
        if clients:
            print(f"  \033[1;33mConnected Devices:\033[0m \033[1;37m{len(clients)}\033[0m")
            for client in clients[:3]:  # Show first 3 clients
                print(f"    └─ \033[1;32m{client}\033[0m")
            if len(clients) > 3:
                print(f"    └─ \033[1;33m... and {len(clients) - 3} more\033[0m")
        else:
            print(f"  \033[1;33mConnected Devices:\033[0m \033[1;31mNone detected\033[0m")
            
    def select_target(self):
        """Allow user to select target from scan results"""
        if not self.networks:
            self.ui.error_message("NO TARGETS AVAILABLE")
            return None
            
        networks_list = list(self.networks.items())
        
        print("\n\033[1;33m[🎯] TARGET SELECTION\033[0m")
        print("\033[1;34m┌────┬──────────────────────────┬──────────┬─────┐\033[0m")
        print("\033[1;34m│ \033[1;37m#  │ NETWORK NAME               │ CH │ PWR \033[1;34m│\033[0m")
        print("\033[1;34m├────┼──────────────────────────┼──────────┼─────┤\033[0m")
        
        for idx, (bssid, network) in enumerate(networks_list, 1):
            essid = network['essid']
            channel = network['channel']
            power = network['power']
            
            display_name = essid if essid != "HIDDEN_SSID" else "HIDDEN_SSID"
            display_name = display_name[:24] + ("..." if len(display_name) > 24 else "")
            
            print(f"\033[1;34m│ \033[1;33m{idx:2d} \033[1;37m{display_name:24} \033[1;36m{channel:>4} \033[1;31m{power:>4} \033[1;34m│\033[0m")
            
        print("\033[1;34m└────┴──────────────────────────┴──────────┴─────┘\033[0m")
        
        try:
            selection = input("\n\033[1;33m[?] SELECT TARGET (1-{}): \033[0m".format(len(networks_list)))
            idx = int(selection) - 1
            
            if 0 <= idx < len(networks_list):
                bssid, target = networks_list[idx]
                self.ui.success_message(f"TARGET ACQUIRED: {target['essid']}")
                return target
            else:
                self.ui.error_message("INVALID SELECTION")
                return None
                
        except ValueError:
            self.ui.error_message("INVALID INPUT")
            return None
            
    def _is_valid_bssid(self, bssid):
        """Validate BSSID format"""
        return (len(bssid) == 17 and 
                bssid.count(':') == 5 and 
                bssid != '00:00:00:00:00:00')
