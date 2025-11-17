#!/usr/bin/env python3

import os
import subprocess
import time
import sys
import threading
import fcntl

class ToolInstaller:
    def __init__(self, core=None):
        self.core = core
        self.distribution = self.detect_distribution()

    def detect_distribution(self):
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

    def wait_for_dpkg_lock(self, timeout=300):
        print("\033[1;33m[!] CHECKING FOR SYSTEM LOCKS...\033[0m")
        start_time = time.time()
        while time.time() - start_time < timeout:
            if not self.is_dpkg_locked():
                print("\033[1;32m[✓] SYSTEM READY FOR INSTALLATION\033[0m")
                return True
            elapsed = int(time.time() - start_time)
            dots = "." * (elapsed % 4)
            print(f"\r\033[1;33m[⌛] WAITING FOR SYSTEM LOCKS{dots} ({elapsed}s)\033[0m", end='', flush=True)
            time.sleep(2)
        print(f"\r\033[1;31m[✘] TIMEOUT WAITING FOR SYSTEM LOCKS AFTER {timeout}s\033[0m")
        return False

    def run_command(self, cmd, desc="", timeout=300):
        print(f"\033[1;33m[→] {desc}...\033[0m", end='', flush=True)
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
            if result.returncode == 0:
                print(f"\r\033[1;32m[✓] {desc} COMPLETED\033[0m")
                return True
            else:
                print(f"\r\033[1;31m[✘] {desc} FAILED: {result.stderr.strip()}\033[0m")
                return False
        except subprocess.TimeoutExpired:
            print(f"\r\033[1;31m[✘] {desc} TIMEOUT\033[0m")
            return False
        except Exception as e:
            print(f"\r\033[1;31m[✘] {desc} ERROR: {e}\033[0m")
            return False

    def update_system(self):
        cmd = "apt update -y || apt-get update -y"
        return self.run_command(cmd, "Updating system repositories", timeout=180)

    def install_package(self, package):
        if self.check_tool_installed(package):
            print(f"\033[1;32m[✓] {package.upper()} ALREADY INSTALLED\033[0m")
            return True
        cmd = f"apt install -y {package} || apt-get install -y {package}"
        return self.run_command(cmd, f"Installing {package}", timeout=180)

    def install_python_package(self, package):
        try:
            subprocess.run(f"python3 -c 'import {package}'", shell=True, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"\033[1;32m[✓] {package.upper()} ALREADY INSTALLED\033[0m")
            return True
        except subprocess.CalledProcessError:
            return self.run_command(f"pip3 install {package} --break-system-packages --quiet", f"Installing Python package {package}", 120)

    def setup_wordlists(self):
        wordlist_dir = "/usr/share/wordlists"
        os.makedirs(wordlist_dir, exist_ok=True)
        if os.path.exists("/usr/share/wordlists/rockyou.txt.gz") and not os.path.exists("/usr/share/wordlists/rockyou.txt"):
            self.run_command("gzip -dc /usr/share/wordlists/rockyou.txt.gz > /usr/share/wordlists/rockyou.txt", "Extracting rockyou.txt", 60)
        elif not os.path.exists("/usr/share/wordlists/rockyou.txt"):
            basic_path = "/usr/share/wordlists/netstrike_passwords.txt"
            with open(basic_path, "w") as f:
                f.write("\n".join([
                    "123456", "password", "12345678", "qwerty", "123456789",
                    "12345", "1234", "111111", "1234567", "dragon", "123123",
                    "baseball", "abc123", "football", "monkey", "letmein",
                    "696969", "shadow", "master", "666666"
                ]))
            print(f"\033[1;32m[✓] BASIC WORDLIST CREATED\033[0m")

    def check_tool_installed(self, tool):
        return subprocess.run(f"command -v {tool}", shell=True, stdout=subprocess.DEVNULL).returncode == 0

    def install_required_tools(self):
        if not self.wait_for_dpkg_lock(): return False
        if not self.update_system(): return False

        if self.distribution == "kali":
            self.install_package("mdk4")
        else:
            for tool in ["aircrack-ng", "macchanger", "reaver", "mdk4"]:
                self.install_package(tool)

        for py_pkg in ["requests", "scapy"]:
            self.install_python_package(py_pkg)

        self.setup_wordlists()
        print("\033[1;32m[✓] INSTALLATION COMPLETE\033[0m")
        return True

if __name__ == "__main__":
    installer = ToolInstaller()
    installer.install_required_tools()
