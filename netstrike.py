#!/usr/bin/env python3
"""
NETSTRIKE v3.0 ULTIMATE
Advanced Cyber Warfare Suite
by ZeroHaven Security
"""

import os
import sys
import time
import signal
import threading

# Fix Python path issues
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import all modules with error handling
try:
    from core_engine import NetStrikeCoreV3
    from security_daemon import SecurityDaemon
    from ui_animations import CyberUI
    from scanner_advanced import AdvancedScanner
    from freeze_attack import FreezeAttack
    from mass_destruction import MassDestruction
    from router_destroyer import RouterDestroyer
    from password_cracker import PasswordCracker
    from evil_twin_advanced import EvilTwinAdvanced
    from zero_existence import ZeroExistence
except ImportError as e:
    print(f"\033[1;31m[✘] IMPORT ERROR: {e}\033[0m")
    print("\033[1;33m[!] Please run the installer first: sudo ./install.sh\033[0m")
    sys.exit(1)

class NetStrikeV3:
    def __init__(self):
        self.core = NetStrikeCoreV3()
        self.security = SecurityDaemon(self.core)
        self.ui = CyberUI()
        self.scanner = AdvancedScanner(self.core)
        self.freeze = FreezeAttack(self.core, self.scanner)
        self.mass_destruction = MassDestruction(self.core, self.scanner)
        self.router_destroyer = RouterDestroyer(self.core, self.scanner)
        self.password_cracker = PasswordCracker(self.core, self.scanner)
        self.evil_twin = EvilTwinAdvanced(self.core, self.scanner)
        self.zero_existence = ZeroExistence(self.core)
        self.running = True
        
    def display_banner(self):
        """Cinematic hacker banner with animations"""
        self.ui.matrix_rain(3)
        
        banner = """
\033[1;32m
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║                   🚀 NETSTRIKE v3.0 ULTIMATE                     ║
║                   CYBER WARFARE PLATFORM                        ║
║                   MAXIMUM ANONYMITY MODE                        ║
║                   ZERO EXISTENCE PROTOCOL                       ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
\033[0m
        """
        self.ui.type_effect(banner, 0.001)
        
    def startup_sequence(self):
        """Cinematic startup with system initialization"""
        sequences = [
            "🛡️  INITIATING SECURE BOOT SEQUENCE...",
            "🔒 ACTIVATING ENCRYPTED COMMUNICATIONS...",
            "🌐 ESTABLISHING ANONYMOUS TUNNELS...",
            "📡 DEPLOYING STEALTH PROTOCOLS...",
            "⚡ ARMING CYBER WEAPONS SYSTEMS...",
            "🔄 STARTING SPOOFING DAEMON...",
            "✅ NETSTRIKE v3.0 READY FOR COMBAT"
        ]
        
        for seq in sequences:
            self.ui.animated_text(seq, 0.05)
            time.sleep(0.5)
            
    def status_dashboard(self):
        """Real-time system status display"""
        interface = self.core.interface if hasattr(self.core, 'interface') and self.core.interface else "SCANNING..."
        mon_interface = self.core.mon_interface if hasattr(self.core, 'mon_interface') and self.core.mon_interface else "ACTIVATING..."
        
        status = f"""
\033[1;36m
╔══════════════════════════════════════════════════════════════════╗
║                      LIVE SYSTEM STATUS                         ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║   🖥️  INTERFACE:    {interface:<25}           ║
║   📡 MONITOR MODE:  {mon_interface:<25}           ║
║   🔄 MAC SPOOFING:  \033[1;32mACTIVE (5min rotation)\033[1;36m{' ':17}           ║
║   🌐 IP ROTATION:   \033[1;32mACTIVE (5min rotation)\033[1;36m{' ':17}           ║
║   🎯 STEALTH MODE:  \033[1;32mMAXIMUM\033[1;36m{' ':30}           ║
║   ⚡ ATTACK READY:   \033[1;32mALL SYSTEMS ARMED\033[1;36m{' ':20}           ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
\033[0m
        """
        print(status)

    def main_menu(self):
        """Cinematic main menu with real-time animations"""
        while self.running:
            os.system('clear')
            self.display_banner()
            self.status_dashboard()
            
            menu = """
\033[1;31m
╔══════════════════════════════════════════════════════════════════╗
║                   🎯 CYBER WARFARE MENU                         ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║   \033[1;33m[1]\033[0m \033[1;36m❄️  FREEZE WI-FI\033[0m           - Single Target Annihilation        \033[1;31m║\033[0m
║   \033[1;33m[2]\033[0m \033[1;31m💀 MASS DESTRUCTION\033[0m        - Total Network Blackout            \033[1;31m║\033[0m
║   \033[1;33m[3]\033[0m \033[1;34m📡 ADVANCED SCANNING\033[0m       - Deep Network Intelligence         \033[1;31m║\033[0m
║   \033[1;33m[4]\033[0m \033[1;35m🔥 WI-FI DESTROYER\033[0m         - Permanent Router Damage           \033[1;31m║\033[0m
║   \033[1;33m[5]\033[0m \033[1;32m🔓 PASSWORD CRACKING\033[0m       - Guaranteed Access                 \033[1;31m║\033[0m
║   \033[1;33m[6]\033[0m \033[1;33m👥 EVIL TWIN ATTACK\033[0m        - Credential Harvesting             \033[1;31m║\033[0m
║   \033[1;33m[7]\033[0m \033[1;37m🛡️  ZERO EXISTENCE\033[0m         - Complete Forensic Cleanup         \033[1;31m║\033[0m
║                                                                  ║
║   \033[1;33m[0]\033[0m \033[1;31m🚪 EXIT NETSTRIKE\033[0m         - Safe Shutdown & Cleanup           \033[1;31m║\033[0m
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
\033[0m
            """
            print(menu)
            
            try:
                choice = input("\n\033[1;33m[?] SELECT COMBAT OPTION: \033[0m").strip()
            except (EOFError, KeyboardInterrupt):
                self.clean_exit()
                return
            
            if choice == "1":
                self.freeze_wifi()
            elif choice == "2":
                self.mass_destruction()
            elif choice == "3":
                self.advanced_scanning()
            elif choice == "4":
                self.wifi_destroyer()
            elif choice == "5":
                self.password_cracking()
            elif choice == "6":
                self.evil_twin_attack()
            elif choice == "7":
                self.zero_existence()
            elif choice == "0":
                self.clean_exit()
            else:
                self.ui.error_message("INVALID SELECTION")
                input("\n\033[1;33m[!] PRESS ENTER TO CONTINUE...\033[0m")

    def freeze_wifi(self):
        """Single target freeze attack"""
        self.freeze.execute_freeze_attack()
        input("\n\033[1;33m[!] PRESS ENTER TO RETURN...\033[0m")

    def mass_destruction(self):
        """Mass network destruction"""
        self.mass_destruction.execute_mass_destruction()
        input("\n\033[1;33m[!] PRESS ENTER TO RETURN...\033[0m")

    def advanced_scanning(self):
        """Advanced network scanning"""
        if self.scanner.deep_network_scan(10):
            self.scanner.display_scan_results()
        input("\n\033[1;33m[!] PRESS ENTER TO RETURN...\033[0m")

    def wifi_destroyer(self):
        """Permanent router damage"""
        self.router_destroyer.execute_router_destruction()
        input("\n\033[1;33m[!] PRESS ENTER TO RETURN...\033[0m")

    def password_cracking(self):
        """Intelligent password cracking"""
        self.password_cracker.execute_password_attack()
        input("\n\033[1;33m[!] PRESS ENTER TO RETURN...\033[0m")

    def evil_twin_attack(self):
        """Credential harvesting attack"""
        self.evil_twin.execute_evil_twin()
        input("\n\033[1;33m[!] PRESS ENTER TO RETURN...\033[0m")

    def zero_existence(self):
        """Complete forensic cleanup"""
        self.zero_existence.execute_complete_cleanup()
        input("\n\033[1;33m[!] PRESS ENTER TO RETURN...\033[0m")

    def clean_exit(self):
        """Safe shutdown with cleanup"""
        self.ui.type_effect("\n🛡️  INITIATING SAFE SHUTDOWN PROTOCOL...", 0.03)
        self.running = False
        self.security.stop_spoofing()
        self.core.cleanup()
        self.ui.success_message("NETSTRIKE v3.0 SHUTDOWN COMPLETE")
        sys.exit(0)

    def signal_handler(self, sig, frame):
        """Handle Ctrl+C gracefully"""
        self.ui.warning_message("\n🚨 EMERGENCY SHUTDOWN INITIATED!")
        self.clean_exit()

    def run(self):
        """Main execution function"""
        try:
            # Setup signal handler
            signal.signal(signal.SIGINT, self.signal_handler)
            
            # Check root privileges
            if not self.core.check_root():
                return
                
            # Startup sequence
            self.startup_sequence()
            
            # Initialize system
            if self.core.initialize_system():
                # Start security daemon
                self.security.start_spoofing()
                
                # Main menu loop
                self.main_menu()
            else:
                self.ui.error_message("SYSTEM INITIALIZATION FAILED")
                
        except Exception as e:
            self.ui.error_message(f"CRITICAL ERROR: {e}")
            self.clean_exit()

if __name__ == "__main__":
    # Check if running with sudo
    if os.geteuid() != 0:
        print("\033[1;31m[✘] NETSTRIKE v3.0 REQUIRES ROOT PRIVILEGES\033[0m")
        print("\033[1;33m[💡] Run: sudo python3 netstrike.py\033[0m")
        sys.exit(1)
        
    netstrike = NetStrikeV3()
    netstrike.run()
