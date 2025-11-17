#!/usr/bin/env python3

import os
import subprocess
import time

class ToolInstaller:
    def __init__(self, core):
        self.core = core

    def install_required_tools(self):
        """Install all required tools automatically with NetStrike style"""
        print("\033[1;33m[!] DEPLOYING NETSTRIKE TOOLKIT...\033[0m")
        print("\033[1;36m[⚡] INITIATING ADVANCED TOOL DEPLOYMENT...\033[0m")
        
        # Update system
        print("\033[1;33m[!] UPDATING SYSTEM REPOSITORIES...\033[0m")
        self.core.run_command("apt update > /dev/null 2>&1")
        
        # Essential WiFi tools
        wifi_tools = [
            "aircrack-ng", "macchanger", "xterm", "reaver", "bully",
            "wash", "wireless-tools", "iw", "iproute2", "hostapd",
            "dnsmasq", "net-tools"
        ]
        
        # Advanced cracking tools
        advanced_tools = [
            "hashcat", "hcxdumptool", "hcxtools", "python3-pip"
        ]
        
        # Bluetooth tools
        bluetooth_tools = [
            "bluetooth", "bluez", "blueman", "hcitool", "l2ping", "bluetoothctl"
        ]
        
        # Python packages
        python_packages = [
            "requests", "scapy"
        ]
        
        # Install WiFi tools
        print("\033[1;33m[!] INSTALLING WI-FI WARFARE TOOLS...\033[0m")
        for tool in wifi_tools:
            if not self.check_tool_installed(tool):
                print(f"\033[1;33m[→] DEPLOYING {tool.upper()}...\033[0m")
                result = self.core.run_command(f"apt install -y {tool} > /dev/null 2>&1")
                if result and result.returncode == 0:
                    print(f"\033[1;32m[✓] {tool.upper()} DEPLOYED\033[0m")
                else:
                    print(f"\033[1;31m[✘] {tool.upper()} DEPLOYMENT FAILED\033[0m")
        
        # Install advanced tools
        print("\033[1;33m[!] INSTALLING ADVANCED CRACKING TOOLS...\033[0m")
        for tool in advanced_tools:
            if not self.check_tool_installed(tool):
                print(f"\033[1;33m[→] DEPLOYING {tool.upper()}...\033[0m")
                result = self.core.run_command(f"apt install -y {tool} > /dev/null 2>&1")
                if result and result.returncode == 0:
                    print(f"\033[1;32m[✓] {tool.upper()} DEPLOYED\033[0m")
                else:
                    print(f"\033[1;31m[✘] {tool.upper()} DEPLOYMENT FAILED\033[0m")
        
        # Install Bluetooth tools
        print("\033[1;33m[!] INSTALLING BLUETOOTH ASSAULT TOOLS...\033[0m")
        for tool in bluetooth_tools:
            if not self.check_tool_installed(tool):
                print(f"\033[1;33m[→] DEPLOYING {tool.upper()}...\033[0m")
                result = self.core.run_command(f"apt install -y {tool} > /dev/null 2>&1")
                if result and result.returncode == 0:
                    print(f"\033[1;32m[✓] {tool.upper()} DEPLOYED\033[0m")
                else:
                    print(f"\033[1;31m[✘] {tool.upper()} DEPLOYMENT FAILED\033[0m")
        
        # Install Python packages
        print("\033[1;33m[!] INSTALLING PYTHON ENHANCEMENTS...\033[0m")
        for package in python_packages:
            print(f"\033[1;33m[→] DEPLOYING {package.upper()}...\033[0m")
            result = self.core.run_command(f"pip3 install {package} > /dev/null 2>&1")
            if result and result.returncode == 0:
                print(f"\033[1;32m[✓] {package.upper()} DEPLOYED\033[0m")
            else:
                print(f"\033[1;31m[✘] {package.upper()} DEPLOYMENT FAILED\033[0m")
        
        # Install MDK4 from source
        if not self.check_tool_installed("mdk4"):
            print("\033[1;33m[!] DEPLOYING MDK4 NUCLEAR WEAPON...\033[0m")
            if self.install_mdk4():
                print("\033[1;32m[✓] MDK4 NUCLEAR WEAPON DEPLOYED\033[0m")
            else:
                print("\033[1;31m[✘] MDK4 DEPLOYMENT FAILED\033[0m")
        
        # Download wordlists
        print("\033[1;33m[!] DEPLOYING CRACKING WORDLISTS...\033[0m")
        self.download_wordlists()
        
        print("\033[1;32m[✓] NETSTRIKE TOOLKIT READY FOR COMBAT\033[0m")
        print("\033[1;32m[✓] ALL SYSTEMS GO - READY FOR DEPLOYMENT\033[0m")

    def check_tool_installed(self, tool):
        """Check if tool is installed"""
        result = self.core.run_command(f"which {tool}")
        return result and result.returncode == 0

    def install_mdk4(self):
        """Install MDK4 from source with better error handling"""
        try:
            print("\033[1;33m[→] DOWNLOADING MDK4 SOURCE...\033[0m")
            clone_result = self.core.run_command("git clone https://github.com/aircrack-ng/mdk4 > /dev/null 2>&1")
            
            if clone_result and clone_result.returncode == 0:
                os.chdir("mdk4")
                
                print("\033[1;33m[→] COMPILING MDK4...\033[0m")
                make_result = self.core.run_command("make > /dev/null 2>&1")
                
                if make_result and make_result.returncode == 0:
                    print("\033[1;33m[→] INSTALLING MDK4...\033[0m")
                    install_result = self.core.run_command("make install > /dev/null 2>&1")
                    
                    os.chdir("..")
                    self.core.run_command("rm -rf mdk4 > /dev/null 2>&1")
                    
                    if install_result and install_result.returncode == 0:
                        return True
            
            # Fallback: try package installation
            print("\033[1;33m[→] TRYING PACKAGE INSTALLATION...\033[0m")
            result = self.core.run_command("apt install -y mdk4 > /dev/null 2>&1")
            return result and result.returncode == 0
            
        except Exception as e:
            print(f"\033[1;31m[✘] MDK4 INSTALLATION FAILED: {e}\033[0m")
            return False

    def download_wordlists(self):
        """Download comprehensive wordlists for cracking"""
        print("\033[1;33m[!] DEPLOYING ENHANCED WORDLISTS...\033[0m")
        
        wordlist_dir = "/usr/share/wordlists"
        temp_dir = "/tmp/netstrike_wordlists"
        
        # Create directories
        os.makedirs(wordlist_dir, exist_ok=True)
        os.makedirs(temp_dir, exist_ok=True)
        
        # Comprehensive wordlist sources
        wordlists = {
            "rockyou.txt": "https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt",
            "common_passwords.txt": "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Common-Credentials/10-million-password-list-top-100000.txt",
            "top_million.txt": "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Common-Credentials/10-million-password-list-top-1000000.txt",
            "wpa_wordlist.txt": "https://raw.githubusercontent.com/kennyn510/wpa2-wordlists/master/wordlists/rockyou.txt"
        }
        
        downloaded_count = 0
        
        for filename, url in wordlists.items():
            filepath = os.path.join(wordlist_dir, filename)
            temp_path = os.path.join(temp_dir, filename)
            
            if not os.path.exists(filepath) or os.path.getsize(filepath) < 1000:
                print(f"\033[1;33m[→] DOWNLOADING {filename}...\033[0m")
                
                # Try wget first
                result = self.core.run_command(f"wget -q --show-progress -O {temp_path} '{url}' 2>&1")
                
                if not result or result.returncode != 0:
                    # Try curl as fallback
                    result = self.core.run_command(f"curl -L -o {temp_path} '{url}' 2>&1")
                
                if os.path.exists(temp_path) and os.path.getsize(temp_path) > 1000:
                    self.core.run_command(f"mv {temp_path} {filepath} 2>/dev/null")
                    downloaded_count += 1
                    print(f"\033[1;32m[✓] {filename} DEPLOYED\033[0m")
                else:
                    print(f"\033[1;31m[✘] {filename} DOWNLOAD FAILED\033[0m")
            else:
                print(f"\033[1;32m[✓] {filename} ALREADY DEPLOYED\033[0m")
                downloaded_count += 1
        
        # Cleanup
        self.core.run_command(f"rm -rf {temp_dir} 2>/dev/null")
        
        # Install wordlists package if available
        if downloaded_count < 2:
            print("\033[1;33m[→] INSTALLING WORDLISTS PACKAGE...\033[0m")
            self.core.run_command("apt install -y wordlists 2>/dev/null")
        
        print(f"\033[1;32m[✓] {downloaded_count} WORDLISTS READY FOR DEPLOYMENT\033[0m")

    def verify_installation(self):
        """Verify all critical tools are installed"""
        print("\033[1;33m[!] VERIFYING NETSTRIKE DEPLOYMENT...\033[0m")
        
        critical_tools = [
            "aircrack-ng", "macchanger", "iwconfig", "mdk4", 
            "hcxdumptool", "hashcat", "hcitool"
        ]
        
        missing_tools = []
        
        for tool in critical_tools:
            if self.check_tool_installed(tool):
                print(f"\033[1;32m[✓] {tool.upper()} VERIFIED\033[0m")
            else:
                print(f"\033[1;31m[✘] {tool.upper()} MISSING\033[0m")
                missing_tools.append(tool)
        
        if missing_tools:
            print(f"\033[1;31m[✘] MISSING TOOLS: {', '.join(missing_tools)}\033[0m")
            return False
        else:
            print("\033[1;32m[✓] ALL CRITICAL TOOLS VERIFIED\033[0m")
            return True
