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

    def wifi_scan(self, duration=10):
        """NETSTRIKE-STYLE WiFi Scan with Real-time Display"""
        print("\033[1;33m[!] INITIATING NUCLEAR SCAN PROTOCOL...\033[0m")
        
        if not self.core.mon_interface:
            print("\033[1;31m[✘] NO MONITOR INTERFACE AVAILABLE\033[0m")
            return False
        
        # Clear previous data
        self.networks = {}
        
        print(f"\033[1;36m[→] DEPLOYING SCAN DRONE ON {self.core.mon_interface}...\033[0m")
        print(f"\033[1;36m[⌛] SCAN DURATION: {duration} SECONDS\033[0m")
        
        # Use the working airodump approach
        return self.netstrike_real_time_scan(duration)

    def netstrike_real_time_scan(self, duration):
        """NetStrike real-time scanning with live display"""
        try:
            scan_file = "/tmp/netstrike_live"
            subprocess.run(f"rm -f {scan_file}* 2>/dev/null", shell=True)
            
            # Build the working airodump command
            cmd = [
                "airodump-ng",
                self.core.mon_interface,
                "--output-format", "csv",
                "-w", scan_file,
                "--write-interval", "1"
            ]
            
            print("\033[1;32m[✓] SCAN DRONE DEPLOYED\033[0m")
            print("\033[1;36m[📡] CAPTURING NETWORK SIGNALS...\033[0m")
            
            # Start airodump in background
            scan_process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
            # Show real-time progress with NetStrike style
            start_time = time.time()
            while time.time() - start_time < duration:
                elapsed = int(time.time() - start_time)
                remaining = duration - elapsed
                
                # Update scan file and show progress
                self.update_live_display(scan_file, elapsed, duration)
                time.sleep(2)
            
            # Stop scanning
            scan_process.terminate()
            scan_process.wait()
            
            print("\033[1;32m[✓] SCAN COMPLETE\033[0m")
            return self.finalize_scan_results(scan_file)
            
        except Exception as e:
            print(f"\033[1;31m[✘] SCAN FAILED: {e}\033[0m")
            return False

    def update_live_display(self, scan_file, elapsed, total):
        """Update live display during scanning"""
        csv_file = f"{scan_file}-01.csv"
        
        if os.path.exists(csv_file) and os.path.getsize(csv_file) > 100:
            networks = self.parse_live_scan(csv_file)
            if networks:
                self.show_live_results(networks, elapsed, total)

    def parse_live_scan(self, csv_file):
        """Parse live scan results"""
        networks = {}
        try:
            with open(csv_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            lines = content.split('\n')
            count = 0
            
            for line in lines:
                line = line.strip()
                if not line or 'BSSID' in line or 'Station MAC' in line:
                    continue
                
                parts = line.split(',')
                if len(parts) >= 14:
                    bssid = parts[0].strip()
                    if self.is_valid_bssid(bssid):
                        count += 1
                        
                        # Extract network info
                        channel = parts[3].strip() if len(parts) > 3 else "1"
                        power = parts[8].strip() if len(parts) > 8 else "-1"
                        encryption = parts[5].strip() if len(parts) > 5 else "OPN"
                        essid = parts[13].strip().replace('"', '') if len(parts) > 13 else "HIDDEN_SSID"
                        
                        if not essid or essid == "--":
                            essid = "HIDDEN_SSID"
                        
                        networks[count] = {
                            'bssid': bssid,
                            'channel': channel,
                            'power': power,
                            'encryption': encryption,
                            'essid': essid
                        }
            
            return networks
            
        except Exception:
            return {}

    def show_live_results(self, networks, elapsed, total):
        """Show live scanning results in NetStrike style"""
        os.system('clear')
        
        # NetStrike Banner
        print("\033[1;31m")
        print("╔══════════════════════════════════════════════════════════════════╗")
        print("║                   🚀 NETSTRIKE LIVE SCAN                        ║")
        print("║                   📡 REAL-TIME NETWORK DISCOVERY                ║")
        print("╚══════════════════════════════════════════════════════════════════╝")
        print("\033[0m")
        
        # Progress
        progress = int((elapsed / total) * 50)
        bar = "[" + "█" * progress + " " * (50 - progress) + "]"
        print(f"\033[1;36m[⌛] SCAN PROGRESS: {bar} {elapsed}/{total}s\033[0m")
        print(f"\033[1;32m[✓] NETWORKS DETECTED: {len(networks)}\033[0m")
        print()
        
        # Display networks
        if networks:
            print("\033[1;34m┌──────────────────────┬────┬─────┬───────────┬──────────────────────────┐\033[0m")
            print("\033[1;34m│ \033[1;37m#  MAC Address         CH  PWR  ENCRYPTION  NETWORK NAME\033[1;34m             │\033[0m")
            print("\033[1;34m├──────────────────────┼────┼─────┼───────────┼──────────────────────────┤\033[0m")
            
            for idx, net_info in list(networks.items())[:8]:  # Show first 8
                bssid = net_info['bssid']
                channel = net_info['channel']
                power = net_info['power']
                encryption = net_info['encryption']
                essid = net_info['essid']
                
                # NetStrike visual formatting
                if essid == "HIDDEN_SSID":
                    display_name = "\033[1;31mHIDDEN_SSID\033[0m"
                else:
                    display_name = f"\033[1;37m{essid:.20}\033[0m" + ("..." if len(essid) > 20 else "")
                
                # Encryption icons with NetStrike style
                enc_icon = "🔓"
                enc_color = "\033[1;33m"  # Yellow for open
                if "WPA2" in encryption:
                    enc_icon = "🔒"
                    enc_color = "\033[1;31m"  # Red for WPA2
                elif "WPA" in encryption:
                    enc_icon = "🔐" 
                    enc_color = "\033[1;35m"  # Purple for WPA
                elif "WEP" in encryption:
                    enc_icon = "🗝️ "
                    enc_color = "\033[1;36m"  # Cyan for WEP
                
                enc_display = f"{enc_icon} {encryption.split()[0] if ' ' in encryption else encryption}"
                
                print(f"\033[1;34m│ \033[1;33m{idx:2d}\033[0m \033[1;32m{bssid}\033[0m \033[1;36m{channel:>3}\033[0m \033[1;31m{power:>3}\033[0m {enc_color}{enc_display:10}\033[0m {display_name:24} \033[1;34m│\033[0m")
            
            print("\033[1;34m└──────────────────────┴────┴─────┴───────────┴──────────────────────────┘\033[0m")
            
            if len(networks) > 8:
                print(f"\033[1;33m[!] ... AND {len(networks) - 8} MORE NETWORKS\033[0m")
        
        print(f"\033[1;36m[📡] CONTINUING SCAN... PRESS CTRL+C TO ABORT\033[0m")

    def finalize_scan_results(self, scan_file):
        """Finalize and display complete scan results"""
        csv_file = f"{scan_file}-01.csv"
        
        if not os.path.exists(csv_file):
            print("\033[1;31m[✘] SCAN DATA NOT FOUND\033[0m")
            return False
        
        # Parse final results
        self.networks = self.parse_final_scan(csv_file)
        
        if not self.networks:
            print("\033[1;31m[✘] NO NETWORKS CAPTURED\033[0m")
            return False
        
        print(f"\033[1;32m[🎯] SCAN MISSION ACCOMPLISHED: {len(self.networks)} TARGETS ACQUIRED\033[0m")
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
                        power = parts[8].strip() if len(parts) > 8 else "-1"
                        encryption = parts[5].strip() if len(parts) > 5 else "OPN"
                        essid = parts[13].strip().replace('"', '') if len(parts) > 13 else "HIDDEN_SSID"
                        
                        if not essid or essid == "--":
                            essid = "HIDDEN_SSID"
                        
                        networks[count] = {
                            'bssid': bssid,
                            'channel': channel,
                            'power': power,
                            'encryption': encryption,
                            'essid': essid
                        }
            
            return networks
            
        except Exception as e:
            print(f"\033[1;31m[✘] FINAL PARSE ERROR: {e}\033[0m")
            return {}

    def is_valid_bssid(self, bssid):
        """Validate BSSID format"""
        return (len(bssid) == 17 and 
                bssid.count(':') == 5 and 
                bssid != '00:00:00:00:00:00')

    def display_scan_results(self):
        """Display final scan results in NetStrike victory style"""
        if not self.networks:
            print("\033[1;31m[✘] NO TARGETS TO DISPLAY\033[0m")
            return
        
        print("\033[1;31m")
        print("╔══════════════════════════════════════════════════════════════════╗")
        print("║                   🎯 SCAN MISSION COMPLETE                      ║")
        print("║                   📊 TARGET ACQUISITION REPORT                  ║")
        print("╚══════════════════════════════════════════════════════════════════╝")
        print("\033[0m")
        
        print(f"\033[1;32m[✓] TOTAL TARGETS ACQUIRED: {len(self.networks)}\033[0m")
        print()
        
        print("\033[1;34m┌──────────────────────┬────┬─────┬───────────┬──────────────────────────┐\033[0m")
        print("\033[1;34m│ \033[1;37m#  MAC Address         CH  PWR  ENCRYPTION  NETWORK NAME\033[1;34m             │\033[0m")
        print("\033[1;34m├──────────────────────┼────┼─────┼───────────┼──────────────────────────┤\033[0m")
        
        for idx, net_info in self.networks.items():
            bssid = net_info['bssid']
            channel = net_info['channel']
            power = net_info['power']
            encryption = net_info['encryption']
            essid = net_info['essid']
            
            # NetStrike victory formatting
            if essid == "HIDDEN_SSID":
                display_name = "\033[1;31m🚫 HIDDEN_SSID\033[0m"
            else:
                display_name = f"\033[1;37m🎯 {essid:.18}\033[0m" + ("..." if len(essid) > 18 else "")
            
            # Victory encryption styling
            enc_icon = "🔓"
            enc_color = "\033[1;33m"
            if "WPA2" in encryption:
                enc_icon = "🔒"
                enc_color = "\033[1;31m"
            elif "WPA" in encryption:
                enc_icon = "🔐"
                enc_color = "\033[1;35m"
            elif "WEP" in encryption:
                enc_icon = "🗝️ "
                enc_color = "\033[1;36m"
            
            enc_display = f"{enc_icon} {encryption.split()[0] if ' ' in encryption else encryption}"
            
            print(f"\033[1;34m│ \033[1;33m{idx:2d}\033[0m \033[1;32m{bssid}\033[0m \033[1;36m{channel:>3}\033[0m \033[1;31m{power:>3}\033[0m {enc_color}{enc_display:10}\033[0m {display_name:24} \033[1;34m│\033[0m")
        
        print("\033[1;34m└──────────────────────┴────┴─────┴───────────┴──────────────────────────┘\033[0m")
        print("\033[1;32m[✅] TARGETS READY FOR NUCLEAR ENGAGEMENT\033[0m")

    def select_target(self):
        """Select target with NetStrike style"""
        if not self.networks:
            print("\033[1;31m[✘] NO TARGETS AVAILABLE\033[0m")
            return None
        
        print("\033[1;33m[🎯] PREPARE TARGET SELECTION\033[0m")
        
        try:
            selection = input("\n\033[1;33m[?] SELECT TARGET (1-{}): \033[0m".format(len(self.networks)))
            idx = int(selection)
            
            if 1 <= idx <= len(self.networks):
                target = self.networks[idx]
                print(f"\033[1;32m[🎯] TARGET ACQUIRED: {target['essid']}\033[0m")
                print(f"\033[1;32m[📡] TARGET LOCKED: {target['bssid']} | CH: {target['channel']}\033[0m")
                return target
            else:
                print("\033[1;31m[✘] INVALID TARGET SELECTION\033[0m")
                return None
                
        except ValueError:
            print("\033[1;31m[✘] INVALID INPUT - ENTER TARGET NUMBER\033[0m")
            return None

    def bluetooth_scan(self):
        """NetStrike Bluetooth scanning"""
        print("\033[1;33m[!] INITIATING BLUETOOTH RECONNAISSANCE...\033[0m")
        
        self.core.run_command("systemctl start bluetooth >/dev/null 2>&1")
        self.core.run_command("hciconfig hci0 up >/dev/null 2>&1")
        
        devices = {}
        
        try:
            print("\033[1;36m[📡] DEPLOYING BLUETOOTH SENSORS...\033[0m")
            result = self.core.run_command("timeout 20s hcitool scan")
            
            if result and result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]
                
                for line in lines:
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 2:
                            mac = parts[0]
                            name = ' '.join(parts[1:]) if len(parts) > 2 else "Unknown Device"
                            device_type = self.get_bluetooth_device_type(mac, name)
                            devices[mac] = {'name': name, 'type': device_type}
                
                if devices:
                    print(f"\033[1;32m[✓] BLUETOOTH TARGETS ACQUIRED: {len(devices)}\033[0m")
                    return devices
                    
        except Exception as e:
            print(f"\033[1;31m[✘] BLUETOOTH RECON FAILED: {e}\033[0m")
        
        if not devices:
            print("\033[1;33m[!] NO BLUETOOTH TARGETS DETECTED\033[0m")
            print("  • Ensure devices are in discoverable mode")
            print("  • Check Bluetooth adapter functionality")
        
        return devices

    def get_bluetooth_device_type(self, mac, name):
        """Classify Bluetooth devices"""
        name_lower = name.lower()
        
        if any(word in name_lower for word in ['airpod', 'airpods', 'earpod', 'headphone', 'headset']):
            return "🎧 Audio Device"
        elif any(word in name_lower for word in ['iphone', 'samsung', 'xiaomi', 'huawei', 'phone', 'mobile']):
            return "📱 Mobile Device"
        elif any(word in name_lower for word in ['tablet', 'ipad', 'tab']):
            return "📟 Tablet"
        elif any(word in name_lower for word in ['laptop', 'notebook', 'macbook']):
            return "💻 Computer"
        elif any(word in name_lower for word in ['watch', 'smartwatch', 'galaxy watch']):
            return "⌚ Wearable"
        elif any(word in name_lower for word in ['speaker', 'sound', 'jbl', 'bose']):
            return "🔊 Speaker"
        else:
            return "🔵 Unknown Device"
