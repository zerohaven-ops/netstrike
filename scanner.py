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
        """Perform WiFi network scan using multiple methods"""
        print("\033[1;33m[!] INITIATING NETSTRIKE SCAN...\033[0m")
        
        if not self.core.mon_interface:
            print("\033[1;31m[✘] NO MONITOR INTERFACE AVAILABLE\033[0m")
            return False
        
        # Clear previous scan data
        self.networks = {}
        
        print(f"\033[1;36m[→] SCANNING FOR {duration} SECONDS ON {self.core.mon_interface}...\033[0m")
        
        # Try Method 1: Airodump-ng with specific channel hopping
        print("\033[1;36m[→] METHOD 1: AIRODUMP-NG SCAN...\033[0m")
        if self.scan_with_airodump(duration):
            return True
        
        # Try Method 2: Manual channel hopping with airodump
        print("\033[1;36m[→] METHOD 2: CHANNEL HOPPING SCAN...\033[0m")
        if self.scan_with_channel_hopping():
            return True
        
        # Try Method 3: Use wash for WPS networks
        print("\033[1;36m[→] METHOD 3: WPS SCAN...\033[0m")
        if self.scan_with_wash():
            return True
        
        print("\033[1;31m[✘] ALL SCAN METHODS FAILED\033[0m")
        return False

    def scan_with_airodump(self, duration):
        """Method 1: Standard airodump scan"""
        try:
            scan_file = "/tmp/netstrike_scan"
            subprocess.run(f"rm -f {scan_file}* 2>/dev/null", shell=True)
            
            # Run airodump on specific common channels
            cmd = f"timeout {duration}s airodump-ng {self.core.mon_interface} --output-format csv -w {scan_file} --band abg"
            scan_process = self.core.run_command(cmd, background=True)
            
            # Show progress
            for i in range(duration):
                print(f"\033[1;36m[⌛] SCANNING... {i+1}/{duration} SECONDS\033[0m", end='\r')
                time.sleep(1)
            print()
            
            if scan_process:
                scan_process.wait()
            
            # Check results
            csv_file = f"{scan_file}-01.csv"
            if os.path.exists(csv_file) and os.path.getsize(csv_file) > 100:
                return self.parse_scan_results(csv_file)
                
        except Exception as e:
            print(f"\033[1;31m[✘] AIRODUMP SCAN FAILED: {e}\033[0m")
        
        return False

    def scan_with_channel_hopping(self):
        """Method 2: Scan common channels one by one"""
        try:
            common_channels = [1, 6, 11, 2, 3, 4, 5, 7, 8, 9, 10]  # 2.4GHz channels
            scan_file = "/tmp/netstrike_channel"
            
            for channel in common_channels:
                print(f"\033[1;36m[→] SCANNING CHANNEL {channel}...\033[0m")
                
                # Set channel
                self.core.run_command(f"iwconfig {self.core.mon_interface} channel {channel}")
                time.sleep(1)
                
                # Quick scan on this channel
                cmd = f"timeout 3s airodump-ng {self.core.mon_interface} --channel {channel} --output-format csv -w {scan_file}_{channel}"
                self.core.run_command(cmd)
                
                # Parse results
                csv_file = f"{scan_file}_{channel}-01.csv"
                if os.path.exists(csv_file) and os.path.getsize(csv_file) > 100:
                    if self.parse_scan_results(csv_file):
                        return True
            
            # If we found networks in any channel, return them
            return len(self.networks) > 0
            
        except Exception as e:
            print(f"\033[1;31m[✘] CHANNEL HOPPING FAILED: {e}\033[0m")
        
        return False

    def scan_with_wash(self):
        """Method 3: Use wash to find WPS-enabled networks"""
        try:
            print("\033[1;36m[→] SCANNING FOR WPS NETWORKS...\033[0m")
            
            result = self.core.run_command(f"timeout 15s wash -i {self.core.mon_interface}")
            if result and result.returncode == 0 and "BSSID" in result.stdout:
                lines = result.stdout.strip().split('\n')
                count = 0
                
                for line in lines:
                    parts = line.split()
                    if len(parts) >= 6 and ':' in parts[0] and len(parts[0]) == 17:
                        bssid = parts[0]
                        channel = parts[1] if parts[1].isdigit() else "1"
                        power = parts[3] if len(parts) > 3 else "-1"
                        wps_locked = "WPS" if "Yes" in line else "No WPS"
                        
                        # Extract ESSID (usually after WPS status)
                        essid_start = line.find('   ') + 3
                        essid = line[essid_start:].strip() if essid_start > 3 else "WPS_NETWORK"
                        
                        count += 1
                        self.networks[count] = {
                            'bssid': bssid,
                            'channel': channel,
                            'power': power,
                            'encryption': f"WPA2 {wps_locked}",
                            'essid': essid
                        }
                
                if count > 0:
                    print(f"\033[1;32m[✓] FOUND {count} WPS NETWORKS\033[0m")
                    return True
                    
        except Exception as e:
            print(f"\033[1;31m[✘] WPS SCAN FAILED: {e}\033[0m")
        
        return False

    def parse_scan_results(self, scan_file):
        """Parse airodump-ng CSV results"""
        try:
            networks = {}
            count = 0
            
            with open(scan_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
                networks_section = True
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # Check if we've reached the client section
                    if 'Station MAC' in line:
                        networks_section = False
                        continue
                    
                    if networks_section and len(line) > 10:
                        parts = line.split(',')
                        if len(parts) >= 2:
                            bssid = parts[0].strip()
                            if len(bssid) == 17 and ':' in bssid:
                                # Extract basic info with better error handling
                                channel = "1"
                                power = "-1"
                                encryption = "OPN"
                                essid = "HIDDEN_SSID"
                                
                                # Try different column positions
                                if len(parts) > 3 and parts[3].strip():
                                    channel = parts[3].strip()
                                if len(parts) > 8 and parts[8].strip():
                                    power = parts[8].strip()
                                if len(parts) > 5 and parts[5].strip():
                                    encryption = parts[5].strip()
                                if len(parts) > 13 and parts[13].strip():
                                    essid = parts[13].strip().replace('"', '')
                                elif len(parts) > 1 and parts[1].strip():
                                    essid = parts[1].strip().replace('"', '')
                                
                                # Clean data
                                channel = ''.join(filter(str.isdigit, channel)) or "1"
                                if not essid or essid == "--":
                                    essid = "HIDDEN_SSID"
                                
                                count += 1
                                networks[count] = {
                                    'bssid': bssid,
                                    'channel': channel,
                                    'power': power,
                                    'encryption': encryption,
                                    'essid': essid
                                }
            
            # Update networks if we found any
            if networks:
                self.networks = networks
                print(f"\033[1;32m[✓] PARSED {count} NETWORKS\033[0m")
                return True
            
        except Exception as e:
            print(f"\033[1;31m[✘] PARSING ERROR: {e}\033[0m")
        
        return False

    def display_scan_results(self):
        """Display scanned networks"""
        if not self.networks:
            print("\033[1;31m[✘] NO NETWORKS FOUND\033[0m")
            print("\033[1;33m[!] TROUBLESHOOTING TIPS:\033[0m")
            print("  • Ensure you're in range of WiFi networks")
            print("  • Try using a different wireless adapter")
            print("  • Some adapters don't support scanning in monitor mode")
            print("  • Check if networks are on 2.4GHz (5GHz may not be supported)")
            print("  • Try the WPS scan method in the attack menu")
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
        """Scan for Bluetooth devices"""
        print("\033[1;33m[!] SCANNING FOR BLUETOOTH DEVICES...\033[0m")
        
        # Ensure Bluetooth is enabled
        self.core.run_command("systemctl start bluetooth >/dev/null 2>&1")
        self.core.run_command("hciconfig hci0 up >/dev/null 2>&1")
        
        devices = {}
        
        try:
            # Try multiple Bluetooth scanning methods
            methods = [
                ("hcitool", "timeout 20s hcitool scan"),
                ("bluetoothctl", "timeout 10s bluetoothctl scan on && sleep 3 && bluetoothctl devices")
            ]
            
            for method_name, cmd in methods:
                print(f"\033[1;36m[→] TRYING {method_name.upper()}...\033[0m")
                result = self.core.run_command(cmd)
                
                if result and result.returncode == 0 and result.stdout.strip():
                    lines = result.stdout.strip().split('\n')
                    
                    for line in lines:
                        if 'Device' in line or (':' in line and len(line.split()[0]) == 17):
                            parts = line.split()
                            if len(parts) >= 2:
                                mac = parts[1] if 'Device' in line else parts[0]
                                if len(mac) == 17 and ':' in mac:
                                    name = ' '.join(parts[2:]) if 'Device' in line else ' '.join(parts[1:])
                                    name = name or "Unknown Device"
                                    
                                    device_type = self.get_bluetooth_device_type(mac, name)
                                    devices[mac] = {
                                        'name': name,
                                        'type': device_type
                                    }
                    
                    if devices:
                        print(f"\033[1;32m[✓] FOUND {len(devices)} BLUETOOTH DEVICES\033[0m")
                        return devices
            
            if not devices:
                print("\033[1;33m[!] NO BLUETOOTH DEVICES FOUND\033[0m")
                print("  • Make sure Bluetooth is enabled on your devices")
                print("  • Ensure devices are in discoverable mode")
                print("  • Try moving closer to the devices")
                
        except Exception as e:
            print(f"\033[1;31m[✘] BLUETOOTH SCAN ERROR: {e}\033[0m")
        
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
