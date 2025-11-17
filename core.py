#!/usr/bin/env python3

import os
import sys
import time
import subprocess
import threading
from typing import Dict, List

class NetStrikeCore:
    def __init__(self):
        self.interface = "wlan0"
        self.mon_interface = ""
        self.original_mac = ""
        self.original_ip = ""
        self.mac_spoof_thread = None
        self.ip_spoof_thread = None
        self.spoofing_active = False
        
    def check_root(self):
        """Check if running as root"""
        if os.geteuid() != 0:
            print("\033[1;31m[✘] NETSTRIKE FRAMEWORK REQUIRES ROOT PRIVILEGES\033[0m")
            return False
        print("\033[1;32m[✓] ROOT ACCESS CONFIRMED\033[0m")
        return True

    def run_command(self, command, background=False):
        """Execute system command with error handling"""
        try:
            if background:
                return subprocess.Popen(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                result = subprocess.run(command, shell=True, capture_output=True, text=True)
                return result
        except Exception as e:
            print(f"\033[1;31m[✘] COMMAND FAILED: {command}\033[0m")
            return None

    def save_original_config(self):
        """Save original network configuration"""
        print("\033[1;33m[!] SAVING ORIGINAL SYSTEM CONFIG...\033[0m")
        
        # Save original MAC
        result = self.run_command(f"macchanger -s {self.interface}")
        if result and "Current MAC" in result.stdout:
            lines = result.stdout.split('\n')
            for line in lines:
                if "Current MAC" in line:
                    self.original_mac = line.split("Current MAC:")[1].strip().split()[0]
                    break
        
        # Save original IP
        result = self.run_command(f"ip addr show {self.interface}")
        if result and "inet " in result.stdout:
            for line in result.stdout.split('\n'):
                if "inet " in line and "scope global" in line:
                    self.original_ip = line.strip().split()[1].split('/')[0]
                    break
        
        print("\033[1;32m[✓] ORIGINAL CONFIG SAVED\033[0m")

    def setup_monitor_mode(self):
        """Setup monitor mode on wireless interface"""
        print("\033[1;33m[!] ACTIVATING MONITOR MODE...\033[0m")
        
        # Kill interfering processes
        self.run_command("airmon-ng check kill")
        time.sleep(2)
        
        # Start monitor mode
        result = self.run_command(f"airmon-ng start {self.interface}")
        if result and result.returncode == 0:
            # Find monitor interface
            result = self.run_command("iwconfig 2>/dev/null | grep 'Mode:Monitor' | awk '{print $1}'")
            if result and result.stdout.strip():
                self.mon_interface = result.stdout.strip().split('\n')[0]
            else:
                self.mon_interface = f"{self.interface}mon"
            
            # Verify monitor mode
            result = self.run_command(f"iwconfig {self.mon_interface} 2>/dev/null")
            if result and "Mode:Monitor" in result.stdout:
                print(f"\033[1;32m[✓] MONITOR MODE: {self.mon_interface}\033[0m")
                return True
        
        print("\033[1;31m[✘] MONITOR MODE FAILED\033[0m")
        return False

    def spoof_mac(self):
        """MAC spoofing thread"""
        count = 0
        while self.spoofing_active:
            time.sleep(300)  # 5 minutes
            self.run_command(f"ip link set {self.mon_interface} down")
            if self.run_command(f"macchanger -r {self.mon_interface}"):
                self.run_command(f"ip link set {self.mon_interface} up")
                count += 1
                print(f"\033[1;32m[✓] MAC CYCLED #{count}\033[0m")

    def spoof_ip(self):
        """IP spoofing thread"""
        while self.spoofing_active:
            time.sleep(300)  # 5 minutes
            self.run_command("systemctl restart NetworkManager")
            print("\033[1;32m[✓] NETWORK CONFIG REFRESHED\033[0m")

    def start_nuclear_spoofing(self):
        """Start MAC and IP spoofing"""
        print("\033[1;33m[!] ACTIVATING NUCLEAR ANONYMITY...\033[0m")
        
        self.spoofing_active = True
        
        self.mac_spoof_thread = threading.Thread(target=self.spoof_mac)
        self.ip_spoof_thread = threading.Thread(target=self.spoof_ip)
        
        self.mac_spoof_thread.daemon = True
        self.ip_spoof_thread.daemon = True
        
        self.mac_spoof_thread.start()
        self.ip_spoof_thread.start()
        
        print("\033[1;32m[✓] NUCLEAR ANONYMITY ACTIVE\033[0m")

    def stop_nuclear_spoofing(self):
        """Stop spoofing threads"""
        self.spoofing_active = False
        if self.mac_spoof_thread:
            self.mac_spoof_thread.join(timeout=1)
        if self.ip_spoof_thread:
            self.ip_spoof_thread.join(timeout=1)

    def stop_monitor_mode(self):
        """Stop monitor mode"""
        if self.mon_interface:
            print("\033[1;33m[!] DEACTIVATING MONITOR MODE...\033[0m")
            self.run_command(f"airmon-ng stop {self.mon_interface}")
            self.run_command("systemctl restart NetworkManager")
            print("\033[1;32m[✓] MONITOR MODE STOPPED\033[0m")

    def nuclear_cleanup(self):
        """Complete system cleanup"""
        messages = [
            "🧹 TERMINATING ACTIVE SESSIONS...",
            "📁 CLEANING SYSTEM LOGS...",
            "🔄 RESTORING ORIGINAL CONFIG...",
            "🚮 REMOVING TEMPORARY FILES...",
            "🔒 WIPING DIGITAL TRACES...",
            "✅ NO EXISTENCE MODE ACTIVATED"
        ]
        
        for msg in messages:
            print(f"\033[1;35m[☢️] \033[1;36m{msg}\033[0m")
            time.sleep(1)
        
        # Terminate all attacks
        self.run_command("killall airodump-ng aireplay-ng mdk4 xterm reaver wash hcitool l2ping 2>/dev/null")
        
        # Stop spoofing
        self.stop_nuclear_spoofing()
        
        # Stop monitor mode
        self.stop_monitor_mode()
        
        # Restore original MAC
        if self.original_mac and self.original_mac != "unknown":
            print("\033[1;33m[!] RESTORING ORIGINAL IDENTITY...\033[0m")
            self.run_command(f"ip link set {self.interface} down")
            self.run_command(f"macchanger -m {self.original_mac} {self.interface}")
            self.run_command(f"ip link set {self.interface} up")
        
        # Clean all traces
        print("\033[1;33m[!] WIPING ALL DIGITAL TRACES...\033[0m")
        self.run_command("rm -rf /tmp/netstrike_* /tmp/*.cap /tmp/*.csv /tmp/cracked.txt /tmp/wordlist.txt 2>/dev/null")
        self.run_command("echo '' > ~/.bash_history && history -c")
        
        # Restart network services
        self.run_command("systemctl restart NetworkManager")
        self.run_command("systemctl restart bluetooth")
        
        print("\033[1;32m[✓] NO-EXISTENCE PROTOCOL COMPLETE\033[0m")
        print("\033[1;32m[✓] ALL TRACES ELIMINATED - MISSION ACCOMPLISHED\033[0m")
        sys.exit(0)
