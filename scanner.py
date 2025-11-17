#!/usr/bin/env python3

import os
import time
import subprocess
import threading
from typing import Dict, List

class NetworkScanner:
    def __init__(self, core):
        self.core = core
        self.networks = {}
        self.clients = {}
        self.scanning = False

    def wifi_scan(self, duration=15):
        """Perform WiFi network scan"""
        print("\033[1;33m[!] INITIATING NETSTRIKE SCAN...\033[0m")
        
        scan_file = "/tmp/netstrike_scan"
        
        # Clear previous scan data
        self.networks = {}
        
        # Remove old scan files
        subprocess.run(f"rm -f {scan_file}*", shell=True)
        
        print("\033[1;36m[→] SCANNING FOR 15 SECONDS...\033[0m")
        
        # Start airodump-ng scan
        scan_process = self.core.run_command(
            f"timeout {duration}s airodump-ng {self.core.mon_interface} --output-format csv -w {scan_file}",
            background=True
        )
        
        # Show progress
        for i in range(duration):
            print(f"\033[1;36m[⌛] SCANNING... {i+1}/{duration} SECONDS\033[0m", end='\r')
            time.sleep(1)
        print()
        
        # Wait for process to finish
        if scan_process:
            scan_process.wait()
        
        # Check if scan was successful
        if os.path.exists(f"{scan_file}-01.csv") and os.path.getsize(f"{scan_file}-01.csv") > 0:
            print("\033[1;32m[✓] SCAN COMPLETED SUCCESSFULLY\033[0m")
            return self.parse_scan_results(f"{scan_file}-01.csv")
        else:
            print("\033[1;31m[✘] SCAN FAILED - NO NETWORKS DETECTED\033[0m")
            return False

    def parse_scan_results(self, scan_file):
        """Parse airodump-ng CSV results"""
        try:
            with open(scan_file, 'r', errors='ignore') as f:
                lines = f.readlines()
            
            networks_section = True
            count = 0
            
            for line in lines:
                line = line.strip()
                
                # Skip empty lines and headers
                if not line or "BSSID" in line or "Station MAC" in line:
                    if "Station MAC" in line:
                        networks_section = False
                    continue
                
                if networks_section:
                    # Parse network line
                    parts = line.split(',')
                    if len(parts) >= 14:
                        bssid = parts[0].strip()
                        if len(bssid) == 17 and ':' in bssid:  # Valid MAC
                            channel = parts[3].strip() if parts[3].strip() else "--"
                            power = parts[8].strip() if parts[8].strip() else "--"
                            encryption = parts[5].strip() if parts[5].strip() else "OPN"
                            essid = parts[13].strip()
                            
                            # Clean ESSID
                            essid = essid.replace('"', '').strip()
                            if not essid or essid == "--":
                                essid = "HIDDEN_SSID"
                            
                            count += 1
                            self.networks[count] = {
                                'bssid': bssid,
                                'channel': channel,
                                'power': power,
                                'encryption': encryption,
                                'essid': essid
                            }
            
            return count > 0
            
        except Exception as e:
            print(f"\033[1;31m[✘] SCAN PARSING ERROR: {e}\033[0m")
            return False

    def display_scan_results(self):
        """Display scanned networks in a beautiful format"""
        if not self.networks:
            print("\033[1;31m[✘] NO NETWORKS FOUND\033[0m")
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
        print(f"\033[1;32m[✓] DETECTED {len(self.networks)} NETWORKS\033[0m")

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
        """Scan for Bluetooth devices with name resolution"""
        print("\033[1;33m[!] SCANNING FOR BLUETOOTH DEVICES...\033[0m")
        
        # Ensure Bluetooth is enabled
        self.core.run_command("systemctl start bluetooth")
        self.core.run_command("hciconfig hci0 up")
        
        devices = {}
        
        try:
            # Scan for devices
            result = self.core.run_command("timeout 30s hcitool scan")
            if result and result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                
                for line in lines:
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 2:
                            mac = parts[0]
                            name = ' '.join(parts[1:]) if len(parts) > 2 else "Unknown"
                            
                            # Get device type
                            device_type = self.get_bluetooth_device_type(mac, name)
                            devices[mac] = {
                                'name': name,
                                'type': device_type
                            }
                
                return devices
                
        except Exception as e:
            print(f"\033[1;31m[✘] BLUETOOTH SCAN ERROR: {e}\033[0m")
        
        return {}

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
