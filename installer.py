#!/usr/bin/env python3

import os
import subprocess
import time
import sys
import threading
import fcntl

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

    def is_dpkg_locked(self):
        """Check if dpkg is currently locked"""
        lock_files = [
            "/var/lib/dpkg/lock-frontend",
            "/var/lib/dpkg/lock",
            "/var/lib/apt/lists/lock"
        ]
        
        for lock_file in lock_files:
            if os.path.exists(lock_file):
                try:
                    # Try to acquire lock to check if it's locked
                    with open(lock_file, 'w') as f:
                        fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                        # If we get here, we acquired the lock (not locked)
                        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                except (IOError, BlockingIOError):
                    # Couldn't acquire lock, so it's locked
                    return True
        return False

    def wait_for_dpkg_lock(self, timeout=300):
        """Wait for dpkg lock to be released"""
        print("\033[1;33m[!] CHECKING FOR SYSTEM LOCKS...\033[0m")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            if not self.is_dpkg_locked():
                print("\033[1;32m[✓] SYSTEM READY FOR INSTALLATION\033[0m")
                return True
            
            # Show waiting animation
            elapsed = int(time.time() - start_time)
            dots = "." * (elapsed % 4)
            print(f"\r\033[1;33m[⌛] WAITING FOR SYSTEM LOCKS TO RELEASE{dots} ({elapsed}s)\033[0m", end='', flush=True)
            time.sleep(2)
        
        print(f"\r\033[1;31m[✘] TIMEOUT WAITING FOR SYSTEM LOCKS AFTER {timeout}s\033[0m")
        return False

    def install_required_tools(self):
        """Install all required tools with lock detection"""
        print("\033[1;33m[!] DEPLOYING NETSTRIKE TOOLKIT...\033[0m")
        print(f"\033[1;36m[⚡] DETECTED SYSTEM: {self.distribution.upper()}\033[0m")
        
        # Wait for system locks first
        if not self.wait_for_dpkg_lock():
            print("\033[1;31m[✘] CANNOT PROCEED - SYSTEM LOCKS HELD\033[0m")
            print("\033[1;33m[💡] TIP: Wait for other package operations to complete\033[0m")
            return False
        
        # Update system
        if not self.update_system():
            return False
        
        # Install tools based on distribution
        if self.distribution == "kali":
            return self.install_kali_tools()
        else:
            return self.install_generic_tools()

    def update_system(self):
        """Update system repositories with lock detection"""
        print("\033[1;33m[!] UPDATING SYSTEM REPOSITORIES...\033[0m")
        
        if self.distribution == "kali":
            cmd = "apt update"
        else:
            cmd = "apt-get update"
            
        success = self.run_command_with_progress(cmd, "Updating repositories", timeout=120)
        if success:
            print("\033[1;32m[✓] SYSTEM UPDATED\033[0m")
            return True
        else:
            print("\033[1;31m[✘] UPDATE FAILED\033[0m")
            return False

    def run_command_with_progress(self, command, description, timeout=120):
        """Run command with progress animation and lock detection"""
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
            # Check for locks before running command
            if self.is_dpkg_locked():
                stop_animation.set()
                animation_thread.join(timeout=1)
                print(f"\r\033[1;31m[✘] {description} - SYSTEM LOCKED\033[0m")
                return False
            
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
                # Check if it failed due to locks
                if "Could not get lock" in result.stderr or "locked" in result.stderr.lower():
                    print(f"\r\033[1;31m[✘] {description} - SYSTEM LOCKED\033[0m")
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
        """Install tools optimized for Kali Linux with minimal package operations"""
        print("\033[1;33m[!] KALI LINUX DETECTED - MINIMAL INSTALLATION...\033[0m")
        
        # On Kali, most tools are pre-installed. Only install absolutely necessary ones.
        # Skip problematic packages that cause locks
        essential_tools = ["mdk4"]  # Only install MDK4 if missing
        
        tools_installed = True
        
        for tool in essential_tools:
            if not self.check_tool_installed(tool):
                print(f"\033[1;33m[!] INSTALLING ESSENTIAL TOOL: {tool}\033[0m")
                if not self.install_package_kali(tool):
                    tools_installed = False
            else:
                print(f"\033[1;32m[✓] {tool.upper()} ALREADY INSTALLED\033[0m")
        
        # Install Python packages using pip (avoid apt locks)
        print("\033[1;33m[!] INSTALLING PYTHON PACKAGES...\033[0m")
        python_packages = ["requests", "scapy"]
        for package in python_packages:
            if not self.is_python_package_installed(package):
                self.install_python_package_pip(package)
            else:
                print(f"\033[1;32m[✓] {package.upper()} ALREADY INSTALLED\033[0m")
        
        # Download wordlists
        print("\033[1;33m[!] SETTING UP WORDLISTS...\033[0m")
        self.setup_wordlists()
        
        return self.verify_installation()

    def install_package_kali(self, package):
        """Install package on Kali Linux with lock detection"""
        if self.check_tool_installed(package):
            return True
            
        # Use apt with progress and lock detection
        cmd = f"apt install -y {package}"
        return self.run_command_with_progress(cmd, f"Installing {package}", timeout=180)

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
        cmd = f"pip3 install {package} --break-system-packages --quiet"
        if self.run_command_with_progress(cmd, f"Installing {package}", timeout=60):
            print(f"\033[1;32m[✓] {package.upper()} INSTALLED\033[0m")
            return True
        else:
            print(f"\033[1;31m[✘] {package.upper()} INSTALLATION FAILED\033[0m")
            return False

    def setup_wordlists(self):
        """Setup wordlists without downloading if possible"""
        print("\033[1;33m[!] CHECKING WORDLISTS...\033[0m")
        
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
        elif os.path.exists("/usr/share/wordlists/rockyou.txt"):
            print("\033[1;32m[✓] ROCKYOU.TXT AVAILABLE\033[0m")
        else:
            # Create basic wordlist instead of downloading
            self.create_basic_wordlist()

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

    def check_tool_installed(self, tool):
        """Check if tool is installed"""
        result = self.core.run_command(f"command -v {tool}")
        return result and result.returncode == 0

    def verify_installation(self):
        """Verify critical tools are installed"""
        print("\033[1;33m[!] VERIFYING INSTALLATION...\033[0m")
        
        # Only check essential tools that are absolutely required
        essential_tools = ["aircrack-ng", "macchanger", "iwconfig"]
        
        missing_tools = []
        
        for tool in essential_tools:
            if self.check_tool_installed(tool):
                print(f"\033[1;32m[✓] {tool.upper()} VERIFIED\033[0m")
            else:
                print(f"\033[1;31m[✘] {tool.upper()} MISSING\033[0m")
                missing_tools.append(tool)
        
        if not missing_tools:
            print("\033[1;32m[✓] ALL ESSENTIAL TOOLS VERIFIED\033[0m")
            print("\033[1;32m[✓] NETSTRIKE READY FOR DEPLOYMENT\033[0m")
            return True
        else:
            print(f"\033[1;31m[✘] MISSING ESSENTIAL TOOLS: {', '.join(missing_tools)}\033[0m")
            print("\033[1;33m[⚠️] SOME FEATURES MAY NOT WORK\033[0m")
            return False
