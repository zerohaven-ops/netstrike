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
        self.essential_tools = [
            "aircrack-ng", "macchanger", "iwconfig", "mdk4", 
            "reaver", "hostapd", "dnsmasq", "hcxdumptool", "hashcat"
        ]
        
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

    def check_tools_availability(self):
        """Check which tools are already available"""
        print("\033[1;36m[→] Checking professional toolkit...\033[0m")
        
        available_tools = []
        missing_tools = []
        
        for tool in self.essential_tools:
            if self.core.run_command(f"command -v {tool}") and self.core.run_command(f"command -v {tool}").returncode == 0:
                available_tools.append(tool)
                print(f"\033[1;32m[✅] {tool} available\033[0m")
            else:
                missing_tools.append(tool)
                print(f"\033[1;33m[⚠️] {tool} missing\033[0m")
        
        return available_tools, missing_tools

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
                    with open(lock_file, 'w') as f:
                        fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                except (IOError, BlockingIOError):
                    return True
        return False

    def get_locking_process(self):
        """Get the process that's holding the dpkg lock"""
        try:
            result = subprocess.run(
                "lsof /var/lib/dpkg/lock-frontend 2>/dev/null | tail -1 | awk '{print $2}'",
                shell=True,
                capture_output=True,
                text=True
            )
            if result.returncode == 0 and result.stdout.strip():
                pid = result.stdout.strip()
                # Get process name
                cmd_result = subprocess.run(
                    f"ps -p {pid} -o comm= 2>/dev/null",
                    shell=True,
                    capture_output=True,
                    text=True
                )
                if cmd_result.returncode == 0:
                    return pid, cmd_result.stdout.strip()
            return None, None
        except:
            return None, None

    def smart_lock_cleanup(self):
        """Smart lock cleanup - only when absolutely necessary"""
        print("\033[1;33m[!] Attempting smart lock resolution...\033[0m")
        
        pid, process_name = self.get_locking_process()
        if pid and process_name:
            print(f"\033[1;33m[→] Found locking process: {process_name} (PID: {pid})\033[0m")
            
            # Ask user for permission to kill
            response = input("\033[1;33m[?] Kill this process to continue installation? (y/N): \033[0m")
            if response.lower() in ['y', 'yes']:
                print(f"\033[1;31m[💣] Killing process {pid} ({process_name})...\033[0m")
                self.core.run_command(f"kill -9 {pid}")
                time.sleep(2)
                
                # Remove lock files
                lock_files = [
                    "/var/lib/dpkg/lock-frontend",
                    "/var/lib/dpkg/lock", 
                    "/var/lib/apt/lists/lock"
                ]
                for lock_file in lock_files:
                    self.core.run_command(f"rm -f {lock_file}")
                
                # Fix any broken states
                self.core.run_command("dpkg --configure -a")
                self.core.run_command("apt-get install -f -y")
                
                print("\033[1;32m[✓] System locks cleared\033[0m")
                return True
            else:
                print("\033[1;33m[!] Continuing without killing process...\033[0m")
                return False
        else:
            print("\033[1;33m[!] No specific locking process found\033[0m")
            return False

    def wait_for_dpkg_lock(self, timeout=60):
        """Wait for dpkg lock to be released with smart handling"""
        print("\033[1;36m[→] Checking for system locks...\033[0m")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            if not self.is_dpkg_locked():
                print("\033[1;32m[✓] System ready for installation\033[0m")
                return True
            
            elapsed = int(time.time() - start_time)
            if elapsed >= 20:  # After 20 seconds, offer smart cleanup
                print(f"\033[1;33m[⚠️] System locked for {elapsed}s\033[0m")
                if self.smart_lock_cleanup():
                    return True
            
            dots = "." * ((elapsed // 2) % 4)
            print(f"\r\033[1;33m[⌛] Waiting for system locks{dots} ({elapsed}s)\033[0m", end='', flush=True)
            time.sleep(2)
        
        print(f"\r\033[1;31m[✘] Timeout waiting for system locks after {timeout}s\033[0m")
        return False

    def install_required_tools(self):
        """Install all required tools with smart lock handling"""
        print("\033[1;36m[→] Deploying NetStrike toolkit...\033[0m")
        print(f"\033[1;35m[⚡] Detected system: {self.distribution.upper()}\033[0m")
        
        # First check what tools are available
        available_tools, missing_tools = self.check_tools_availability()
        
        if not missing_tools:
            print("\033[1;32m[✅] All essential tools are already available!\033[0m")
            return True
        
        print(f"\033[1;33m[!] Need to install {len(missing_tools)} tools: {', '.join(missing_tools)}\033[0m")
        
        # Wait for system locks only if we need to install
        if not self.wait_for_dpkg_lock():
            print("\033[1;31m[✘] Cannot proceed - system locks held\033[0m")
            print("\033[1;33m[💡] Tip: Wait for other package operations to complete\033[0m")
            return False
        
        # Update system
        if not self.update_system():
            return False
        
        # Install tools based on distribution
        if self.distribution == "kali":
            return self.install_kali_tools(missing_tools)
        else:
            return self.install_generic_tools(missing_tools)

    def update_system(self):
        """Update system repositories"""
        print("\033[1;36m[→] Updating system repositories...\033[0m")
        
        if self.distribution == "kali":
            cmd = "apt update -y"
        else:
            cmd = "apt-get update -y"
            
        success = self.run_command_with_progress(cmd, "Updating repositories", timeout=120)
        if success:
            print("\033[1;32m[✅] System updated\033[0m")
            return True
        else:
            print("\033[1;33m[⚠️] Update failed - continuing anyway\033[0m")
            return True  # Continue anyway

    def run_command_with_progress(self, command, description, timeout=120):
        """Run command with progress animation"""
        print(f"\033[1;36m[→] {description}...\033[0m", end='', flush=True)
        
        def animate():
            frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
            i = 0
            while not stop_animation.is_set():
                print(f"\r\033[1;36m[→] {description}... {frames[i % len(frames)]}\033[0m", end='', flush=True)
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
                print(f"\r\033[1;32m[✅] {description} completed\033[0m")
                return True
            else:
                print(f"\r\033[1;31m[✘] {description} failed\033[0m")
                return False
                
        except subprocess.TimeoutExpired:
            stop_animation.set()
            animation_thread.join(timeout=1)
            print(f"\r\033[1;31m[✘] {description} timeout\033[0m")
            return False
        except Exception as e:
            stop_animation.set()
            animation_thread.join(timeout=1)
            print(f"\r\033[1;31m[✘] {description} error: {e}\033[0m")
            return False

    def install_kali_tools(self, missing_tools):
        """Install tools optimized for Kali Linux"""
        print("\033[1;36m[→] Kali Linux detected - smart installation...\033[0m")
        
        tools_installed = True
        
        for tool in missing_tools:
            print(f"\033[1;33m[!] Installing essential tool: {tool}\033[0m")
            if not self.install_package_kali(tool):
                print(f"\033[1;33m[⚠️] Failed to install {tool} - trying alternative...\033[0m")
                if tool == "mdk4":
                    self.install_mdk4_from_source()
            else:
                print(f"\033[1;32m[✅] {tool.upper()} installed successfully\033[0m")
        
        # Install Python packages using pip
        print("\033[1;36m[→] Checking Python packages...\033[0m")
        python_packages = ["requests", "scapy"]
        for package in python_packages:
            if not self.is_python_package_installed(package):
                self.install_python_package_pip(package)
            else:
                print(f"\033[1;32m[✅] {package.upper()} already installed\033[0m")
        
        # Setup wordlists
        print("\033[1;36m[→] Setting up wordlists...\033[0m")
        self.setup_wordlists()
        
        return self.verify_installation()

    def install_package_kali(self, package):
        """Install package on Kali Linux"""
        cmd = f"apt install -y {package}"
        return self.run_command_with_progress(cmd, f"Installing {package}", timeout=180)

    def install_generic_tools(self, missing_tools):
        """Install tools on generic Linux distributions"""
        print("\033[1;36m[→] Generic Linux detected - standard installation...\033[0m")
        
        for tool in missing_tools:
            if not self.install_package_generic(tool):
                print(f"\033[1;33m[⚠️] Failed to install {tool}\033[0m")
        
        # Python packages
        self.install_python_package_pip("requests")
        self.install_python_package_pip("scapy")
        
        self.setup_wordlists()
        return self.verify_installation()

    def install_package_generic(self, package):
        """Install package on generic Linux"""
        cmd = f"apt-get install -y {package}"
        return self.run_command_with_progress(cmd, f"Installing {package}", timeout=180)

    def install_mdk4_from_source(self):
        """Install MDK4 from source"""
        print("\033[1;33m[!] Installing MDK4 from source...\033[0m")
        
        cmds = [
            "git clone https://github.com/aircrack-ng/mdk4 2>/dev/null",
            "cd mdk4 && make 2>/dev/null",
            "cd mdk4 && make install 2>/dev/null", 
            "rm -rf mdk4 2>/dev/null"
        ]
        
        for cmd in cmds:
            if not self.run_command_with_progress(cmd, "Building MDK4", timeout=120):
                return False
        
        if self.core.run_command("command -v mdk4") and self.core.run_command("command -v mdk4").returncode == 0:
            print("\033[1;32m[✅] MDK4 installed from source\033[0m")
            return True
        return False

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
        """Install Python package using pip"""
        print(f"\033[1;36m[→] Installing {package} via pip...\033[0m")
        
        cmd = f"pip3 install {package} --break-system-packages --quiet"
        if self.run_command_with_progress(cmd, f"Installing {package}", timeout=60):
            print(f"\033[1;32m[✅] {package.upper()} installed\033[0m")
            return True
        else:
            print(f"\033[1;31m[✘] {package.upper()} installation failed\033[0m")
            return False

    def setup_wordlists(self):
        """Setup wordlists"""
        print("\033[1;36m[→] Checking wordlists...\033[0m")
        
        wordlist_dir = "/usr/share/wordlists"
        os.makedirs(wordlist_dir, exist_ok=True)
        
        if os.path.exists("/usr/share/wordlists/rockyou.txt.gz"):
            if not os.path.exists("/usr/share/wordlists/rockyou.txt"):
                self.run_command_with_progress(
                    "gzip -dc /usr/share/wordlists/rockyou.txt.gz > /usr/share/wordlists/rockyou.txt",
                    "Extracting rockyou.txt"
                )
            print("\033[1;32m[✅] ROCKYOU.TXT available\033[0m")
        elif os.path.exists("/usr/share/wordlists/rockyou.txt"):
            print("\033[1;32m[✅] ROCKYOU.TXT available\033[0m")
        else:
            self.create_basic_wordlist()

    def create_basic_wordlist(self):
        """Create a basic wordlist"""
        basic_path = "/usr/share/wordlists/netstrike_passwords.txt"
        print("\033[1;36m[→] Creating professional wordlist...\033[0m")
        
        passwords = [
            "123456", "password", "12345678", "qwerty", "123456789",
            "12345", "1234", "111111", "1234567", "dragon", "123123",
            "baseball", "abc123", "football", "monkey", "letmein",
            "admin", "welcome", "passw0rd", "master", "hello",
            "freedom", "whatever", "qazwsx", "trustno1", "jennifer"
        ]
        
        try:
            with open(basic_path, 'w') as f:
                for pwd in passwords:
                    f.write(pwd + '\n')
            print("\033[1;32m[✅] Professional wordlist created\033[0m")
            return True
        except Exception as e:
            print(f"\033[1;31m[✘] Wordlist creation failed: {e}\033[0m")
            return False

    def verify_installation(self):
        """Verify critical tools are installed"""
        print("\033[1;36m[→] Verifying installation...\033[0m")
        
        essential_tools = ["aircrack-ng", "macchanger", "iwconfig", "mdk4"]
        
        missing_tools = []
        
        for tool in essential_tools:
            if self.core.run_command(f"command -v {tool}") and self.core.run_command(f"command -v {tool}").returncode == 0:
                print(f"\033[1;32m[✅] {tool.upper()} verified\033[0m")
            else:
                print(f"\033[1;31m[✘] {tool.upper()} missing\033[0m")
                missing_tools.append(tool)
        
        if not missing_tools:
            print("\033[1;32m[✅] All essential tools verified\033[0m")
            return True
        else:
            print(f"\033[1;33m[⚠️] Missing essential tools: {', '.join(missing_tools)}\033[0m")
            return False
