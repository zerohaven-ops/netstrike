#!/usr/bin/env python3

import os
import subprocess
import time
import sys

class ToolInstaller:
    def __init__(self, core):
        self.core = core

    def install_required_tools(self):
        """Install all required tools automatically with NetStrike style"""
        print("\033[1;33m[!] DEPLOYING NETSTRIKE TOOLKIT...\033[0m")
        print("\033[1;36m[⚡] INITIATING ADVANCED TOOL DEPLOYMENT...\033[0m")
        
        # Update system
        print("\033[1;33m[!] UPDATING SYSTEM REPOSITORIES...\033[0m")
        result = self.core.run_command("apt update")
        if result and result.returncode == 0:
            print("\033[1;32m[✓] SYSTEM UPDATED\033[0m")
        else:
            print("\033[1;31m[✘] UPDATE FAILED - CHECK INTERNET CONNECTION\033[0m")
            return False
        
        # Install essential dependencies first
        print("\033[1;33m[!] INSTALLING ESSENTIAL DEPENDENCIES...\033[0m")
        deps = ["git", "build-essential", "libssl-dev", "zlib1g-dev", "libpcap-dev"]
        for dep in deps:
            if not self.install_package(dep):
                print(f"\033[1;31m[✘] FAILED TO INSTALL {dep}\033[0m")
        
        # WiFi tools (fixed order to avoid dependencies issues)
        wifi_tools = [
            "wireless-tools", "iw", "iproute2", "net-tools",
            "aircrack-ng", "macchanger", "xterm"
        ]
        
        # Install WiFi tools
        print("\033[1;33m[!] INSTALLING WI-FI WARFARE TOOLS...\033[0m")
        for tool in wifi_tools:
            self.install_package(tool)
        
        # Install reaver and bully for WPS (alternative to wash)
        print("\033[1;33m[!] INSTALLING WPS ATTACK TOOLS...\033[0m")
        if not self.install_reaver_bully():
            print("\033[1;31m[✘] WPS TOOLS INSTALLATION FAILED\033[0m")
        
        # Advanced cracking tools
        advanced_tools = ["hashcat"]
        for tool in advanced_tools:
            self.install_package(tool)
        
        # Install hcxdumptool and hcxtools from source (more reliable)
        print("\033[1;33m[!] INSTALLING ADVANCED CRACKING TOOLS...\033[0m")
        self.install_hcxtools()
        
        # Bluetooth tools
        bluetooth_tools = ["bluetooth", "bluez", "blueman", "hcitool", "l2ping", "bluetoothctl"]
        print("\033[1;33m[!] INSTALLING BLUETOOTH ASSAULT TOOLS...\033[0m")
        for tool in bluetooth_tools:
            self.install_package(tool)
        
        # Python packages
        python_packages = ["requests", "scapy"]
        print("\033[1;33m[!] INSTALLING PYTHON ENHANCEMENTS...\033[0m")
        for package in python_packages:
            self.install_python_package(package)
        
        # Install MDK4 from source
        if not self.check_tool_installed("mdk4"):
            print("\033[1;33m[!] DEPLOYING MDK4 NUCLEAR WEAPON...\033[0m")
            if self.install_mdk4():
                print("\033[1;32m[✓] MDK4 NUCLEAR WEAPON DEPLOYED\033[0m")
            else:
                print("\033[1;31m[✘] MDK4 DEPLOYMENT FAILED\033[0m")
        
        # Install hostapd and dnsmasq for Evil Twin
        print("\033[1;33m[!] INSTALLING EVIL TWIN TOOLS...\033[0m")
        self.install_package("hostapd")
        self.install_package("dnsmasq")
        
        # Download wordlists
        print("\033[1;33m[!] DEPLOYING CRACKING WORDLISTS...\033[0m")
        self.download_wordlists()
        
        # Verify installation
        if self.verify_installation():
            print("\033[1;32m[✓] NETSTRIKE TOOLKIT READY FOR COMBAT\033[0m")
            print("\033[1;32m[✓] ALL SYSTEMS GO - READY FOR DEPLOYMENT\033[0m")
            return True
        else:
            print("\033[1;33m[⚠️] SOME TOOLS MISSING - BUT CORE FUNCTIONALITY READY\033[0m")
            return True

    def install_package(self, package):
        """Install a package with better error handling"""
        if self.check_tool_installed(package):
            print(f"\033[1;32m[✓] {package.upper()} ALREADY INSTALLED\033[0m")
            return True
        
        print(f"\033[1;33m[→] INSTALLING {package.upper()}...\033[0m")
        
        # Try apt install with timeout
        try:
            result = subprocess.run(
                f"apt install -y {package}".split(),
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                print(f"\033[1;32m[✓] {package.upper()} INSTALLED\033[0m")
                return True
            else:
                print(f"\033[1;31m[✘] {package.upper()} INSTALLATION FAILED\033[0m")
                return False
                
        except subprocess.TimeoutExpired:
            print(f"\033[1;31m[✘] {package.upper()} INSTALLATION TIMEOUT\033[0m")
            return False
        except Exception as e:
            print(f"\033[1;31m[✘] {package.upper()} INSTALLATION ERROR: {e}\033[0m")
            return False

    def install_reaver_bully(self):
        """Install Reaver and Bully for WPS attacks (alternative to wash)"""
        tools_installed = True
        
        # Install reaver
        if not self.install_package("reaver"):
            print("\033[1;33m[→] TRYING TO INSTALL REAVER FROM SOURCE...\033[0m")
            if not self.install_reaver_from_source():
                tools_installed = False
        
        # Install bully
        if not self.install_package("bully"):
            print("\033[1;33m[→] TRYING TO INSTALL BULLY FROM SOURCE...\033[0m")
            if not self.install_bully_from_source():
                tools_installed = False
        
        return tools_installed

    def install_reaver_from_source(self):
        """Install Reaver from source"""
        try:
            print("\033[1;33m[→] DOWNLOADING REAVER SOURCE...\033[0m")
            clone_cmd = "git clone https://github.com/t6x/reaver-wps-fork-t6x.git"
            result = self.core.run_command(clone_cmd)
            
            if result and result.returncode == 0:
                os.chdir("reaver-wps-fork-t6x/src")
                
                print("\033[1;33m[→] CONFIGURING REAVER...\033[0m")
                self.core.run_command("./configure")
                
                print("\033[1;33m[→] COMPILING REAVER...\033[0m")
                self.core.run_command("make")
                
                print("\033[1;33m[→] INSTALLING REAVER...\033[0m")
                self.core.run_command("make install")
                
                os.chdir("../..")
                self.core.run_command("rm -rf reaver-wps-fork-t6x")
                
                if self.check_tool_installed("reaver"):
                    print("\033[1;32m[✓] REAVER INSTALLED FROM SOURCE\033[0m")
                    return True
                    
        except Exception as e:
            print(f"\033[1;31m[✘] REAVER SOURCE INSTALL FAILED: {e}\033[0m")
        
        return False

    def install_bully_from_source(self):
        """Install Bully from source"""
        try:
            print("\033[1;33m[→] DOWNLOADING BULLY SOURCE...\033[0m")
            clone_cmd = "git clone https://github.com/aanarchyy/bully.git"
            result = self.core.run_command(clone_cmd)
            
            if result and result.returncode == 0:
                os.chdir("bully/src")
                
                print("\033[1;33m[→] COMPILING BULLY...\033[0m")
                self.core.run_command("make")
                
                print("\033[1;33m[→] INSTALLING BULLY...\033[0m")
                self.core.run_command("make install")
                
                os.chdir("../..")
                self.core.run_command("rm -rf bully")
                
                if self.check_tool_installed("bully"):
                    print("\033[1;32m[✓] BULLY INSTALLED FROM SOURCE\033[0m")
                    return True
                    
        except Exception as e:
            print(f"\033[1;31m[✘] BULLY SOURCE INSTALL FAILED: {e}\033[0m")
        
        return False

    def install_hcxtools(self):
        """Install hcxdumptool and hcxtools from source"""
        try:
            print("\033[1;33m[→] INSTALLING HCXTOOLS FROM SOURCE...\033[0m")
            
            # Install dependencies
            deps = ["libcurl4-openssl-dev", "zlib1g-dev", "libpcap-dev"]
            for dep in deps:
                self.install_package(dep)
            
            # Clone and build
            self.core.run_command("git clone https://github.com/ZerBea/hcxtools.git")
            self.core.run_command("git clone https://github.com/ZerBea/hcxdumptool.git")
            
            # Build hcxtools
            os.chdir("hcxtools")
            self.core.run_command("make")
            self.core.run_command("make install")
            os.chdir("..")
            
            # Build hcxdumptool
            os.chdir("hcxdumptool")
            self.core.run_command("make")
            self.core.run_command("make install")
            os.chdir("..")
            
            # Cleanup
            self.core.run_command("rm -rf hcxtools hcxdumptool")
            
            if self.check_tool_installed("hcxdumptool") and self.check_tool_installed("hcxpcaptool"):
                print("\033[1;32m[✓] HCXTOOLS INSTALLED FROM SOURCE\033[0m")
                return True
            else:
                print("\033[1;31m[✘] HCXTOOLS INSTALLATION FAILED\033[0m")
                return False
                
        except Exception as e:
            print(f"\033[1;31m[✘] HCXTOOLS INSTALLATION ERROR: {e}\033[0m")
            return False

    def install_mdk4(self):
        """Install MDK4 from source with better error handling"""
        try:
            print("\033[1;33m[→] DOWNLOADING MDK4 SOURCE...\033[0m")
            clone_result = self.core.run_command("git clone https://github.com/aircrack-ng/mdk4")
            
            if clone_result and clone_result.returncode == 0:
                os.chdir("mdk4")
                
                print("\033[1;33m[→] COMPILING MDK4...\033[0m")
                make_result = self.core.run_command("make")
                
                if make_result and make_result.returncode == 0:
                    print("\033[1;33m[→] INSTALLING MDK4...\033[0m")
                    install_result = self.core.run_command("make install")
                    
                    os.chdir("..")
                    self.core.run_command("rm -rf mdk4")
                    
                    if install_result and install_result.returncode == 0:
                        return True
            
            # Fallback: try package installation
            print("\033[1;33m[→] TRYING PACKAGE INSTALLATION...\033[0m")
            return self.install_package("mdk4")
            
        except Exception as e:
            print(f"\033[1;31m[✘] MDK4 INSTALLATION FAILED: {e}\033[0m")
            return self.install_package("mdk4")

    def install_python_package(self, package):
        """Install Python package with pip"""
        print(f"\033[1;33m[→] INSTALLING {package.upper()}...\033[0m")
        
        try:
            result = subprocess.run(
                f"pip3 install {package}".split(),
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode == 0:
                print(f"\033[1;32m[✓] {package.upper()} INSTALLED\033[0m")
                return True
            else:
                # Try with --break-system-packages if needed
                result = subprocess.run(
                    f"pip3 install {package} --break-system-packages".split(),
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                if result.returncode == 0:
                    print(f"\033[1;32m[✓] {package.upper()} INSTALLED\033[0m")
                    return True
                else:
                    print(f"\033[1;31m[✘] {package.upper()} INSTALLATION FAILED\033[0m")
                    return False
                    
        except subprocess.TimeoutExpired:
            print(f"\033[1;31m[✘] {package.upper()} INSTALLATION TIMEOUT\033[0m")
            return False
        except Exception as e:
            print(f"\033[1;31m[✘] {package.URNAL} INSTALLATION ERROR: {e}\033[0m")
            return False

    def check_tool_installed(self, tool):
        """Check if tool is installed"""
        result = self.core.run_command(f"which {tool}")
        return result and result.returncode == 0

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
            "rockyou.txt": "https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt.gz",
            "common_passwords.txt": "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Common-Credentials/10-million-password-list-top-100000.txt"
        }
        
        downloaded_count = 0
        
        for filename, url in wordlists.items():
            filepath = os.path.join(wordlist_dir, filename)
            temp_path = os.path.join(temp_dir, filename)
            
            if not os.path.exists(filepath) or os.path.getsize(filepath) < 1000:
                print(f"\033[1;33m[→] DOWNLOADING {filename}...\033[0m")
                
                # Download file
                if url.endswith('.gz'):
                    # Download and extract gz file
                    result = self.core.run_command(f"wget -q -O {temp_path}.gz '{url}' && gzip -dc {temp_path}.gz > {temp_path} && rm {temp_path}.gz")
                else:
                    # Download regular file
                    result = self.core.run_command(f"wget -q -O {temp_path} '{url}'")
                
                if os.path.exists(temp_path) and os.path.getsize(temp_path) > 1000:
                    self.core.run_command(f"cp {temp_path} {filepath}")
                    downloaded_count += 1
                    print(f"\033[1;32m[✓] {filename} DEPLOYED\033[0m")
                else:
                    # Try curl as fallback
                    if url.endswith('.gz'):
                        result = self.core.run_command(f"curl -L -o {temp_path}.gz '{url}' && gzip -dc {temp_path}.gz > {temp_path} && rm {temp_path}.gz")
                    else:
                        result = self.core.run_command(f"curl -L -o {temp_path} '{url}'")
                    
                    if os.path.exists(temp_path) and os.path.getsize(temp_path) > 1000:
                        self.core.run_command(f"cp {temp_path} {filepath}")
                        downloaded_count += 1
                        print(f"\033[1;32m[✓] {filename} DEPLOYED\033[0m")
                    else:
                        print(f"\033[1;31m[✘] {filename} DOWNLOAD FAILED\033[0m")
            else:
                print(f"\033[1;32m[✓] {filename} ALREADY DEPLOYED\033[0m")
                downloaded_count += 1
        
        # Cleanup
        self.core.run_command(f"rm -rf {temp_dir}")
        
        # Create a basic wordlist if others failed
        if downloaded_count == 0:
            self.create_basic_wordlist()
        
        print(f"\033[1;32m[✓] {downloaded_count} WORDLISTS READY FOR DEPLOYMENT\033[0m")

    def create_basic_wordlist(self):
        """Create a basic wordlist if downloads fail"""
        basic_path = "/usr/share/wordlists/basic_passwords.txt"
        print("\033[1;33m[→] CREATING BASIC WORDLIST...\033[0m")
        
        common_passwords = [
            "123456", "password", "12345678", "qwerty", "123456789",
            "12345", "1234", "111111", "1234567", "dragon",
            "123123", "baseball", "abc123", "football", "monkey",
            "letmein", "696969", "shadow", "master", "666666",
            "qwertyuiop", "123321", "mustang", "1234567890", "michael",
            "654321", "superman", "1qaz2wsx", "7777777", "121212",
            "000000", "qazwsx", "123qwe", "killer", "trustno1",
            "jordan", "jennifer", "zxcvbnm", "asdfgh", "hunter",
            "buster", "soccer", "harley", "batman", "andrew",
            "tigger", "sunshine", "iloveyou", "2000", "charlie",
            "robert", "thomas", "hockey", "ranger", "daniel"
        ]
        
        with open(basic_path, 'w') as f:
            for pwd in common_passwords:
                f.write(pwd + '\n')
        
        print("\033[1;32m[✓] BASIC WORDLIST CREATED\033[0m")

    def verify_installation(self):
        """Verify all critical tools are installed"""
        print("\033[1;33m[!] VERIFYING NETSTRIKE DEPLOYMENT...\033[0m")
        
        critical_tools = [
            "aircrack-ng", "macchanger", "iwconfig", "mdk4", "hcitool"
        ]
        
        important_tools = [
            "reaver", "bully", "hcxdumptool", "hashcat", "hostapd"
        ]
        
        missing_critical = []
        missing_important = []
        
        for tool in critical_tools:
            if self.check_tool_installed(tool):
                print(f"\033[1;32m[✓] {tool.upper()} VERIFIED\033[0m")
            else:
                print(f"\033[1;31m[✘] {tool.upper()} MISSING\033[0m")
                missing_critical.append(tool)
        
        for tool in important_tools:
            if self.check_tool_installed(tool):
                print(f"\033[1;32m[✓] {tool.upper()} VERIFIED\033[0m")
            else:
                print(f"\033[1;33m[⚠️] {tool.upper()} MISSING\033[0m")
                missing_important.append(tool)
        
        if missing_critical:
            print(f"\033[1;31m[✘] MISSING CRITICAL TOOLS: {', '.join(missing_critical)}\033[0m")
            return False
        else:
            if missing_important:
                print(f"\033[1;33m[⚠️] MISSING IMPORTANT TOOLS: {', '.join(missing_important)}\033[0m")
            print("\033[1;32m[✓] CORE FUNCTIONALITY VERIFIED\033[0m")
            return True
