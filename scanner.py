#!/usr/bin/env python3

import os
import time
import subprocess
import threading
import csv
from typing import Dict, List

class NetworkScanner:
    def __init__(self, core):
        self.core = core
        self.networks = {}
        self.clients = {}
        self.scanning = False

    def wifi_scan(self, duration=15):
        """Perform WiFi network scan with DEBUG output"""
        print("\033[1;33m[!] INITIATING NETSTRIKE SCAN...\033[0m")
        
        if not self.core.mon_interface:
            print("\033[1;31m[✘] NO MONITOR INTERFACE AVAILABLE\033[0m")
            return False
        
        scan_file = "/tmp/netstrike_scan"
        
        # Clear previous scan data
        self.networks = {}
        
        # Remove old scan files
        subprocess.run(f"rm -f {scan_file}* 2>/dev/null", shell=True)
        
        print(f"\033[1;36m[→] SCANNING FOR {duration} SECONDS ON {self.core.mon_interface}...\033[0m")
        
        try:
            # DEBUG: Show the exact command being run
            print(f"\033[1;35m[DEBUG] Running: timeout {duration}s airodump-ng {self.core.mon_interface} --output-format csv -w {scan_file}\033[0m")
            
            # Start airodump-ng scan
            scan_process = self.core.run_command(
                f"timeout {duration}s airodump-ng {self.core.mon_interface} --output-format csv -w {scan_file} --ignore-negative-one",
                background=True
            )
            
            # Show progress animation
            for i in range(duration):
                print(f"\033[1;36m[⌛] SCANNING... {i+1}/{duration} SECONDS\033[0m", end='\r')
                time.sleep(1)
            print()
            
            # Wait for process to finish
            if scan_process:
                scan_process.wait()
            
            # DEBUG: Check if file was created
            csv_file = f"{scan_file}-01.csv"
            print(f"\033[1;35m[DEBUG] Looking for file: {csv_file}\033[0m")
            
            if os.path.exists(csv_file):
                file_size = os.path.getsize(csv_file)
                print(f"\033[1;35m[DEBUG] File exists! Size: {file_size} bytes\033[0m")
                
                # DEBUG: Show first few lines of the file
                if file_size > 0:
                    print(f"\033[1;35m[DEBUG] First 5 lines of CSV:\033[0m")
                    with open(csv_file, 'r', errors='ignore') as f:
                        for i, line in enumerate(f):
                            if i < 5:
                                print(f"\033[1;35m[DEBUG] Line {i}: {line.strip()}\033[0m")
                            else:
                                break
                else:
                    print("\033[1;35m[DEBUG] File is empty!\033[0m")
                
                if file_size > 100:
                    print("\033[1;32m[✓] SCAN COMPLETED SUCCESSFULLY\033[0m")
                    return self.parse_scan_results(csv_file)
                else:
                    print("\033[1;31m[✘] SCAN FAILED - CSV FILE TOO SMALL\033[0m")
                    return self.manual_scan(duration)
            else:
                print("\033[1;31m[✘] SCAN FAILED - NO CSV FILE CREATED\033[0m")
                return self.manual_scan(duration)
                
        except Exception as e:
            print(f"\033[1;31m[✘] SCAN ERROR: {e}\033[0m")
            return False

    def parse_scan_results(self, scan_file):
        """Parse airodump-ng CSV results with DEBUG output"""
        try:
            self.networks = {}
            count = 0
            
            print(f"\033[1;35m[DEBUG] Starting CSV parsing...\033[0m")
            
            with open(scan_file, 'r', encoding='utf-8', errors='ignore') as f:
                reader = csv.reader(f)
                networks_section = True
                
                for row_num, row in enumerate(reader):
                    if not row:
                        continue
                    
                    # DEBUG: Show what we're parsing
                    if row_num < 3:  # Show first 3 rows for debugging
                        print(f"\033[1;35m[DEBUG] Row {row_num}: {row}\033[0m")
                    
                    # Check if we've reached the client section
                    if len(row) > 0 and 'Station MAC' in row[0]:
                        networks_section = False
                        print(f"\033[1;35m[DEBUG] Reached client section at row {row_num}\033[0m")
                        continue
                    
                    if networks_section and len(row) >= 14:
                        bssid = row[0].strip()
                        # Validate BSSID format
                        if len(bssid) == 17 and ':' in bssid and bssid.count(':') == 5:
                            channel = row[3].strip() if len(row) > 3 and row[3].strip() else "1"
                            power = row[8].strip() if len(row) > 8 and row[8].strip() else "-1"
                            encryption = row[5].strip() if len(row) > 5 and row[5].strip() else "OPN"
                            
                            # Get ESSID (can be in different positions)
                            essid = ""
                            if len(row) > 13:
                                essid = row[13].strip()
                            elif len(row) > 1:
                                essid = row[1].strip()
                            
                            # Clean ESSID
                            essid = essid.replace('"', '').strip()
                            if not essid:
                                essid = "HIDDEN_SSID"
                            
                            # Clean channel (remove non-numeric)
                            channel = ''.join(filter(str.isdigit, channel))
                            if not channel:
                                channel = "1"
                            
                            count += 1
                            self.networks[count] = {
                                'bssid': bssid,
                                'channel': channel,
                                'power': power,
                                'encryption': encryption,
                                'essid': essid
                            }
                            
                            # DEBUG: Show parsed network
                            print(f"\033[1;35m[DEBUG] Found network {count}: {essid} ({bssid})\033[0m")
            
            print(f"\033[1;32m[✓] PARSED {count} NETWORKS\033[0m")
            return count > 0
            
        except Exception as e:
            print(f"\033[1;31m[✘] CSV PARSING ERROR: {e}\033[0m")
            return False

    def display_scan_results(self):
        """Display scanned networks"""
        if not self.networks:
            print("\033[1;31m[✘] NO NETWORKS FOUND IN SCAN RESULTS\033[0m")
            print("\033[1;33m[!] TROUBLESHOOTING:\033[0m")
            print("  • Check if monitor mode is active")
            print("  • Ensure wireless adapter supports monitoring")
            print("  • Try moving closer to networks")
            print("  • Check if networks are operating on 2.4GHz/5GHz")
            return
        
        print("\033[1;34m┌──────────────────────┬────┬─────┬───────────┬──────────────────────────┐\033[0m")
        print("\033[1;34m│ \033[1;37m#  MAC Address         CH  PWR  ENCRYPTION  NETWORK NAME\033[1;34m             │\033[0m")
        print("\033[1;34m├──────────────────────┼────┼─────┼───────────┼──────────────────────────┤\033[0m")
        
        for idx, net_info in self.networks.items():
            bssid = net_info['bssid']
            channel = net_info['channel']
            power = net_info['power']
            encryption = net_info['encryption']
            essid = net_info['essid']
            
            # Format display name
            if essid == "HIDDEN_SSID":
                display_name = "\033[1;31mHIDDEN_SSID\033[0m"
            else:
                display_name = f"\033[1;37m{essid:.20}\033[0m" + ("..." if len(essid) > 20 else "")
            
            # Determine encryption type with icons
            enc_icon = "🔓"
            if "WPA2" in encryption:
                enc_icon = "🔒"
            elif "WPA" in encryption:
                enc_icon = "🔐"
            elif "WEP" in encryption:
                enc_icon = "🗝️ "
            
            enc_display = f"{enc_icon} {encryption.split()[0] if ' ' in encryption else encryption}"
            
            print(f"\033[1;34m│ \033[1;33m{idx:2d}\033[0m \033[1;32m{bssid}\033[0m \033[1;36m{channel:>3}\033[0m \033[1;31m{power:>3}\033[0m \033[1;34m{enc_display:10}\033[0m {display_name:24} \033[1;34m│\033[0m")
        
        print("\033[1;34m└──────────────────────┴────┴─────┴───────────┴──────────────────────────┘\033[0m")
        print(f"\033[1;32m[✓] DISPLAYING {len(self.networks)} NETWORKS\033[0m")

    def select_target(self):
        """Select target from scanned networks"""
        if not self.networks:
            print("\033[1;31m[✘] NO TARGETS AVAILABLE\033[0m")
            return None
        
        try:
            selection = input("\n\033[1;33m[?] SELECT TARGET (1-{}): \033[0m".format(len(self.networks)))
            idx = int(selection)
            
            if 1 <= idx <= len(self.networks):
                target = self.networks[idx]
                print(f"\033[1;32m[✓] TARGET ACQUIRED: {target['essid']}\033[0m")
                return target
            else:
                print("\033[1;31m[✘] INVALID SELECTION\033[0m")
                return None
                
        except ValueError:
            print("\033[1;31m[✘] INVALID INPUT\033[0m")
            return None

    def bluetooth_scan(self):
        """Scan for Bluetooth devices with DEBUG output"""
        print("\033[1;33m[!] SCANNING FOR BLUETOOTH DEVICES...\033[0m")
        
        # Ensure Bluetooth is enabled
        self.core.run_command("systemctl start bluetooth >/dev/null 2>&1")
        self.core.run_command("hciconfig hci0 up >/dev/null 2>&1")
        
        devices = {}
        
        try:
            # Method 1: Use hcitool scan
            print("\033[1;36m[→] USING HCITOOL SCAN...\033[0m")
            result = self.core.run_command("timeout 20s hcitool scan")
            
            print(f"\033[1;35m[DEBUG] hcitool scan result: {result}\033[0m")
            
            if result and result.returncode == 0 and len(result.stdout.strip()) > 10:
                print(f"\033[1;35m[DEBUG] hcitool output: {result.stdout}\033[0m")
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                
                for line in lines:
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 2:
                            mac = parts[0]
                            name = ' '.join(parts[1:]) if len(parts) > 2 else "Unknown Device"
                            
                            # Get device type
                            device_type = self.get_bluetooth_device_type(mac, name)
                            devices[mac] = {
                                'name': name,
                                'type': device_type
                            }
                
                if devices:
                    return devices
            
            # Method 2: Use bluetoothctl if hcitool fails
            print("\033[1;36m[→] TRYING BLUETOOTHCTL SCAN...\033[0m")
            result = self.core.run_command("timeout 20s bluetoothctl scan on")
            time.sleep(3)
            result = self.core.run_command("bluetoothctl devices")
            
            print(f"\033[1;35m[DEBUG] bluetoothctl result: {result}\033[0m")
            
            if result and result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if 'Device' in line:
                        parts = line.split()
                        if len(parts) >= 3:
                            mac = parts[1]
                            name = ' '.join(parts[2:])
                            device_type = self.get_bluetooth_device_type(mac, name)
                            devices[mac] = {
                                'name': name,
                                'type': device_type
                            }
                
                return devices
                
        except Exception as e:
            print(f"\033[1;31m[✘] BLUETOOTH SCAN ERROR: {e}\033[0m")
        
        if not devices:
            print("\033[1;33m[!] NO BLUETOOTH DEVICES FOUND\033[0m")
            print("  • Ensure Bluetooth is enabled on target devices")
            print("  • Make sure devices are discoverable")
            print("  • Try moving closer to devices")
            print("  • Check if Bluetooth adapter is working")
        
        return devices

    def get_bluetooth_device_type(self, mac, name):
        """Determine Bluetooth device type"""
        name_lower = name.lower()
        
        if any(word in name_lower for word in ['airpod', 'airpods', 'earpod', 'headphone', 'headset']):
            return "🎧 Headphones"
        elif any(word in name_lower for word in ['iphone', 'samsung', 'xiaomi', 'huawei', 'phone', 'mobile']):
            return "📱 Phone"
        elif any(word in name_lower for word in ['tablet', 'ipad', 'tab']):
            return "📟 Tablet"
        elif any(word in name_lower for word in ['laptop', 'notebook', 'macbook']):
            return "💻 Laptop"
        elif any(word in name_lower for word in ['watch', 'smartwatch', 'galaxy watch']):
            return "⌚ Smartwatch"
        elif any(word in name_lower for word in ['speaker', 'sound', 'jbl', 'bose']):
            return "🔊 Speaker"
        else:
            return "🔵 Bluetooth Device"
