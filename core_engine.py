#!/usr/bin/env python3
"""
NETSTRIKE v3.0 CORE ENGINE
Advanced System Management & Stealth Operations
"""

import os
import sys
import time
import subprocess
import threading
import random
import hashlib
import signal
from typing import List, Dict

class NetStrikeCoreV3:
    def __init__(self):
        self.interface = ""
        self.mon_interface = ""
        self.original_mac = ""
        self.current_mac = ""
        self.original_ip = ""
        self.attack_processes = []
        self.stealth_mode = True
        self.spoofing_active = False
        self.system_initialized = False
        self.current_operation = None
        
    def check_root(self):
        """Verify root privileges with cinematic display"""
        if os.geteuid() != 0:
            print("\033[1;31m[✘] NETSTRIKE v3.0 REQUIRES ROOT PRIVILEGES\033[0m")
            print("\033[1;33m[💡] Run: sudo python3 netstrike.py\033[0m")
            return False
            
        print("\033[1;32m[✓] ROOT PRIVILEGES CONFIRMED\033[0m")
        return True
        
    def initialize_system(self):
        """Complete system initialization with better error handling"""
        print("\033[1;36m[⚡] INITIALIZING NETSTRIKE v3.0 SYSTEMS...\033[0m")
        
        steps = [
            ("DETECTING WIRELESS INTERFACES", self.detect_interfaces),
            ("SAVING ORIGINAL CONFIGURATION", self.save_original_config),
            ("ACTIVATING MONITOR MODE", self.setup_monitor_mode),
            ("VERIFYING SYSTEM READINESS", self.verify_system)
        ]
        
        for step_name, step_func in steps:
            print(f"\033[1;33m[→] {step_name}...\033[0m", end="", flush=True)
            success = step_func()
            if success:
                print(f"\r\033[1;32m[✓] {step_name}\033[0m")
            else:
                print(f"\r\033[1;31m[✘] {step_name}\033[0m")
                # Show detailed error for the failed step
                self._show_step_error(step_name)
                return False
            time.sleep(0.5)
            
        self.system_initialized = True
        return True

    def _show_step_error(self, step_name):
        """Show detailed error information for failed steps"""
        if step_name == "DETECTING WIRELESS INTERFACES":
            print("\033[1;31m[!] No wireless interfaces found!\033[0m")
            print("\033[1;33m[💡] Make sure you have a wireless adapter connected\033[0m")
            print("\033[1;33m[💡] Check with: iwconfig\033[0m")
            
        elif step_name == "ACTIVATING MONITOR MODE":
            print("\033[1;31m[!] Failed to activate monitor mode!\033[0m")
            print("\033[1;33m[💡] Try manually: sudo airmon-ng start wlan0\033[0m")
            print("\033[1;33m[💡] Check if your adapter supports monitor mode\033[0m")
            
        elif step_name == "VERIFYING SYSTEM READINESS":
            print("\033[1;31m[!] System verification failed!\033[0m")
            print(f"\033[1;33m[📊] Interface: {self.interface}\033[0m")
            print(f"\033[1;33m[📊] Monitor Interface: {self.mon_interface}\033[0m")
            print(f"\033[1;33m[📊] Original MAC: {self.original_mac}\033[0m")
            print("\033[1;33m[💡] Try restarting the tool or check your wireless adapter\033[0m")
        
    def detect_interfaces(self):
        """Advanced wireless interface detection with fallbacks"""
        interfaces = []
        
        print("\n\033[1;36m[🔍] Scanning for wireless interfaces...\033[0m")
        
        # Method 1: iwconfig detection
        result = self.run_command("iwconfig 2>/dev/null | grep -E '^[a-zA-Z]' | grep -v 'no wireless' | awk '{print $1}'")
        if result and result.stdout:
            found = [iface.strip() for iface in result.stdout.split('\n') if iface.strip()]
            interfaces.extend(found)
            print(f"\033[1;33m[📡] iwconfig found: {found}\033[0m")
            
        # Method 2: ip link detection
        result = self.run_command("ip link show | grep -E '^[0-9]+:' | awk -F: '{print $2}' | grep -E '(wlan|wlx|wlp)' | tr -d ' '")
        if result and result.stdout:
            found = []
            for iface in result.stdout.split('\n'):
                if iface.strip() and iface.strip() not in interfaces:
                    found.append(iface.strip())
                    interfaces.append(iface.strip())
            if found:
                print(f"\033[1;33m[📡] ip link found: {found}\033[0m")
                    
        # Method 3: Direct device check
        if not interfaces:
            common_interfaces = ["wlan0", "wlan1", "wlp2s0", "wlx00c0caa5c4e0"]
            for iface in common_interfaces:
                result = self.run_command(f"iwconfig {iface} 2>/dev/null")
                if result and "no wireless" not in result.stdout:
                    interfaces.append(iface)
                    print(f"\033[1;33m[📡] Direct check found: {iface}\033[0m")
                    break
                    
        if not interfaces:
            print("\033[1;31m[✘] No wireless interfaces detected!\033[0m")
            return False
            
        # Auto-select first available interface
        self.interface = interfaces[0]
        print(f"\033[1;32m[✓] Selected interface: {self.interface}\033[0m")
        return True
        
    def save_original_config(self):
        """Save original system configuration with fallbacks"""
        print(f"\033[1;36m[💾] Saving original configuration for {self.interface}...\033[0m")
        
        # Save original MAC
        result = self.run_command(f"macchanger -s {self.interface} 2>/dev/null")
        if result and "Current MAC" in result.stdout:
            for line in result.stdout.split('\n'):
                if "Current MAC" in line:
                    self.original_mac = line.split("Current MAC:")[1].strip().split()[0]
                    self.current_mac = self.original_mac
                    print(f"\033[1;32m[✓] Original MAC: {self.original_mac}\033[0m")
                    break
        else:
            # Fallback MAC detection
            result = self.run_command(f"cat /sys/class/net/{self.interface}/address 2>/dev/null")
            if result and result.stdout.strip():
                self.original_mac = result.stdout.strip()
                self.current_mac = self.original_mac
                print(f"\033[1;32m[✓] Original MAC (fallback): {self.original_mac}\033[0m")
            else:
                self.original_mac = "unknown"
                print("\033[1;33m[⚠️] Could not detect original MAC\033[0m")
                    
        # Save original IP
        result = self.run_command(f"ip addr show {self.interface} 2>/dev/null")
        if result and "inet " in result.stdout:
            for line in result.stdout.split('\n'):
                if "inet " in line and "scope global" in line:
                    self.original_ip = line.strip().split()[1].split('/')[0]
                    print(f"\033[1;32m[✓] Original IP: {self.original_ip}\033[0m")
                    break
        else:
            self.original_ip = "unknown"
            print("\033[1;33m[⚠️] Could not detect original IP\033[0m")
                    
        return True
        
    def setup_monitor_mode(self):
        """Activate monitor mode with multiple methods"""
        print(f"\033[1;36m[📡] Activating monitor mode on {self.interface}...\033[0m")
        
        # Kill interfering processes
        print("\033[1;33m[→] Stopping network services...\033[0m")
        self.run_command("airmon-ng check kill >/dev/null 2>&1")
        time.sleep(2)
        
        # Method 1: airmon-ng
        print("\033[1;33m[→] Starting monitor mode (Method 1)...\033[0m")
        result = self.run_command(f"airmon-ng start {self.interface} >/dev/null 2>&1")
        time.sleep(3)
        
        # Detect monitor interface
        monitor_interfaces = []
        
        # Check existing monitor interfaces
        result = self.run_command("iwconfig 2>/dev/null | grep 'Mode:Monitor' | awk '{print $1}'")
        if result and result.stdout.strip():
            found = result.stdout.strip().split('\n')
            monitor_interfaces.extend(found)
            print(f"\033[1;33m[📡] Found monitor interfaces: {found}\033[0m")
            
        # Check common monitor interface names
        common_names = [f"{self.interface}mon", "mon0", "wlan0mon", "wlan1mon"]
        for name in common_names:
            result = self.run_command(f"iwconfig {name} 2>/dev/null")
            if result and "Mode:Monitor" in result.stdout:
                if name not in monitor_interfaces:
                    monitor_interfaces.append(name)
                    print(f"\033[1;33m[📡] Found monitor interface: {name}\033[0m")
                
        if monitor_interfaces:
            self.mon_interface = monitor_interfaces[0]
            print(f"\033[1;32m[✓] Monitor mode activated: {self.mon_interface}\033[0m")
            return True
            
        # Method 2: Manual monitor mode
        print("\033[1;33m[→] Trying manual monitor mode...\033[0m")
        self.run_command(f"ip link set {self.interface} down")
        self.run_command(f"iw dev {self.interface} set type monitor")
        self.run_command(f"ip link set {self.interface} up")
        time.sleep(2)
        
        # Check if manual mode worked
        result = self.run_command(f"iwconfig {self.interface} 2>/dev/null")
        if result and "Mode:Monitor" in result.stdout:
            self.mon_interface = self.interface
            print(f"\033[1;32m[✓] Manual monitor mode activated\033[0m")
            return True
            
        print("\033[1;31m[✘] Failed to activate monitor mode!\033[0m")
        return False
        
    def verify_system(self):
        """Verify all systems are operational with lenient checks"""
        print("\033[1;36m[🔍] Verifying system readiness...\033[0m")
        
        checks = [
            ("Wireless Interface", self.interface, True),
            ("Monitor Interface", self.mon_interface, True),
            ("Original MAC", self.original_mac, False),  # MAC can be unknown
            ("Original IP", self.original_ip, False)     # IP can be unknown
        ]
        
        all_critical_ok = True
        
        for check_name, check_value, is_critical in checks:
            if check_value and check_value != "unknown":
                print(f"\033[1;32m[✓] {check_name}: {check_value}\033[0m")
            elif not check_value and is_critical:
                print(f"\033[1;31m[✘] {check_name}: NOT SET\033[0m")
                all_critical_ok = False
            else:
                print(f"\033[1;33m[⚠️] {check_name}: {check_value if check_value else 'NOT SET'}\033[0m")
                
        if not all_critical_ok:
            print("\033[1;31m[✘] Critical systems not ready!\033[0m")
            return False
            
        print("\033[1;32m[✓] All critical systems ready!\033[0m")
        return True
        
    def generate_random_mac(self):
        """Generate random MAC address"""
        mac = [0x00, 0x16, 0x3e,
               random.randint(0x00, 0x7f),
               random.randint(0x00, 0xff),
               random.randint(0x00, 0xff)]
        return ':'.join(map(lambda x: "%02x" % x, mac))
        
    def spoof_mac_address(self):
        """Spoof MAC address with stealth techniques"""
        new_mac = self.generate_random_mac()
        
        try:
            # Bring interface down
            self.run_command(f"ip link set {self.mon_interface} down")
            
            # Change MAC address
            result = self.run_command(f"macchanger -m {new_mac} {self.mon_interface}")
            
            # Bring interface up
            self.run_command(f"ip link set {self.mon_interface} up")
            
            if result and result.returncode == 0:
                self.current_mac = new_mac
                return True
                
        except Exception as e:
            print(f"\033[1;31m[✘] MAC Spoofing Error: {e}\033[0m")
            
        return False
        
    def spoof_ip_address(self):
        """Spoof IP address with multiple methods"""
        try:
            # Method 1: NetworkManager restart
            self.run_command("systemctl restart NetworkManager >/dev/null 2>&1")
            
            # Method 2: DHCP renewal
            self.run_command(f"dhclient -r {self.interface} >/dev/null 2>&1")
            self.run_command(f"dhclient {self.interface} >/dev/null 2>&1")
            
            return True
            
        except Exception as e:
            print(f"\033[1;31m[✘] IP Spoofing Error: {e}\033[0m")
            return False

    def set_current_operation(self, operation):
        """Set current operation for signal handling"""
        self.current_operation = operation

    def clear_current_operation(self):
        """Clear current operation"""
        self.current_operation = None
            
    def run_command(self, command, background=False):
        """Execute system command with enhanced error handling"""
        try:
            if background:
                process = subprocess.Popen(
                    command, 
                    shell=True, 
                    stdout=subprocess.DEVNULL, 
                    stderr=subprocess.DEVNULL,
                    preexec_fn=os.setsid
                )
                return process
            else:
                result = subprocess.run(
                    command, 
                    shell=True, 
                    capture_output=True, 
                    text=True,
                    timeout=30
                )
                return result
                
        except subprocess.TimeoutExpired:
            return None
        except Exception as e:
            return None
            
    def hide_process(self, process):
        """Hide process from system monitoring"""
        if not self.stealth_mode:
            return
            
        try:
            # Rename process for stealth
            import ctypes
            libc = ctypes.CDLL("libc.so.6")
            libc.prctl(15, b"[kworker]", 0, 0, 0)
        except:
            pass
            
    def add_attack_process(self, process):
        """Add attack process to management list"""
        self.hide_process(process)
        self.attack_processes.append(process)
        
    def stop_all_attacks(self):
        """Stop all running attacks with stealth"""
        if not self.attack_processes:
            return
            
        print("\033[1;33m[!] TERMINATING ALL ATTACK PROCESSES...\033[0m")
        
        for process in self.attack_processes:
            try:
                if process and process.poll() is None:
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                    process.wait(timeout=5)
            except:
                pass
                
        # Cleanup any remaining processes
        self.run_command("pkill -f 'mdk4|aireplay-ng|airodump-ng|hostapd|dnsmasq|reaver' 2>/dev/null")
        
        self.attack_processes = []
        print("\033[1;32m[✓] ALL ATTACKS TERMINATED\033[0m")
        
    def zero_existence_cleanup(self):
        """Complete forensic cleanup protocol"""
        print("\033[1;31m[☢️] INITIATING ZERO EXISTENCE PROTOCOL...\033[0m")
        
        cleanup_steps = [
            ("TERMINATING ALL ATTACK PROCESSES", self.stop_all_attacks),
            ("RESTORING ORIGINAL IDENTITY", self.restore_original_identity),
            ("CLEANING TEMPORARY FILES", self.clean_temporary_files),
            ("WIPING SYSTEM LOGS", self.wipe_system_logs),
            ("FINALIZING CLEANUP", self.finalize_cleanup)
        ]
        
        for step_name, step_func in cleanup_steps:
            print(f"\033[1;35m[☢️] {step_name}...\033[0m")
            step_func()
            time.sleep(1)
            
        print("\033[1;32m[✓] ZERO EXISTENCE PROTOCOL COMPLETE\033[0m")
        
    def restore_original_identity(self):
        """Restore original MAC and configuration"""
        if self.original_mac and self.original_mac != "unknown":
            self.run_command(f"ip link set {self.interface} down")
            self.run_command(f"macchanger -m {self.original_mac} {self.interface}")
            self.run_command(f"ip link set {self.interface} up")
            
    def clean_temporary_files(self):
        """Remove all temporary files"""
        temp_files = [
            "/tmp/netstrike_*",
            "/tmp/*.cap",
            "/tmp/*.csv", 
            "/tmp/*.pcapng",
            "/tmp/*.hash",
            "/tmp/cracked.txt",
            "/tmp/wordlist.txt"
        ]
        
        for pattern in temp_files:
            self.run_command(f"rm -rf {pattern} 2>/dev/null")
            
    def wipe_system_logs(self):
        """Clean system logs"""
        log_commands = [
            "echo '' > /var/log/syslog",
            "echo '' > /var/log/messages",
            "journalctl --vacuum-time=1seconds",
            "history -c",
            "echo '' > ~/.bash_history"
        ]
        
        for cmd in log_commands:
            self.run_command(cmd)
            
    def finalize_cleanup(self):
        """Final cleanup steps"""
        self.run_command("systemctl restart NetworkManager")
        self.run_command("systemctl restart bluetooth")
        
    def cleanup(self):
        """Complete system cleanup"""
        if self.system_initialized:
            self.stop_all_attacks()
            self.restore_original_identity()
            self.clean_temporary_files()

    def signal_handler(self, sig, frame):
        """Handle Ctrl+C signal gracefully"""
        if self.current_operation:
            print(f"\n\033[1;33m[!] STOPPING CURRENT OPERATION: {self.current_operation}\033[0m")
            self.stop_all_attacks()
            self.clear_current_operation()
        else:
            print("\n\033[1;33m[!] EXITING NETSTRIKE FRAMEWORK...\033[0m")
            self.cleanup()
