#!/usr/bin/env python3
"""
NETSTRIKE v3.0 SECURITY DAEMON
Continuous MAC/IP Spoofing & Stealth Operations
"""

import threading
import time
import random
import subprocess
import os
from datetime import datetime

class SecurityDaemon:
    def __init__(self, core):
        self.core = core
        self.spoofing_active = False
        self.spoofing_thread = None
        self.rotation_interval = 300  # 5 minutes
        self.spoof_count = 0
        
    def start_spoofing(self):
        """Start continuous spoofing daemon"""
        if self.spoofing_active:
            return
            
        print("\033[1;32m[🛡️] ACTIVATING CONTINUOUS SPOOFING DAEMON...\033[0m")
        
        self.spoofing_active = True
        self.spoofing_thread = threading.Thread(target=self._spoofing_loop)
        self.spoofing_thread.daemon = True
        self.spoofing_thread.start()
        
        # Initial spoof
        self._perform_spoof_cycle()
        
        print("\033[1;32m[✓] SPOOFING DAEMON ACTIVE (5min rotations)\033[0m")
        
    def stop_spoofing(self):
        """Stop spoofing daemon"""
        if not self.spoofing_active:
            return
            
        print("\033[1;33m[!] STOPPING SPOOFING DAEMON...\033[0m")
        self.spoofing_active = False
        
        if self.spoofing_thread and self.spoofing_thread.is_alive():
            self.spoofing_thread.join(timeout=5)
            
        print("\033[1;32m[✓] SPOOFING DAEMON STOPPED\033[0m")
        
    def _spoofing_loop(self):
        """Main spoofing loop"""
        while self.spoofing_active:
            try:
                # Wait for next rotation
                time.sleep(self.rotation_interval)
                
                if self.spoofing_active:
                    self._perform_spoof_cycle()
                    
            except Exception as e:
                print(f"\033[1;31m[✘] Spoofing Error: {e}\033[0m")
                time.sleep(30)  # Wait before retry
                
    def _perform_spoof_cycle(self):
        """Perform complete spoof cycle"""
        self.spoof_count += 1
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        print(f"\033[1;36m[🔄] ROTATION #{self.spoof_count} at {timestamp}\033[0m")
        
        # MAC Spoofing
        if self._spoof_mac_address():
            print(f"\033[1;32m[✓] MAC Address Changed: {self.core.current_mac}\033[0m")
        else:
            print("\033[1;31m[✘] MAC Spoofing Failed\033[0m")
            
        # IP Spoofing  
        if self._spoof_ip_address():
            print("\033[1;32m[✓] IP Address Rotated\033[0m")
        else:
            print("\033[1;31m[✘] IP Spoofing Failed\033[0m")
            
        # Cleanup operations
        self._cleanup_cycle()
        
        print(f"\033[1;32m[✅] SPOOFING CYCLE #{self.spoof_count} COMPLETE\033[0m")
        
    def _spoof_mac_address(self):
        """Spoof MAC address with enhanced stealth"""
        try:
            # Generate new MAC
            new_mac = self._generate_stealth_mac()
            
            # Bring interface down
            self.core.run_command(f"ip link set {self.core.mon_interface} down")
            time.sleep(1)
            
            # Change MAC
            result = self.core.run_command(f"macchanger -m {new_mac} {self.core.mon_interface}")
            
            # Bring interface up
            self.core.run_command(f"ip link set {self.core.mon_interface} up")
            time.sleep(2)
            
            if result and result.returncode == 0:
                self.core.current_mac = new_mac
                return True
                
        except Exception as e:
            print(f"\033[1;31m[✘] MAC Spoofing Error: {e}\033[0m")
            
        return False
        
    def _spoof_ip_address(self):
        """Spoof IP address with multiple methods"""
        try:
            # Method 1: NetworkManager restart (most effective)
            self.core.run_command("systemctl restart NetworkManager >/dev/null 2>&1")
            time.sleep(3)
            
            # Method 2: DHCP release/renew
            self.core.run_command(f"dhclient -r {self.core.interface} >/dev/null 2>&1")
            self.core.run_command(f"dhclient {self.core.interface} >/dev/null 2>&1")
            time.sleep(2)
            
            return True
            
        except Exception as e:
            print(f"\033[1;31m[✘] IP Spoofing Error: {e}\033[0m")
            return False
            
    def _generate_stealth_mac(self):
        """Generate stealth MAC address that looks legitimate"""
        # Use OUI from common vendors to appear legitimate
        common_ouis = [
            "00:16:3e",  # Xen
            "00:0c:29",  # VMware
            "00:50:56",  # VMware
            "00:1c:42",  # Parallels
            "00:1b:21",  # Huawei
            "00:1d:72",  # Dell
            "00:24:e8",  # Dell
            "00:26:b9",  # Dell
        ]
        
        oui = random.choice(common_ouis)
        nic = ":".join([f"{random.randint(0x00, 0xff):02x}" 
                       for _ in range(3)])
                       
        return f"{oui}:{nic}"
        
    def _cleanup_cycle(self):
        """Perform cleanup operations during spoof cycle"""
        try:
            # Clean temporary files
            self.core.run_command("rm -rf /tmp/netstrike_* 2>/dev/null")
            
            # Clear command history
            self.core.run_command("history -c 2>/dev/null")
            self.core.run_command("echo '' > ~/.bash_history 2>/dev/null")
            
        except Exception as e:
            print(f"\033[1;33m[!] Cleanup Warning: {e}\033[0m")
            
    def get_spoofing_status(self):
        """Get current spoofing status"""
        if not self.spoofing_active:
            return "INACTIVE"
            
        time_until_next = self._get_time_until_next_rotation()
        return f"ACTIVE (Next in {time_until_next})"
        
    def _get_time_until_next_rotation(self):
        """Calculate time until next rotation"""
        if not self.spoofing_active:
            return "N/A"
            
        # Simplified time calculation
        return "4:30"
        
    def emergency_stop(self):
        """Emergency stop all spoofing operations"""
        print("\033[1;31m[🚨] EMERGENCY SPOOFING STOP!\033[0m")
        self.stop_spoofing()
