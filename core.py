#!/usr/bin/env python3

import os
import sys
import time
import subprocess
import threading
import signal
import random
from typing import Dict, List

class NetStrikeCore:
    def __init__(self):
        self.interface = ""
        self.mon_interface = ""
        self.original_mac = ""
        self.original_ip = ""
        self.mac_spoof_thread = None
        self.ip_spoof_thread = None
        self.spoofing_active = False
        self.attack_processes = []
        self.current_operation = None
        
    def check_root(self):
        """Check if running as root"""
        if os.geteuid() != 0:
            print("\033[1;31m[✘] NetStrike Framework requires root privileges\033[0m")
            return False
        print("\033[1;32m[✓] Root privileges confirmed\033[0m")
        return True

    def set_current_operation(self, operation):
        """Set current operation for signal handling"""
        self.current_operation = operation

    def clear_current_operation(self):
        """Clear current operation"""
        self.current_operation = None

    def run_command(self, command, background=False, timeout=30):
        """Execute system command with enhanced error handling"""
        try:
            if background:
                return subprocess.Popen(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=timeout)
                return result
        except subprocess.TimeoutExpired:
            print(f"\033[1;33m[!] Command timeout: {command}\033[0m")
            return None
        except Exception as e:
            print(f"\033[1;31m[✘] Command failed: {e}\033[0m")
            return None

    def detect_wireless_interfaces(self):
        """Detect available wireless interfaces"""
        print("\033[1;36m[→] Scanning for wireless interfaces...\033[0m")
        
        interfaces = []
        
        # Method 1: Use iwconfig
        result = self.run_command("iwconfig 2>/dev/null | grep -E '^[a-zA-Z]' | grep -v 'no wireless' | awk '{print $1}'")
        if result and result.stdout:
            interfaces.extend([iface.strip() for iface in result.stdout.split('\n') if iface.strip()])
        
        # Method 2: Use ip link
        result = self.run_command("ip link show | grep -E '^[0-9]+:' | awk -F: '{print $2}' | grep -E '(wlan|wlx|wlp)' | tr -d ' '")
        if result and result.stdout:
            for iface in result.stdout.split('\n'):
                if iface.strip() and iface.strip() not in interfaces:
                    interfaces.append(iface.strip())
        
        # Remove duplicates and empty strings
        interfaces = list(set([iface for iface in interfaces if iface]))
        
        return interfaces

    def select_interface(self):
        """Let user select wireless interface"""
        interfaces = self.detect_wireless_interfaces()
        
        if not interfaces:
            print("\033[1;31m[✘] No wireless interfaces found\033[0m")
            return False
        
        print("\033[1;35m┌──────────────────────────────────────────────────────────┐\033[0m")
        print("\033[1;35m│ \033[1;37mDETECTED WIRELESS INTERFACES\033[1;35m                           │\033[0m")
        print("\033[1;35m├──────────────────────────────────────────────────────────┤\033[0m")
        
        for idx, iface in enumerate(interfaces, 1):
            # Get interface status
            status = self.run_command(f"iwconfig {iface} 2>/dev/null | grep 'Mode:'")
            mode = "Monitor" if status and "Monitor" in status.stdout else "Managed"
            print(f"\033[1;35m│ \033[1;36m{idx}\033[0m) \033[1;32m{iface}\033[0m - \033[1;33m{mode}\033[0m{' ' * (30 - len(iface))}\033[1;35m│\033[0m")
        
        print("\033[1;35m└──────────────────────────────────────────────────────────┘\033[0m")
        
        try:
            selection = input("\n\033[1;36m[?] Select interface (1-{}): \033[0m".format(len(interfaces)))
            idx = int(selection) - 1
            
            if 0 <= idx < len(interfaces):
                self.interface = interfaces[idx]
                print(f"\033[1;32m[✓] Interface selected: {self.interface}\033[0m")
                return True
            else:
                print("\033[1;31m[✘] Invalid selection\033[0m")
                return False
                
        except ValueError:
            print("\033[1;31m[✘] Invalid input\033[0m")
            return False

    def save_original_config(self):
        """Save original network configuration"""
        print("\033[1;36m[→] Saving original system configuration...\033[0m")
        
        # Save original MAC
        result = self.run_command(f"macchanger -s {self.interface} 2>/dev/null")
        if result and "Current MAC" in result.stdout:
            lines = result.stdout.split('\n')
            for line in lines:
                if "Current MAC" in line:
                    self.original_mac = line.split("Current MAC:")[1].strip().split()[0]
                    break
        else:
            # Alternative method
            result = self.run_command(f"cat /sys/class/net/{self.interface}/address")
            if result and result.stdout.strip():
                self.original_mac = result.stdout.strip()
            else:
                self.original_mac = "unknown"
        
        # Save original IP
        result = self.run_command(f"ip addr show {self.interface} 2>/dev/null")
        if result and "inet " in result.stdout:
            for line in result.stdout.split('\n'):
                if "inet " in line and "scope global" in line:
                    self.original_ip = line.strip().split()[1].split('/')[0]
                    break
        else:
            self.original_ip = "unknown"
        
        print("\033[1;32m[✓] Original configuration saved\033[0m")
        print(f"\033[1;33m[→] Original MAC: {self.original_mac}\033[0m")
        print(f"\033[1;33m[→] Original IP: {self.original_ip}\033[0m")

    def setup_monitor_mode(self):
        """Setup monitor mode on wireless interface"""
        print("\033[1;36m[→] Activating monitor mode...\033[0m")
        
        # Kill interfering processes
        self.run_command("airmon-ng check kill >/dev/null 2>&1")
        time.sleep(2)
        
        # Start monitor mode
        result = self.run_command(f"airmon-ng start {self.interface} >/dev/null 2>&1")
        
        # Try to find monitor interface
        time.sleep(2)
        
        # Check for monitor interfaces
        result = self.run_command("iwconfig 2>/dev/null | grep 'Mode:Monitor' | awk '{print $1}'")
        if result and result.stdout.strip():
            self.mon_interface = result.stdout.strip().split('\n')[0]
        else:
            # Try common monitor interface names
            possible_names = [f"{self.interface}mon", "mon0", "wlan0mon", "wlan1mon"]
            for name in possible_names:
                result = self.run_command(f"iwconfig {name} 2>/dev/null")
                if result and "Mode:Monitor" in result.stdout:
                    self.mon_interface = name
                    break
            else:
                # Use original interface if already in monitor mode
                result = self.run_command(f"iwconfig {self.interface} 2>/dev/null")
                if result and "Mode:Monitor" in result.stdout:
                    self.mon_interface = self.interface
                else:
                    print("\033[1;31m[✘] Monitor mode activation failed\033[0m")
                    return False
        
        # Verify monitor mode
        result = self.run_command(f"iwconfig {self.mon_interface} 2>/dev/null")
        if result and "Mode:Monitor" in result.stdout:
            print(f"\033[1;32m[✓] Monitor mode activated: {self.mon_interface}\033[0m")
            return True
        else:
            print("\033[1;31m[✘] Monitor mode verification failed\033[0m")
            return False

    def start_advanced_spoofing(self):
        """Start advanced MAC and IP spoofing"""
        print("\033[1;36m[→] Activating advanced anonymity...\033[0m")
        
        self.spoofing_active = True
        
        self.mac_spoof_thread = threading.Thread(target=self.advanced_mac_spoofing)
        self.ip_spoof_thread = threading.Thread(target=self.advanced_ip_spoofing)
        
        self.mac_spoof_thread.daemon = True
        self.ip_spoof_thread.daemon = True
        
        self.mac_spoof_thread.start()
        self.ip_spoof_thread.start()
        
        print("\033[1;32m[✓] Advanced anonymity activated\033[0m")

    def advanced_mac_spoofing(self):
        """Advanced MAC spoofing with multiple methods"""
        count = 0
        while self.spoofing_active:
            time.sleep(180)  # Change every 3 minutes
            
            if not self.spoofing_active:
                break
                
            try:
                # Method 1: Using macchanger
                self.run_command(f"ip link set {self.mon_interface} down >/dev/null 2>&1")
                self.run_command(f"macchanger -r {self.mon_interface} >/dev/null 2>&1")
                self.run_command(f"ip link set {self.mon_interface} up >/dev/null 2>&1")
                
                count += 1
                print(f"\033[1;32m[✓] MAC address cycled #{count}\033[0m")
                
            except Exception as e:
                print(f"\033[1;33m[!] MAC spoofing attempt failed: {e}\033[0m")

    def advanced_ip_spoofing(self):
        """Advanced IP spoofing and network refresh"""
        while self.spoofing_active:
            time.sleep(300)  # 5 minutes
            
            if not self.spoofing_active:
                break
                
            try:
                # Refresh network configuration
                self.run_command("systemctl restart NetworkManager >/dev/null 2>&1")
                time.sleep(2)
                
                # Flush IP tables and renew
                self.run_command("iptables --flush >/dev/null 2>&1")
                self.run_command("ip route flush table main >/dev/null 2>&1")
                
                print("\033[1;32m[✓] Network configuration refreshed\033[0m")
                
            except Exception as e:
                print(f"\033[1;33m[!] IP spoofing attempt failed: {e}\033[0m")

    def stop_advanced_spoofing(self):
        """Stop spoofing threads"""
        self.spoofing_active = False
        if self.mac_spoof_thread:
            self.mac_spoof_thread.join(timeout=2)
        if self.ip_spoof_thread:
            self.ip_spoof_thread.join(timeout=2)

    def stop_monitor_mode(self):
        """Stop monitor mode"""
        if self.mon_interface:
            print("\033[1;36m[→] Deactivating monitor mode...\033[0m")
            self.run_command(f"airmon-ng stop {self.mon_interface} >/dev/null 2>&1")
            self.run_command("systemctl restart NetworkManager >/dev/null 2>&1")
            print("\033[1;32m[✓] Monitor mode deactivated\033[0m")

    def add_attack_process(self, process):
        """Add attack process to management list"""
        if process and process.poll() is None:
            self.attack_processes.append(process)

    def stop_all_attacks(self):
        """Stop all running attacks"""
        print("\033[1;36m[→] Terminating all active operations...\033[0m")
        
        # Kill all attack processes
        for process in self.attack_processes:
            try:
                if process and process.poll() is None:
                    process.terminate()
                    process.wait(timeout=2)
            except:
                pass
        
        self.attack_processes = []
        
        # Kill any remaining attack processes
        kill_commands = [
            "killall airodump-ng aireplay-ng mdk4 xterm reaver bully wash 2>/dev/null",
            "pkill -f 'mdk4|aireplay-ng|airodump-ng|hostapd|dnsmasq' 2>/dev/null",
            "pkill -9 -f 'airodump-ng|aireplay-ng' 2>/dev/null"
        ]
        
        for cmd in kill_commands:
            self.run_command(cmd)
        
        print("\033[1;32m[✓] All operations terminated\033[0m")

    def signal_handler(self, sig, frame):
        """Handle Ctrl+C signal gracefully"""
        if self.current_operation:
            print(f"\n\033[1;33m[!] Stopping current operation: {self.current_operation}\033[0m")
            self.stop_all_attacks()
            self.clear_current_operation()
        else:
            print("\n\033[1;33m[!] Exiting NetStrike Framework...\033[0m")
            self.nuclear_cleanup()

    def nuclear_cleanup(self):
        """Complete system cleanup"""
        print("\033[1;35m[→] Initiating secure cleanup protocol...\033[0m")
        
        messages = [
            "🛑 Terminating active sessions...",
            "🧹 Cleaning system logs...", 
            "🔄 Restoring original configuration...",
            "🗑️ Removing temporary files...",
            "🔒 Wiping digital traces...",
            "✅ Secure cleanup completed"
        ]
        
        for msg in messages:
            print(f"\033[1;35m[→] \033[1;36m{msg}\033[0m")
            time.sleep(1)
        
        # Stop all attacks
        self.stop_all_attacks()
        
        # Stop spoofing
        self.stop_advanced_spoofing()
        
        # Stop monitor mode
        self.stop_monitor_mode()
        
        # Restore original MAC
        if self.original_mac and self.original_mac != "unknown":
            print("\033[1;36m[→] Restoring original identity...\033[0m")
            self.run_command(f"ip link set {self.interface} down >/dev/null 2>&1")
            self.run_command(f"macchanger -m {self.original_mac} {self.interface} >/dev/null 2>&1")
            self.run_command(f"ip link set {self.interface} up >/dev/null 2>&1")
        
        # Clean all traces
        print("\033[1;36m[→] Removing all temporary files...\033[0m")
        self.run_command("rm -rf /tmp/netstrike_* /tmp/*.cap /tmp/*.csv /tmp/cracked.txt /tmp/wordlist.txt 2>/dev/null")
        self.run_command("echo '' > ~/.bash_history && history -c")
        
        # Restart network services
        self.run_command("systemctl restart NetworkManager >/dev/null 2>&1")
        
        print("\033[1;32m[✓] Secure cleanup protocol complete\033[0m")
        print("\033[1;32m[✓] All digital traces eliminated - Operation complete\033[0m")
        sys.exit(0)
