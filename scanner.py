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
        """Professional Network Discovery - Fresh Scan Every Time"""
        print("\033[1;36m[→] Initializing professional network discovery...\033[0m")
        
        # Verify monitor mode is active
        if not self.verify_monitor_mode():
            print("\033[1;31m[✘] Monitor mode verification failed\033[0m")
            return False
        
        if not self.core.mon_interface:
            print("\033[1;31m[✘] No monitor interface available\033[0m")
            return False
        
        # CRITICAL: Always reset for fresh scan
        self.networks = {}
        self.clients = {}
        
        print(f"\033[1;36m[📡] Scanning on: {self.core.mon_interface}\033[0m")
        print(f"\033[1;36m[⏱️] Duration: {duration} seconds\033[0m")
        
        return self.professional_scan(duration)

    def verify_monitor_mode(self):
        """Verify interface is actually in monitor mode"""
        result = self.core.run_command(f"iwconfig {self.core.mon_interface} 2>/dev/null")
        if result and "Mode:Monitor" in result.stdout:
            return True
        else:
            print("\033[1;31m[✘] Interface not in monitor mode - attempting recovery...\033[0m")
            return self.core.setup_monitor_mode()

    def professional_scan(self, duration):
        """Professional scanning with robust CSV parsing"""
        try:
            self.current_scan_file = "/tmp/netstrike_pro_scan"
            subprocess.run(f"rm -f {self.current_scan_file}* 2>/dev/null", shell=True)

            # Verify airodump-ng is available
            if not self.core.run_command("command -v airodump-ng"):
                print("\033[1;31m[✘] airodump-ng not found - please install aircrack-ng\033[0m")
                return False

            # Kill any existing airodump processes
            self.core.run_command("killall airodump-ng 2>/dev/null")
            time.sleep(1)

            # Try dual-band first; fall back to 2.4GHz-only if adapter rejects --band abg
            scan_process = self._start_airodump(dual_band=True)
            time.sleep(3)
            csv_file = f"{self.current_scan_file}-01.csv"
            if scan_process.poll() is not None or not os.path.exists(csv_file):
                # Process died or produced nothing — restart without --band
                try:
                    scan_process.terminate()
                except Exception:
                    pass
                time.sleep(1)
                print("\033[1;33m[!] Dual-band unavailable — scanning 2.4GHz\033[0m")
                scan_process = self._start_airodump(dual_band=False)

            print("\033[1;32m[✓] Scan initiated\033[0m")

            start_time = time.time()
            while time.time() - start_time < duration:
                elapsed = int(time.time() - start_time)
                self.update_professional_display(elapsed, duration)
                time.sleep(2)

            try:
                scan_process.terminate()
                scan_process.wait(timeout=3)
            except Exception:
                pass

            print("\033[1;32m[✓] Scan complete\033[0m")
            return self.finalize_professional_scan()

        except Exception as e:
            print(f"\033[1;31m[✘] Scan failed: {e}\033[0m")
            return False

    def _start_airodump(self, dual_band=True):
        """Start airodump-ng, optionally with --band abg for 5GHz support."""
        cmd = [
            "airodump-ng",
            self.core.mon_interface,
            "--output-format", "csv",
            "-w", self.current_scan_file,
            "--write-interval", "2",
        ]
        if dual_band:
            cmd += ["--band", "abg"]
        return subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

    def update_professional_display(self, elapsed, total):
        """Professional real-time display"""
        networks = self.parse_professional_scan_data()
        
        if networks:
            self.show_professional_results(networks, elapsed, total)

    def parse_professional_scan_data(self):
        """ATOMIC & ROBUST CSV PARSING - FIXED VERSION"""
        csv_file = f"{self.current_scan_file}-01.csv"
        networks = {}
        
        # 1. Wait for file to exist (Don't return empty immediately)
        if not os.path.exists(csv_file):
            return networks

        try:
            with open(csv_file, 'r', encoding='utf-8', errors='replace') as f:
                content = f.readlines()

            # 2. Separate APs from Clients reliably
            ap_lines = []
            for line in content:
                if "Station MAC" in line:
                    break  # Stop when we hit the Client section
                if line.strip() and "BSSID" not in line:
                    ap_lines.append(line)

            # 3. Parse APs using CSV Library (Handles commas in SSIDs)
            reader = csv.reader(ap_lines)
            network_count = 0
            
            for row in reader:
                try:
                    # Robust Validation
                    if not row or len(row) < 14:
                        continue
                    
                    bssid = row[0].strip()
                    if not self.is_valid_bssid(bssid):
                        continue

                    # Safe Field Extraction
                    channel = row[3].strip()
                    encryption = row[5].strip()
                    power = row[8].strip()
                    essid = row[13].strip()
                    
                    # Filter weak signals or bad data
                    if power == "-1" or not channel.isdigit():
                        continue

                    # Handle Hidden SSIDs
                    if not essid or essid == "\\x00" or essid == "":
                        essid = "🚫 HIDDEN_NETWORK"
                    
                    network_count += 1
                    networks[network_count] = {
                        'bssid': bssid,
                        'channel': channel,
                        'power': power,
                        'encryption': encryption,
                        'essid': essid,
                        'clients': 0  # Will be populated by client parser
                    }
                except Exception as e:
                    continue  # Skip bad row, keep scanning!
            
            # 4. Parse Clients (Optional for now)
            self.parse_clients_robust(content)
            
            # Update client counts
            for net_id, net_info in networks.items():
                net_info['clients'] = self.get_client_count(net_info['bssid'])
            
            return networks

        except Exception as e:
            print(f"\033[1;33m[⚠️] CSV parsing error: {e}\033[0m")
            return {}

    def parse_clients_robust(self, content):
        """Robust client parsing using CSV library"""
        self.clients = {}
        client_section = False
        
        try:
            for line in content:
                if "Station MAC" in line:
                    client_section = True
                    continue
                if client_section and line.strip():
                    reader = csv.reader([line])
                    for row in reader:
                        if len(row) >= 6:
                            client_mac = row[0].strip()
                            if self.is_valid_bssid(client_mac):
                                self.clients[client_mac] = {
                                    'power': row[3].strip() if len(row) > 3 else "-1",
                                    'packets': row[4].strip() if len(row) > 4 else "0",
                                    'bssid': row[5].strip() if len(row) > 5 else "Not Associated"
                                }
        except Exception as e:
            print(f"\033[1;33m[⚠️] Client parsing error: {e}\033[0m")

    def get_client_count(self, bssid):
        """Count clients for a network"""
        return len([c for c, info in self.clients.items() if info.get('bssid') == bssid])

    def show_professional_results(self, networks, elapsed, total):
        """Professional real-time display"""
        os.system('clear')
        
        print("\033[1;35m")
        print("╔══════════════════════════════════════════════════════════════════╗")
        print("║                   📡 NETSTRIKE NETWORK DISCOVERY                ║")
        print("║                   🔍 PROFESSIONAL SCAN ACTIVE                   ║")
        print("╚══════════════════════════════════════════════════════════════════╝")
        print("\033[0m")
        
        # Professional progress bar
        progress = int((elapsed / total) * 50)
        bar = "[" + "█" * progress + "▒" * (50 - progress) + "]"
        print(f"\033[1;36m[⏳] SCAN PROGRESS: {bar} {elapsed}/{total}s\033[0m")
        print(f"\033[1;32m[✅] NETWORKS: {len(networks)} | CLIENTS: {len(self.clients)}\033[0m")
        print()
        
        # Sort networks by signal strength
        sorted_networks = sorted(networks.items(), 
                               key=lambda x: int(x[1]['power']) if x[1]['power'].lstrip('-').isdigit() else 0, 
                               reverse=True)
        
        if sorted_networks:
            print("\033[1;35m┌────┬──────────────────────┬────┬─────┬───────────┬──────┬──────────────────────────┐\033[0m")
            print("\033[1;35m│ \033[1;37m#  │ MAC Address           │ CH │ PWR │ ENCRYPTION │ CLIS │ NETWORK NAME\033[1;35m             │\033[0m")
            print("\033[1;35m├────┼──────────────────────┼────┼─────┼───────────┼──────┼──────────────────────────┤\033[0m")
            
            for idx, (net_id, net_info) in enumerate(sorted_networks[:10], 1):
                bssid = net_info['bssid']
                channel = net_info['channel']
                power = net_info['power']
                encryption = net_info['encryption']
                essid = net_info['essid']
                clients = net_info['clients']
                
                # Professional formatting
                if "HIDDEN" in essid:
                    display_name = f"\033[1;31m{essid:.20}\033[0m"
                else:
                    display_name = f"\033[1;37m{essid:.20}\033[0m"
                
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
                
                print(f"\033[1;35m│ \033[1;36m{idx:2d}\033[0m \033[1;32m{bssid}\033[0m \033[1;33m{channel:>3}\033[0m \033[1;31m{power:>3}\033[0m {enc_color}{enc_display:10}\033[0m {client_icon} {clients:>2}  {display_name:20} \033[1;35m│\033[0m")
            
            print("\033[1;35m└────┴──────────────────────┴────┴─────┴───────────┴──────┴──────────────────────────┘\033[0m")
            
            if len(sorted_networks) > 10:
                print(f"\033[1;33m[📶] ... and {len(sorted_networks) - 10} more networks\033[0m")
        
        print(f"\033[1;36m[🔍] Professional scanning active...\033[0m")

    def finalize_professional_scan(self):
        """Finalize professional scan results"""
        csv_file = f"{self.current_scan_file}-01.csv"
        
        if not os.path.exists(csv_file):
            print("\033[1;31m[✘] Scan data not found\033[0m")
            return False
        
        # Parse final results
        self.networks = self.parse_final_professional_scan(csv_file)
        
        if not self.networks:
            print("\033[1;31m[✘] No networks captured\033[0m")
            return False
        
        print(f"\033[1;32m[✅] Professional scan complete: {len(self.networks)} targets\033[0m")
        return True

    def parse_final_professional_scan(self, csv_file):
        """Final professional scan parsing with robust CSV handling"""
        networks = {}
        try:
            with open(csv_file, 'r', encoding='utf-8', errors='replace') as f:
                content = f.readlines()

            ap_lines = []
            for line in content:
                if "Station MAC" in line:
                    break
                if line.strip() and "BSSID" not in line:
                    ap_lines.append(line)

            reader = csv.reader(ap_lines)
            network_count = 0
            
            for row in reader:
                try:
                    if not row or len(row) < 14:
                        continue
                    
                    bssid = row[0].strip()
                    if not self.is_valid_bssid(bssid):
                        continue

                    channel = row[3].strip()
                    encryption = row[5].strip()
                    power = row[8].strip()
                    essid = row[13].strip()
                    
                    # Filter weak/bad signals
                    if power == "-1" or not channel.isdigit():
                        continue
                    
                    if not essid or essid == "\\x00" or essid == "":
                        essid = "🚫 HIDDEN_NETWORK"
                    
                    network_count += 1
                    networks[network_count] = {
                        'bssid': bssid,
                        'channel': channel,
                        'power': power,
                        'encryption': encryption,
                        'essid': essid,
                        'clients': self.get_client_count(bssid)
                    }
                except Exception:
                    continue
                    
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
        """Display professional scan results"""
        if not self.networks:
            print("\033[1;31m[✘] No targets to display\033[0m")
            return
        
        # Sort by signal strength
        sorted_networks = sorted(self.networks.items(), 
                               key=lambda x: int(x[1]['power']) if x[1]['power'].lstrip('-').isdigit() else 0, 
                               reverse=True)
        
        print("\033[1;35m")
        print("╔══════════════════════════════════════════════════════════════════╗")
        print("║                   📊 PROFESSIONAL SCAN REPORT                   ║")
        print("║                   🎯 TARGET ANALYSIS COMPLETE                   ║")
        print("╚══════════════════════════════════════════════════════════════════╝")
        print("\033[0m")
        
        print(f"\033[1;32m[✅] NETWORKS: {len(sorted_networks)} | CLIENTS: {len(self.clients)}\033[0m")
        print()
        
        print("\033[1;35m┌────┬──────────────────────┬────┬─────┬───────────┬──────┬──────────────────────────┐\033[0m")
        print("\033[1;35m│ \033[1;37m#  │ MAC Address           │ CH │ PWR │ ENCRYPTION │ CLIS │ NETWORK NAME\033[1;35m             │\033[0m")
        print("\033[1;35m├────┼──────────────────────┼────┼─────┼───────────┼──────┼──────────────────────────┤\033[0m")
        
        for idx, (net_id, net_info) in enumerate(sorted_networks, 1):
            bssid = net_info['bssid']
            channel = net_info['channel']
            power = net_info['power']
            encryption = net_info['encryption']
            essid = net_info['essid']
            clients = net_info['clients']
            
            if "HIDDEN" in essid:
                display_name = f"\033[1;31m🚫 {essid:.18}\033[0m"
            else:
                display_name = f"\033[1;37m🎯 {essid:.18}\033[0m"
            
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
            
            print(f"\033[1;35m│ \033[1;36m{idx:2d}\033[0m \033[1;32m{bssid}\033[0m \033[1;33m{channel:>3}\033[0m \033[1;31m{power:>3}\033[0m {enc_color}{enc_display:10}\033[0m {client_icon} {clients:>2}  {display_name:20} \033[1;35m│\033[0m")
        
        print("\033[1;35m└────┴──────────────────────┴────┴─────┴───────────┴──────┴──────────────────────────┘\033[0m")
        print("\033[1;32m[✅] Professional target acquisition complete\033[0m")

    def select_target(self):
        """Professional target selection"""
        if not self.networks:
            print("\033[1;31m[✘] No targets available\033[0m")
            return None
        
        # Sort by signal strength for better selection
        sorted_networks = sorted(self.networks.items(), 
                               key=lambda x: int(x[1]['power']) if x[1]['power'].lstrip('-').isdigit() else 0, 
                               reverse=True)
        
        print("\033[1;36m[🎯] Professional target selection\033[0m")
        
        try:
            selection = input("\n\033[1;36m[?] Select target (1-{}): \033[0m".format(len(sorted_networks)))
            idx = int(selection)
            
            if 1 <= idx <= len(sorted_networks):
                target_id, target = sorted_networks[idx-1]
                print(f"\033[1;32m[✅] Target acquired: {target['essid']}\033[0m")
                print(f"\033[1;32m[📡] Signal strength: {target['power']} | Channel: {target['channel']}\033[0m")
                return target
            else:
                print("\033[1;31m[✘] Invalid target selection\033[0m")
                return None
                
        except ValueError:
            print("\033[1;31m[✘] Invalid input\033[0m")
            return None

    def client_detection_scan(self):
        """Deep client reconnaissance"""
        print("\033[1;36m[→] Starting deep client reconnaissance...\033[0m")
        
        if not self.networks:
            print("\033[1;31m[✘] No networks available for client scan\033[0m")
            return
        
        target = self.select_target()
        if not target:
            return
        
        print(f"\033[1;36m[🔍] Scanning for clients on: {target['essid']}\033[0m")
        
        client_file = f"/tmp/client_scan_{target['bssid'].replace(':', '')}"
        
        # Start targeted client scan
        scan_proc = self.core.run_command(
            f"airodump-ng --bssid {target['bssid']} -c {target['channel']} -w {client_file} --output-format csv {self.core.mon_interface}",
            background=True
        )
        
        print("\033[1;36m[⏱️] Scanning for 15 seconds...\033[0m")
        time.sleep(15)
        
        if scan_proc:
            scan_proc.terminate()
        
        # Parse client results
        client_csv = f"{client_file}-01.csv"
        if os.path.exists(client_csv):
            self.parse_client_data_final(client_csv, target['bssid'])
            self.display_client_results(target)
        else:
            print("\033[1;31m[✘] Client scan failed\033[0m")

    def parse_client_data_final(self, csv_file, target_bssid):
        """Parse final client data with CSV library"""
        self.clients = {}
        try:
            with open(csv_file, 'r', encoding='utf-8', errors='replace') as f:
                content = f.readlines()
                
            client_section = False
            for line in content:
                if 'Station MAC' in line:
                    client_section = True
                    continue
                if client_section and line.strip():
                    reader = csv.reader([line])
                    for row in reader:
                        if len(row) >= 6 and self.is_valid_bssid(row[0]):
                            client_mac = row[0]
                            bssid = row[5] if len(row) > 5 else "Not Associated"
                            
                            if bssid == target_bssid:
                                self.clients[client_mac] = {
                                    'power': row[3] if len(row) > 3 else "-1",
                                    'packets': row[4] if len(row) > 4 else "0",
                                    'bssid': bssid
                                }
        except Exception as e:
            print(f"\033[1;33m[⚠️] Client parse error: {e}\033[0m")

    def display_client_results(self, target):
        """Display client reconnaissance results"""
        if not self.clients:
            print("\033[1;31m[✘] No clients detected\033[0m")
            return
        
        print(f"\n\033[1;35m[📊] CLIENT RECONNAISSANCE: {target['essid']}\033[0m")
        print(f"\033[1;32m[✅] Detected {len(self.clients)} connected clients\033[0m")
        
        print("\033[1;35m┌──────────────────────┬─────┬────────┬──────────────────────┐\033[0m")
        print("\033[1;35m│ \033[1;37mClient MAC           │ PWR │ Packets │ Status\033[1;35m             │\033[0m")
        print("\033[1;35m├──────────────────────┼─────┼────────┼──────────────────────┤\033[0m")
        
        for client_mac, client_info in self.clients.items():
            power = client_info['power']
            packets = client_info['packets']
            status = "🟢 ACTIVE" if packets.strip().lstrip('-').isdigit() and int(packets) > 10 else "🟡 IDLE"
            
            print(f"\033[1;35m│ \033[1;32m{client_mac}\033[0m \033[1;33m{power:>4}\033[0m {packets:>7}   {status:18} \033[1;35m│\033[0m")
        
        print("\033[1;35m└──────────────────────┴─────┴────────┴──────────────────────┘\033[0m")
