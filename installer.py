#!/usr/bin/env python3

import os
import subprocess
import time
import sys
import threading
import queue

class ToolInstaller:
    def __init__(self, core):
        self.core = core
        self.distribution = self.detect_distribution()
        
    def detect_distribution(self):
        """Detect the Linux distribution"""
        try:
            if os.path.exists("/etc/os-release"):
                with open("/etc/os-release", "r") as f:
                    content = f.read().lower()
                    if "kali" in content:
                        return "kali"
                    elif "debian" in content:
                        return "debian"
                    elif "ubuntu" in content:
                        return "ubuntu"
            return "unknown"
        except:
            return "unknown"

    def install_required_tools(self):
        """Install all required tools with progress tracking"""
        print("\033[1;33m[!] DEPLOYING NETSTRIKE TOOLKIT...\033[0m")
        print(f"\033[1;36m[⚡] DETECTED SYSTEM: {self.distribution.upper()}\033[0m")
        
        # Update system
        if not self.update_system():
            return False
        
        # Install tools based on distribution
        if self.distribution == "kali":
            return self.install_kali_tools()
        else:
            return self.install_generic_tools()

    def update_system(self):
        """Update system repositories with progress"""
        print("\033[1;33m[!] UPDATING SYSTEM REPOSITORIES...\033[0m")
        
        if self.distribution == "kali":
            cmd = "apt update"
        else:
            cmd = "apt-get update"
            
        success = self.run_command_with_progress(cmd, "Updating repositories")
        if success:
            print("\033[1;32m[✓] SYSTEM UPDATED\033[0m")
            return True
        else:
            print("\033[1;31m[✘] UPDATE FAILED\033[0m")
            return False

    def run_command_with_progress(self, command, description, timeout=180):
        """Run command with progress animation and timeout"""
        print(f"\033[1;33m[→] {description}...\033[0m", end='', flush=True)
        
        def animate():
            frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
            i = 0
            while not stop_animation.is_set():
                print(f"\r\033[1;33m[→] {description}... {frames[i % len(frames)]}\033[0m", end='', flush=True)
                i += 1
                time.sleep(0.2)
        
        stop_animation = threading.Event()
        animation_thread = threading.Thread(target=animate)
        animation_thread.daemon = True
        animation_thread.start()
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            stop_animation.set()
            animation_thread.join(timeout=1)
            
            if result.returncode == 0:
                print(f"\r\033[1;32m[✓] {description} COMPLETED\033[0m")
                return True
            else:
                print(f"\r\033[1;31m[✘] {description} FAILED\033[0m")
                return False
                
        except subprocess.TimeoutExpired:
            stop_animation.set()
            animation_thread.join(timeout=1)
            print(f"\r\033[1;31m[✘] {description} TIMEOUT\033[0m")
            return False
        except Exception as e:
            stop_animation.set()
            animation_thread.join(timeout=1)
            print(f"\r\033[1;31m[✘] {description} ERROR: {e}\033[0m")
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
            "bluez", "hcitool", "hostapd", "dnsmasq"
        ]
        
        for tool in pre_installed_tools:
            if not self.check_tool_installed(tool):
                tools_to_install.append(tool)
            else:
                print(f"\033[1;32m[✓] {tool.upper()} ALREADY INSTALLED\033[0m")
        
        # Install missing tools with progress
        if tools_to_install:
            print(f"\033[1;33m[!] INSTALLING {len(tools_to_install)} MISSING TOOLS...\033[0m")
            for tool in tools_to_install:
                self.install_package_kali(tool)
        
        # Install MDK4 (not usually pre-installed)
        if not self.check_tool_installed("mdk4"):
            print("\033[1;33m[!] INSTALLING MDK4...\033[0m")
            if not self.install_package_kali("mdk4"):
                self.install_mdk4_from_source()
        
        # Install Python packages using apt (Kali's preferred method)
        print("\033[1;33m[!] INSTALLING PYTHON PACKAGES...\033[0m")
        self.install_python_packages_kali()
        
        # Download wordlists
        print("\033[1;33m[!] DOWNLOADING WORDLISTS...\033[0m")
        self.download_wordlists()
        
        return self.verify_installation()

    def install_package_kali(self, package):
        """Install package on Kali Linux with progress"""
        if self.check_tool_installed(package):
            return True
            
        # Use apt with progress
        cmd = f"apt install -y {package}"
        return self.run_command_with_progress(cmd, f"Installing {package}")

    def install_python_packages_kali(self):
        """Install Python packages on Kali using apt"""
        python_packages_apt = {
            "requests": "python3-requests",
            "scapy": "python3-scapy"
        }
        
        for pypi_name, apt_name in python_packages_apt.items():
            if not self.is_python_package_installed(pypi_name):
                print(f"\033[1;33m[→] Installing {pypi_name} via apt...\033[0m")
                if self.install_package_kali(apt_name):
                    print(f"\033[1;32m[✓] {pypi_name.upper()} INSTALLED\033[0m")
                else:
                    # Fallback to pip with break-system-packages
                    self.install_python_package_pip(pypi_name)
            else:
                print(f"\033[1;32m[✓] {pypi_name.upper()} ALREADY INSTALLED\033[0m")

    def is_python_package_installed(self, package):
        """Check if Python package is installed"""
        try:
            result = subprocess.run(
                f"python3 -c \"import {package}\"".split(),
                capture_output=True,
                text=True,
                timeout=10
            )
            return result.returncode == 0
        except:
            return False

    def install_python_package_pip(self, package):
        """Install Python package using pip with break-system-packages"""
        print(f"\033[1;33m[→] Installing {package} via pip...\033[0m")
        
        # Try with break-system-packages (Kali 2024+ requirement)
        cmd = f"pip3 install {package} --break-system-packages"
        if self.run_command_with_progress(cmd, f"Installing {package}"):
            print(f"\033[1;32m[✓] {package.upper()} INSTALLED\033[0m")
            return True
        else:
            print(f"\033[1;31m[✘] {package.upper()} INSTALLATION FAILED\033[0m")
            return False

    def install_generic_tools(self):
        """Install tools for generic Debian/Ubuntu systems"""
        print("\033[1;33m[!] INSTALLING TOOLS FOR DEBIAN/UBUNTU...\033[0m")
        
        # Essential dependencies
        essential_deps = ["git", "build-essential", "libssl-dev", "zlib1g-dev", "libpcap-dev"]
        for dep in essential_deps:
            self.install_package_generic(dep)
        
        # Core WiFi tools
        wifi_tools = [
            "aircrack-ng", "macchanger", "wireless-tools", "iw", "iproute2",
            "net-tools", "xterm"
        ]
        for tool in wifi_tools:
            self.install_package_generic(tool)
        
        # WPS tools
        wps_tools = ["reaver", "bully"]
        for tool in wps_tools:
            if not self.install_package_generic(tool):
                if tool == "reaver":
                    self.install_reaver_from_source()
                elif tool == "bully":
                    self.install_bully_from_source()
        
        # Advanced tools
        advanced_tools = ["hashcat", "hostapd", "dnsmasq"]
        for tool in advanced_tools:
            self.install_package_generic(tool)
        
        # Install MDK4
        if not self.check_tool_installed("mdk4"):
            if not self.install_package_generic("mdk4"):
                self.install_mdk4_from_source()
        
        # Python packages
        python_packages = ["requests", "scapy"]
        for package in python_packages:
            self.install_python_package_pip(package)
        
        # Download wordlists
        self.download_wordlists()
        
        return self.verify_installation()

    def install_package_generic(self, package):
        """Install package on generic Debian/Ubuntu"""
        if self.check_tool_installed(package):
            return True
            
        cmd = f"apt-get install -y {package}"
        return self.run_command_with_progress(cmd, f"Installing {package}")

    def check_tool_installed(self, tool):
        """Check if tool is installed"""
        result = self.core.run_command(f"which {tool}")
        return result and result.returncode == 0

    def install_reaver_from_source(self):
        """Install Reaver from source"""
        print("\033[1;33m[→] INSTALLING REAVER FROM SOURCE...\033[0m")
        
        # Use verified working source
        source_url = "https://github.com/t6x/reaver-wps-fork-t6x.git"
        
        cmds = [
            f"git clone {source_url}",
            "cd reaver-wps-fork-t6x/src",
            "./configure",
            "make",
            "make install",
            "cd ../..",
            "rm -rf reaver-wps-fork-t6x"
        ]
        
        for cmd in cmds:
            if not self.run_command_with_progress(cmd, "Building reaver"):
                return False
        
        if self.check_tool_installed("reaver"):
            print("\033[1;32m[✓] REAVER INSTALLED FROM SOURCE\033[0m")
            return True
        return False

    def install_bully_from_source(self):
        """Install Bully from source"""
        print("\033[1;33m[→] INSTALLING BULLY FROM SOURCE...\033[0m")
        
        # Use verified working source
        source_url = "https://github.com/aanarchyy/bully.git"
        
        cmds = [
            f"git clone {source_url}",
            "cd bully/src",
            "make",
            "make install",
            "cd ../..",
            "rm -rf bully"
        ]
        
        for cmd in cmds:
            if not self.run_command_with_progress(cmd, "Building bully"):
                return False
        
        if self.check_tool_installed("bully"):
            print("\033[1;32m[✓] BULLY INSTALLED FROM SOURCE\033[0m")
            return True
        return False

    def install_mdk4_from_source(self):
        """Install MDK4 from source"""
        print("\033[1;33m[→] INSTALLING MDK4 FROM SOURCE...\033[0m")
        
        # Use verified working source
        source_url = "https://github.com/aircrack-ng/mdk4.git"
        
        cmds = [
            f"git clone {source_url}",
            "cd mdk4",
            "make",
            "make install",
            "cd ..",
            "rm -rf mdk4"
        ]
        
        for cmd in cmds:
            if not self.run_command_with_progress(cmd, "Building mdk4"):
                return False
        
        if self.check_tool_installed("mdk4"):
            print("\033[1;32m[✓] MDK4 INSTALLED FROM SOURCE\033[0m")
            return True
        return False

    def download_wordlists(self):
        """Download wordlists with progress and verified sources"""
        print("\033[1;33m[!] DOWNLOADING WORDLISTS...\033[0m")
        
        wordlist_dir = "/usr/share/wordlists"
        os.makedirs(wordlist_dir, exist_ok=True)
        
        # Check for existing wordlists in Kali
        if os.path.exists("/usr/share/wordlists/rockyou.txt.gz"):
            if not os.path.exists("/usr/share/wordlists/rockyou.txt"):
                self.run_command_with_progress(
                    "gzip -dc /usr/share/wordlists/rockyou.txt.gz > /usr/share/wordlists/rockyou.txt",
                    "Extracting rockyou.txt"
                )
            print("\033[1;32m[✓] ROCKYOU.TXT AVAILABLE\033[0m")
        elif not os.path.exists("/usr/share/wordlists/rockyou.txt"):
            # Download rockyou from verified source
            self.download_rockyou_wordlist()
        
        # Create basic wordlist as fallback
        basic_path = "/usr/share/wordlists/netstrike_passwords.txt"
        if not os.path.exists(basic_path):
            self.create_basic_wordlist()

    def download_rockyou_wordlist(self):
        """Download rockyou wordlist from verified source"""
        print("\033[1;33m[→] DOWNLOADING ROCKYOU WORDLIST...\033[0m")
        
        # Use multiple verified sources
        sources = [
            "wget -q https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt -O /usr/share/wordlists/rockyou.txt",
            "curl -s -L -o /usr/share/wordlists/rockyou.txt https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt"
        ]
        
        for source in sources:
            if self.run_command_with_progress(source, "Downloading rockyou.txt", timeout=300):
                if os.path.exists("/usr/share/wordlists/rockyou.txt") and os.path.getsize("/usr/share/wordlists/rockyou.txt") > 1000000:
                    print("\033[1;32m[✓] ROCKYOU.TXT DOWNLOADED\033[0m")
                    return True
        
        print("\033[1;31m[✘] ROCKYOU.TXT DOWNLOAD FAILED\033[0m")
        return False

    def create_basic_wordlist(self):
        """Create a basic wordlist"""
        basic_path = "/usr/share/wordlists/netstrike_passwords.txt"
        print("\033[1;33m[→] CREATING BASIC WORDLIST...\033[0m")
        
        passwords = [
            "123456", "password", "12345678", "qwerty", "123456789",
            "12345", "1234", "111111", "1234567", "dragon", "123123",
            "baseball", "abc123", "football", "monkey", "letmein",
            "696969", "shadow", "master", "666666", "qwertyuiop",
            "123321", "mustang", "1234567890", "michael", "654321"
        ]
        
        try:
            with open(basic_path, 'w') as f:
                for pwd in passwords:
                    f.write(pwd + '\n')
            print("\033[1;32m[✓] BASIC WORDLIST CREATED\033[0m")
            return True
        except Exception as e:
            print(f"\033[1;31m[✘] WORDLIST CREATION FAILED: {e}\033[0m")
            return False

    def verify_installation(self):
        """Verify critical tools are installed"""
        print("\033[1;33m[!] VERIFYING INSTALLATION...\033[0m")
        
        critical_tools = ["aircrack-ng", "macchanger", "iwconfig"]
        important_tools = ["mdk4", "reaver", "hcitool"]
        
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
