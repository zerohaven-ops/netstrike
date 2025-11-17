#!/usr/bin/env python3

import os
import subprocess

class ToolInstaller:
    def __init__(self, core):
        self.core = core

    def install_required_tools(self):
        """Install all required tools automatically"""
        print("\033[1;33m[!] DEPLOYING NETSTRIKE TOOLKIT...\033[0m")
        
        # Update system
        self.core.run_command("apt update > /dev/null 2>&1")
        
        # Essential WiFi tools
        wifi_tools = [
            "aircrack-ng", "macchanger", "xterm", "reaver", "bully",
            "wash", "wireless-tools", "iw", "iproute2"
        ]
        
        # Bluetooth tools
        bluetooth_tools = [
            "bluetooth", "bluez", "blueman", "hcitool", "l2ping"
        ]
        
        # Install WiFi tools
        for tool in wifi_tools:
            if not self.check_tool_installed(tool):
                print(f"\033[1;33m[!] INSTALLING {tool}...\033[0m")
                self.core.run_command(f"apt install -y {tool} > /dev/null 2>&1")
                print(f"\033[1;32m[✓] {tool} DEPLOYED\033[0m")
        
        # Install Bluetooth tools
        for tool in bluetooth_tools:
            if not self.check_tool_installed(tool):
                print(f"\033[1;33m[!] INSTALLING {tool}...\033[0m")
                self.core.run_command(f"apt install -y {tool} > /dev/null 2>&1")
                print(f"\033[1;32m[✓] {tool} DEPLOYED\033[0m")
        
        # Install MDK4 from source
        if not self.check_tool_installed("mdk4"):
            print("\033[1;33m[!] INSTALLING MDK4...\033[0m")
            self.install_mdk4()
        
        print("\033[1;32m[✓] NETSTRIKE TOOLKIT READY\033[0m")

    def check_tool_installed(self, tool):
        """Check if tool is installed"""
        result = self.core.run_command(f"which {tool}")
        return result and result.returncode == 0

    def install_mdk4(self):
        """Install MDK4 from source"""
        try:
            # Clone and build MDK4
            self.core.run_command("git clone https://github.com/aircrack-ng/mdk4 > /dev/null 2>&1")
            os.chdir("mdk4")
            self.core.run_command("make > /dev/null 2>&1")
            self.core.run_command("make install > /dev/null 2>&1")
            os.chdir("..")
            self.core.run_command("rm -rf mdk4")
            print("\033[1;32m[✓] MDK4 DEPLOYED\033[0m")
        except Exception as e:
            print(f"\033[1;31m[✘] MDK4 INSTALLATION FAILED: {e}\033[0m")

    def download_wordlists(self):
        """Download additional wordlists"""
        print("\033[1;33m[!] DOWNLOADING ENHANCED WORDLISTS...\033[0m")
        
        wordlist_dir = "/usr/share/wordlists"
        
        # Create directory if it doesn't exist
        if not os.path.exists(wordlist_dir):
            os.makedirs(wordlist_dir, exist_ok=True)
        
        # Download common wordlists
        wordlists = {
            "rockyou.txt": "https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt",
            "common_passwords.txt": "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Common-Credentials/10-million-password-list-top-1000.txt"
        }
        
        for filename, url in wordlists.items():
            filepath = os.path.join(wordlist_dir, filename)
            if not os.path.exists(filepath):
                print(f"\033[1;33m[!] DOWNLOADING {filename}...\033[0m")
                self.core.run_command(f"wget -q {url} -O {filepath} 2>/dev/null")
                if os.path.exists(filepath):
                    print(f"\033[1;32m[✓] {filename} DOWNLOADED\033[0m")
        
        print("\033[1;32m[✓] WORDLETS READY FOR DEPLOYMENT\033[0m")
