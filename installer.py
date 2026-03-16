#!/usr/bin/env python3
"""
NETSTRIKE v4.0 - PHANTOM EDITION
Auto-Installer — fully automatic, zero user interaction required
"""

import os
import subprocess
import time
import fcntl

# binary name → apt package name
TOOL_PACKAGES = {
    "airmon-ng":     "aircrack-ng",
    "airodump-ng":   "aircrack-ng",
    "aireplay-ng":   "aircrack-ng",
    "aircrack-ng":   "aircrack-ng",
    "mdk4":          "mdk4",
    "macchanger":    "macchanger",
    "hostapd":       "hostapd",
    "dnsmasq":       "dnsmasq",
    "hcxdumptool":   "hcxdumptool",
    "hcxpcapngtool": "hcxtools",
    "hashcat":       "hashcat",
    "reaver":        "reaver",
    "bully":         "bully",
    "wash":          "reaver",
    "iwconfig":      "wireless-tools",
    "ip":            "iproute2",
}


class ToolInstaller:
    def __init__(self, core):
        self.core = core

    # ─────────────────────────────────────────────
    # PUBLIC ENTRY POINT
    # ─────────────────────────────────────────────

    def install_required_tools(self):
        """Check and silently auto-install every required tool."""
        print("\033[1;36m[→] Verifying NetStrike toolkit...\033[0m")

        # Collect missing binaries → unique packages
        missing_packages = {}  # pkg → [binaries]
        for binary, package in TOOL_PACKAGES.items():
            r = self._run_silent(f"command -v {binary} 2>/dev/null")
            if r:
                print(f"  \033[1;32m[✓]\033[0m {binary}")
            else:
                print(f"  \033[1;33m[!]\033[0m {binary} — not found")
                missing_packages.setdefault(package, []).append(binary)

        if not missing_packages:
            print("\033[1;32m[✓] All tools present\033[0m")
            self._ensure_wordlists()
            return True

        pkgs = sorted(missing_packages.keys())
        print(f"\033[1;33m[!] Installing: {', '.join(pkgs)}\033[0m")
        self._wait_for_dpkg_lock()
        self._apt("apt-get update -qq", timeout=90)

        for pkg in pkgs:
            print(f"\033[1;36m[→] Installing {pkg}...\033[0m", end="", flush=True)
            ok = self._apt(f"apt-get install -y {pkg}", timeout=240)
            if ok:
                print(f"\r\033[1;32m[✓] {pkg}\033[0m                        ")
            else:
                if pkg == "mdk4":
                    ok = self._build_mdk4_from_source()
                if not ok:
                    print(f"\r\033[1;33m[!] {pkg} failed — continuing\033[0m")

        self._ensure_wordlists()
        return self._verify_critical()

    # ─────────────────────────────────────────────
    # WORDLIST SETUP
    # ─────────────────────────────────────────────

    def _ensure_wordlists(self):
        gz  = "/usr/share/wordlists/rockyou.txt.gz"
        txt = "/usr/share/wordlists/rockyou.txt"
        if os.path.exists(gz) and not os.path.exists(txt):
            print("\033[1;36m[→] Extracting rockyou.txt...\033[0m")
            self._apt(f"gzip -dc {gz} > {txt}", timeout=90)
            if os.path.exists(txt):
                print("\033[1;32m[✓] rockyou.txt ready\033[0m")
        # cracker.py builds its own fallback if rockyou is absent

    # ─────────────────────────────────────────────
    # INTERNAL HELPERS
    # ─────────────────────────────────────────────

    def _run_silent(self, cmd, timeout=10):
        """Return stdout string if command succeeds, else None."""
        try:
            r = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=timeout
            )
            return r.stdout.strip() if r.returncode == 0 and r.stdout.strip() else None
        except Exception:
            return None

    def _apt(self, cmd, timeout=180):
        """Run apt/shell command, return True on success."""
        try:
            r = subprocess.run(
                cmd, shell=True, capture_output=True, text=True, timeout=timeout
            )
            return r.returncode == 0
        except (subprocess.TimeoutExpired, Exception):
            return False

    def _wait_for_dpkg_lock(self, timeout=90):
        lock_files = [
            "/var/lib/dpkg/lock-frontend",
            "/var/lib/dpkg/lock",
            "/var/lib/apt/lists/lock",
        ]
        start = time.time()
        while time.time() - start < timeout:
            locked = False
            for lf in lock_files:
                if os.path.exists(lf):
                    try:
                        with open(lf, 'w') as f:
                            fcntl.flock(f.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
                    except (IOError, BlockingIOError):
                        locked = True
                        break
            if not locked:
                return True
            elapsed = int(time.time() - start)
            print(
                f"\r\033[1;33m[⌛] Waiting for package manager... ({elapsed}s)\033[0m",
                end="", flush=True
            )
            time.sleep(3)
        print()
        return False

    def _build_mdk4_from_source(self):
        print("\033[1;36m[→] Building mdk4 from source...\033[0m")
        steps = [
            "apt-get install -y libpcap-dev git build-essential 2>/dev/null",
            "rm -rf /tmp/_mdk4src && git clone https://github.com/aircrack-ng/mdk4 /tmp/_mdk4src 2>/dev/null",
            "make -C /tmp/_mdk4src 2>/dev/null",
            "make -C /tmp/_mdk4src install 2>/dev/null",
            "rm -rf /tmp/_mdk4src",
        ]
        for step in steps:
            self._apt(step, timeout=150)
        return bool(self._run_silent("command -v mdk4"))

    def _verify_critical(self):
        critical = ["airmon-ng", "airodump-ng", "aireplay-ng", "mdk4"]
        missing = [b for b in critical if not self._run_silent(f"command -v {b}")]
        if missing:
            print(f"\033[1;33m[!] Still missing: {', '.join(missing)}\033[0m")
            print("\033[1;33m[!] Install manually: apt-get install aircrack-ng mdk4\033[0m")
            return False
        print("\033[1;32m[✓] Core toolkit verified\033[0m")
        return True
