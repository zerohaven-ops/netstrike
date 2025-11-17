#!/usr/bin/env python3

import os
import subprocess
import time
import sys
import platform

class ToolInstaller:
    def __init__(self, core):
        self.core = core
        self.distribution = self.detect_distribution()
        
    def detect_distribution(self):
        """Detect the Linux distribution"""
        try:
            # Check for Kali Linux first
            if os.path.exists("/etc/os-release"):
                with open("/etc/os-release", "r") as f:
                    content = f.read().lower()
                    if "kali" in content:
                        return "kali"
                    elif "debian" in content:
                        return "debian"
                    elif "ubuntu" in content:
                        return "ubuntu"
            
            # Check for other distributions
            result = self.core.run_command("lsb_release -is 2>/dev/null")
            if result and result.returncode == 0:
                distro = result.stdout.strip().lower()
                if "kali" in distro:
                    return "kali"
                elif "debian" in distro:
                    return "debian"
                elif "ubuntu" in distro:
                    return "ubuntu"
                    
            return "unknown"
        except:
            return "unknown"

    def install_required_tools(self):
        """Install all required tools optimized for Kali Linux"""
        print("\033[1;33m[!] DEPLOYING NETSTRIKE TOOLKIT...\033[0m")
        print(f"\033[1;36m[⚡] DETECTED SYSTEM: {self.distribution.upper()}\033[0m")
        
        # Update system based on distribution
        if not self.update_system():
            print("\033[1;31m[✘] SYSTEM UPDATE FAILED - CHECK INTERNET CONNECTION\033[0m")
            return False
        
        # Install tools based on distribution
        if self.distribution == "kali":
            return self.install_kali_tools()
        else:
            return self.install_generic_tools()

    def update_system(self):
        """Update system repositories"""
        print("\033[1;33m[!] UPDATING SYSTEM REPOSITORIES...\033[0m")
        
        if self.distribution == "kali":
            # Kali Linux uses apt like Debian
            cmd = "apt update"
        else:
            cmd = "apt-get update"
            
        result = self.core.run_command(cmd)
        if result and result.returncode == 0:
            print("\033[1;32m[✓] SYSTEM UPDATED\033[0m")
            return True
        else:
            print("\033[1;31m[✘] UPDATE FAILED\033[0m")
            return False

    def install_kali_tools(self):
        """Install tools optimized for Kali Linux"""
        print("\033[1;33m[!] KALI LINUX DETECTED - OPTIMIZING INSTALLATION...\033[0m")
        
        # Kali Linux already has most tools - just install missing ones
        tools_to_install = []
        
        # Check what's already installed
        pre_installed_tools = [
            "aircrack-ng", "macchanger", "wireless-tools", "iw", "iproute2",
            "net-tools", "xterm", "reaver", "bully", "hashcat", "bluetooth",
            "bluez", "hcitool", "hostapd", "dnsmasq", "python3-pip"
        ]
        
        for tool in pre_installed_tools:
            if not self.check_tool_installed(tool):
                tools_to_install.append(tool)
            else:
                print(f"\033[1;32m[✓] {tool.upper()} ALREADY INSTALLED\033[0m")
        
        # Install missing tools
        if tools_to_install:
            print(f"\033[1;33m[!] INSTALLING MISSING TOOLS: {', '.join(tools_to_install)}\033[0m")
            for tool in tools_to_install:
                self.install_package(tool)
        
        # Install MDK4 (not usually pre-installed)
        if not self.check_tool_installed("mdk4"):
            print("\033[1;33m[!] INSTALLING MDK4...\033[0m")
            if not self.install_package("mdk4"):
                self.install_mdk4_from_source()
        
        # Install Python packages
        print("\033[1;33m[!] INSTALLING PYTHON PACKAGES...\033[0m")
        python_packages = ["requests", "scapy"]
        for package in python_packages:
            self.install_python_package(package)
        
        # Download wordlists
        print("\033[1;33m[!] DOWNLOADING WORDLISTS...\033[0m")
        self.download_wordlists()
        
        return self.verify_installation()

    def install_generic_tools(self):
        """Install tools for generic Debian/Ubuntu systems"""
        print("\033[1;33m[!] INSTALLING TOOLS FOR DEBIAN/UBUNTU...\033[0m")
        
        # Essential dependencies
        essential_deps = ["git", "build-essential", "libssl-dev", "zlib1g-dev", "libpcap-dev"]
        for dep in essential_deps:
            self.install_package(dep)
        
        # Core WiFi tools
        wifi_tools = [
            "aircrack-ng", "macchanger", "wireless-tools", "iw", "iproute2",
            "net-tools", "xterm"
        ]
        for tool in wifi_tools:
            self.install_package(tool)
        
        # WPS tools
        wps_tools = ["reaver", "bully"]
        for tool in wps_tools:
            if not self.install_package(tool):
                if tool == "reaver":
                    self.install_reaver_from_source()
                elif tool == "bully":
                    self.install_bully_from_source()
        
        # Advanced tools
        advanced_tools = ["hashcat", "hostapd", "dnsmasq"]
        for tool in advanced_tools:
            self.install_package(tool)
        
        # Bluetooth tools
        bt_tools = ["bluetooth", "bluez", "blueman", "hcitool", "l2ping", "bluetoothctl"]
        for tool in bt_tools:
            self.install_package(tool)
        
        # Install MDK4
        if not self.check_tool_installed("mdk4"):
            if not self.install_package("mdk4"):
                self.install_mdk4_from_source()
        
        # Python packages
        python_packages = ["requests", "scapy"]
        for package in python_packages:
            self.install_python_package(package)
        
        # Download wordlists
        self.download_wordlists()
        
        return self.verify_installation()

    def install_package(self, package):
        """Install a package with distribution-specific commands"""
        if self.check_tool_installed(package):
            print(f"\033[1;32m[✓] {package.upper()} ALREADY INSTALLED\033[0m")
            return True
        
        print(f"\033[1;33m[→] INSTALLING {package.upper()}...\033[0m")
        
        # Use apt for Kali/Debian/Ubuntu
        if self.distribution == "kali":
            cmd = f"apt install -y {package}"
        else:
            cmd = f"apt-get install -y {package}"
        
        try:
            result = subprocess.run(
                cmd.split(),
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout
            )
            
            if result.returncode == 0:
                print(f"\033[1;32m[✓] {package.upper()} INSTALLED\033[0m")
                return True
            else:
                # Try with --fix-missing
                cmd_fix = f"{cmd} --fix-missing"
                result = subprocess.run(
                    cmd_fix.split(),
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
            print(f"\033[1;31m[✘] {package.upper()} INSTALLATION ERROR: {e}\033[0m")
            return False

    def check_tool_installed(self, tool):
        """Check if tool is installed"""
        result = self.core.run_command(f"which {tool}")
        return result and result.returncode == 0

    def install_reaver_from_source(self):
        """Install Reaver from source as fallback"""
        try:
            print("\033[1;33m[→] INSTALLING REAVER FROM SOURCE...\033[0m")
            
            # Install dependencies first
            deps = ["libpcap-dev", "libsqlite3-dev"]
            for dep in deps:
                self.install_package(dep)
            
            # Clone and build
            self.core.run_command("git clone https://github.com/t6x/reaver-wps-fork-t6x.git")
            os.chdir("reaver-wps-fork-t6x/src")
            self.core.run_command("./configure")
            self.core.run_command("make")
            self.core.run_command("make install")
            os.chdir("../..")
            self.core.run_command("rm -rf reaver-wps-fork-t6x")
            
            if self.check_tool_installed("reaver"):
                print("\033[1;32m[✓] REAVER INSTALLED FROM SOURCE\033[0m")
                return True
            else:
                return False
                
        except Exception as e:
            print(f"\033[1;31m[✘] REAVER SOURCE INSTALL FAILED: {e}\033[0m")
            return False

    def install_bully_from_source(self):
        """Install Bully from source as fallback"""
        try:
            print("\033[1;33m[→] INSTALLING BULLY FROM SOURCE...\033[0m")
            
            # Install dependencies
            deps = ["libpcap-dev"]
            for dep in deps:
                self.install_package(dep)
            
            # Clone and build
            self.core.run_command("git clone https://github.com/aanarchyy/bully.git")
            os.chdir("bully/src")
            self.core.run_command("make")
            self.core.run_command("make install")
            os.chdir("../..")
            self.core.run_command("rm -rf bully")
            
            if self.check_tool_installed("bully"):
                print("\033[1;32m[✓] BULLY INSTALLED FROM SOURCE\033[0m")
                return True
            else:
                return False
                
        except Exception as e:
            print(f"\033[1;31m[✘] BULLY SOURCE INSTALL FAILED: {e}\033[0m")
            return False

    def install_mdk4_from_source(self):
        """Install MDK4 from source"""
        try:
            print("\033[1;33m[→] INSTALLING MDK4 FROM SOURCE...\033[0m")
            
            # Install dependencies
            deps = ["libpcap-dev", "libnl-3-dev", "libnl-genl-3-dev"]
            for dep in deps:
                self.install_package(dep)
            
            # Clone and build
            self.core.run_command("git clone https://github.com/aircrack-ng/mdk4")
            os.chdir("mdk4")
            self.core.run_command("make")
            self.core.run_command("make install")
            os.chdir("..")
            self.core.run_command("rm -rf mdk4")
            
            if self.check_tool_installed("mdk4"):
                print("\033[1;32m[✓] MDK4 INSTALLED FROM SOURCE\033[0m")
                return True
            else:
                return False
                
        except Exception as e:
            print(f"\033[1;31m[✘] MDK4 SOURCE INSTALL FAILED: {e}\033[0m")
            return False

    def install_python_package(self, package):
        """Install Python package"""
        print(f"\033[1;33m[→] INSTALLING PYTHON PACKAGE: {package}\033[0m")
        
        try:
            # Try pip3 first
            result = subprocess.run(
                f"pip3 install {package}".split(),
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                print(f"\033[1;32m[✓] {package.upper()} INSTALLED\033[0m")
                return True
            else:
                # Try with --user
                result = subprocess.run(
                    f"pip3 install {package} --user".split(),
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                if result.returncode == 0:
                    print(f"\033[1;32m[✓] {package.upper()} INSTALLED\033[0m")
                    return True
                else:
                    print(f"\033[1;31m[✘] {package.upper()} INSTALLATION FAILED\033[0m")
                    return False
                    
        except Exception as e:
            print(f"\033[1;31m[✘] {package.upper()} INSTALLATION ERROR: {e}\033[0m")
            return False

    def download_wordlists(self):
        """Download wordlists with multiple fallbacks"""
        print("\033[1;33m[!] DOWNLOADING WORDLISTS...\033[0m")
        
        wordlist_dir = "/usr/share/wordlists"
        os.makedirs(wordlist_dir, exist_ok=True)
        
        # Try to use Kali's built-in wordlists first
        kali_wordlists = [
            "/usr/share/wordlists/rockyou.txt",
            "/usr/share/wordlists/rockyou.txt.gz"
        ]
        
        for wordlist_path in kali_wordlists:
            if os.path.exists(wordlist_path):
                if wordlist_path.endswith('.gz'):
                    # Extract gz file
                    extract_path = wordlist_path.replace('.gz', '')
                    if not os.path.exists(extract_path):
                        self.core.run_command(f"gzip -dc {wordlist_path} > {extract_path}")
                        print("\033[1;32m[✓] ROCKYOU.TXT EXTRACTED\033[0m")
                else:
                    print("\033[1;32m[✓] ROCKYOU.TXT ALREADY AVAILABLE\033[0m")
                break
        else:
            # Download if not available
            self.download_rockyou_wordlist()
        
        # Create basic wordlist as fallback
        basic_path = "/usr/share/wordlists/basic_passwords.txt"
        if not os.path.exists(basic_path):
            self.create_basic_wordlist()

    def download_rockyou_wordlist(self):
        """Download rockyou wordlist"""
        print("\033[1;33m[→] DOWNLOADING ROCKYOU WORDLIST...\033[0m")
        
        rockyou_path = "/usr/share/wordlists/rockyou.txt"
        
        # Try multiple sources
        sources = [
            "wget -q https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt -O /tmp/rockyou.txt",
            "curl -s -L -o /tmp/rockyou.txt https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt"
        ]
        
        for source in sources:
            self.core.run_command(source)
            if os.path.exists("/tmp/rockyou.txt") and os.path.getsize("/tmp/rockyou.txt") > 1000000:
                self.core.run_command("mv /tmp/rockyou.txt /usr/share/wordlists/rockyou.txt")
                print("\033[1;32m[✓] ROCKYOU.TXT DOWNLOADED\033[0m")
                return True
        
        print("\033[1;31m[✘] ROCKYOU.TXT DOWNLOAD FAILED\033[0m")
        return False

    def create_basic_wordlist(self):
        """Create a basic wordlist"""
        basic_path = "/usr/share/wordlists/basic_passwords.txt"
        print("\033[1;33m[→] CREATING BASIC WORDLIST...\033[0m")
        
        passwords = [
            "123456", "password", "12345678", "qwerty", "123456789",
            "12345", "1234", "111111", "1234567", "dragon",
            "123123", "baseball", "abc123", "football", "monkey",
            "letmein", "696969", "shadow", "master", "666666",
            "qwertyuiop", "123321", "mustang", "1234567890", "michael"
        ]
        
        with open(basic_path, 'w') as f:
            for pwd in passwords:
                f.write(pwd + '\n')
        
        print("\033[1;32m[✓] BASIC WORDLIST CREATED\033[0m")

    def verify_installation(self):
        """Verify critical tools are installed"""
        print("\033[1;33m[!] VERIFYING INSTALLATION...\033[0m")
        
        critical_tools = ["aircrack-ng", "macchanger", "iwconfig"]
        important_tools = ["mdk4", "reaver", "bully", "hcitool"]
        
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
        
        if not missing_critical:
            print("\033[1;32m[✓] CORE FUNCTIONALITY VERIFIED\033[0m")
            if missing_important:
                print(f"\033[1;33m[⚠️] MISSING SOME TOOLS: {', '.join(missing_important)}\033[0m")
            return True
        else:
            print(f"\033[1;31m[✘] MISSING CRITICAL TOOLS: {', '.join(missing_critical)}\033[0m")
            return False
