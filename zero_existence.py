#!/usr/bin/env python3
"""
NETSTRIKE v3.0 ZERO EXISTENCE
Complete Forensic Cleanup & Anti-Forensics
"""

import os
import time
import subprocess
from ui_animations import CyberUI

class ZeroExistence:
    def __init__(self, core):
        self.core = core
        self.ui = CyberUI()
        
    def execute_complete_cleanup(self):
        """Execute complete forensic cleanup"""
        self.ui.attack_header("ZERO EXISTENCE PROTOCOL")
        self.ui.type_effect("🛡️  INITIATING COMPLETE FORENSIC CLEANUP...", 0.03)
        
        # Final confirmation
        confirm = input("\n\033[1;31m[?] TYPE 'CLEAN' TO CONFIRM COMPLETE CLEANUP: \033[0m").strip()
        if confirm.lower() != 'clean':
            self.ui.warning_message("CLEANUP CANCELLED")
            return False
            
        return self._nuclear_cleanup_protocol()
        
    def _nuclear_cleanup_protocol(self):
        """Complete nuclear cleanup protocol"""
        cleanup_steps = [
            ("TERMINATING ALL ATTACK PROCESSES", self._kill_all_processes),
            ("RESTORING ORIGINAL IDENTITY", self._restore_identity),
            ("CLEANING TEMPORARY FILES", self._clean_temporary_files),
            ("WIPING SYSTEM LOGS", self._wipe_logs),
            ("CLEARING COMMAND HISTORY", self._clear_history),
            ("FINALIZING CLEANUP", self._finalize_cleanup)
        ]
        
        for step_name, step_func in cleanup_steps:
            self.ui.type_effect(f"☢️  {step_name}...", 0.02)
            step_func()
            time.sleep(1)
            
        self.ui.success_message("ZERO EXISTENCE PROTOCOL COMPLETE")
        self.ui.type_effect("✅ ALL DIGITAL TRACES ELIMINATED", 0.03)
        self.ui.type_effect("✅ FORENSIC COUNTERMEASURES ACTIVE", 0.03)
        self.ui.type_effect("✅ MISSION ACCOMPLISHED", 0.03)
        
        return True
        
    def _kill_all_processes(self):
        """Kill all NetStrike processes"""
        processes = [
            "airodump-ng", "aireplay-ng", "mdk4", "xterm", "reaver",
            "bully", "wash", "hostapd", "dnsmasq", "hcxdumptool"
        ]
        
        for proc in processes:
            self.core.run_command(f"pkill -9 {proc} 2>/dev/null")
            self.core.run_command(f"pkill -9 -f {proc} 2>/dev/null")
            
    def _restore_identity(self):
        """Restore original MAC and network configuration"""
        if self.core.original_mac and self.core.original_mac != "unknown":
            self.core.run_command(f"ip link set {self.core.interface} down")
            self.core.run_command(f"macchanger -m {self.core.original_mac} {self.core.interface}")
            self.core.run_command(f"ip link set {self.core.interface} up")
            
        # Restart network services
        self.core.run_command("systemctl restart NetworkManager")
        self.core.run_command("systemctl restart networking")
        
    def _clean_temporary_files(self):
        """Remove all temporary files"""
        patterns = [
            "/tmp/netstrike_*",
            "/tmp/*.cap",
            "/tmp/*.csv",
            "/tmp/*.pcapng", 
            "/tmp/*.hash",
            "/tmp/cracked.txt",
            "/tmp/wordlist.txt",
            "/tmp/evil_twin_*",
            "/tmp/*_handshake_*",
            "/tmp/*_pmkid_*"
        ]
        
        for pattern in patterns:
            self.core.run_command(f"rm -rf {pattern} 2>/dev/null")
            
    def _wipe_logs(self):
        """Wipe system logs"""
        log_files = [
            "/var/log/syslog",
            "/var/log/messages",
            "/var/log/kern.log",
            "/var/log/auth.log",
            "/var/log/dmesg"
        ]
        
        for log_file in log_files:
            if os.path.exists(log_file):
                self.core.run_command(f"echo '' > {log_file}")
                
        # Clear journal logs
        self.core.run_command("journalctl --vacuum-time=1seconds")
        
    def _clear_history(self):
        """Clear command history"""
        history_commands = [
            "history -c",
            "echo '' > ~/.bash_history",
            "echo '' > ~/.zsh_history",
            "set +o history"
        ]
        
        for cmd in history_commands:
            self.core.run_command(cmd)
            
    def _finalize_cleanup(self):
        """Final cleanup steps"""
        # Stop monitor mode
        if self.core.mon_interface:
            self.core.run_command(f"airmon-ng stop {self.core.mon_interface} 2>/dev/null")
            
        # Clear RAM (simplified)
        self.core.run_command("sync && echo 3 > /proc/sys/vm/drop_caches")
        
        # Restart services
        self.core.run_command("systemctl restart bluetooth")
