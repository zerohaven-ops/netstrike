#!/usr/bin/env python3
"""
NETSTRIKE v4.0 - PHANTOM EDITION
Core Module
"""

import os
import sys
import time
import subprocess
import threading
import signal


class NetStrikeCore:
    def __init__(self):
        self.interface = ""
        self.mon_interface = ""
        self.original_mac = ""
        self.original_ip = ""
        self.mac_spoof_thread = None
        self.ip_spoof_thread = None
        self.spoofing_active = False
        self.attack_processes = []
        self.current_operation = None

    # ─────────────────────────────────────────────
    # ROOT / DEPS
    # ─────────────────────────────────────────────

    def check_root(self):
        if os.geteuid() != 0:
            print("\033[1;31m[✘] Root privileges required\033[0m")
            return False
        print("\033[1;32m[✓] Root confirmed\033[0m")
        return True

    def check_dependencies(self):
        print("\033[1;36m[→] Checking toolkit...\033[0m")

        # binary -> apt package
        tools = {
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
        }

        missing_pkgs = []
        for binary, package in tools.items():
            r = self.run_command(f"command -v {binary} 2>/dev/null")
            found = bool(r and r.stdout.strip())
            status = "\033[1;32m[✓]\033[0m" if found else "\033[1;33m[!]\033[0m"
            print(f"  {status} {binary}")
            if not found and package not in missing_pkgs:
                missing_pkgs.append(package)

        if missing_pkgs:
            print(f"\033[1;33m[!] Still missing after setup: {', '.join(missing_pkgs)}\033[0m")
            print("\033[1;33m[!] Run: apt-get install " + " ".join(missing_pkgs) + "\033[0m")

    # ─────────────────────────────────────────────
    # COMMAND RUNNER
    # ─────────────────────────────────────────────

    def run_command(self, command, background=False, timeout=30):
        try:
            if background:
                return subprocess.Popen(
                    command, shell=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            return subprocess.run(
                command, shell=True,
                capture_output=True, text=True,
                timeout=timeout
            )
        except subprocess.TimeoutExpired:
            return None
        except Exception:
            return None

    # ─────────────────────────────────────────────
    # INTERFACE SELECTION
    # ─────────────────────────────────────────────

    def detect_wireless_interfaces(self):
        interfaces = []
        cmds = [
            "iwconfig 2>/dev/null | grep -E '^[a-zA-Z]' | grep -v 'no wireless' | awk '{print $1}'",
            "ip link show | grep -E '^[0-9]+:' | awk -F: '{print $2}' | grep -E '(wlan|wlx|wlp)' | tr -d ' '",
        ]
        for cmd in cmds:
            r = self.run_command(cmd)
            if r and r.stdout:
                for iface in r.stdout.split('\n'):
                    iface = iface.strip()
                    if iface and iface not in interfaces:
                        interfaces.append(iface)
        return interfaces

    def _get_iface_info(self, iface):
        """Return (mode, driver, chipset_hint) for display."""
        mode = "Managed"
        r = self.run_command(f"iwconfig {iface} 2>/dev/null")
        if r and "Mode:Monitor" in r.stdout:
            mode = "Monitor"

        driver = ""
        r2 = self.run_command(f"ethtool -i {iface} 2>/dev/null | grep driver")
        if r2 and r2.stdout.strip():
            driver = r2.stdout.strip().split(":")[-1].strip()
        if not driver:
            r3 = self.run_command(f"readlink /sys/class/net/{iface}/device/driver 2>/dev/null")
            if r3 and r3.stdout.strip():
                driver = r3.stdout.strip().split("/")[-1]

        chipset = ""
        r4 = self.run_command(f"iw {iface} info 2>/dev/null | grep -i wiphy")
        if r4 and r4.stdout.strip():
            phy = r4.stdout.strip().split()[-1]
            r5 = self.run_command(f"iw {phy} info 2>/dev/null | grep -i 'Band\\|Wiphy'")
            if r5 and "Band" in r5.stdout:
                if "5 GHz" in r5.stdout or "Band 2" in r5.stdout:
                    chipset = "2.4/5GHz"
                else:
                    chipset = "2.4GHz"

        return mode, driver, chipset

    def select_interface(self):
        print("\033[1;36m[🔍] Scanning for wireless adapters...\033[0m")
        interfaces = self.detect_wireless_interfaces()
        if not interfaces:
            print("\033[1;31m[✘] No wireless interfaces found\033[0m")
            print("\033[1;33m[!] Plug in a WiFi adapter and try again\033[0m")
            return False

        # Build info for all interfaces
        iface_data = []
        for iface in interfaces:
            mode, driver, chipset = self._get_iface_info(iface)
            iface_data.append((iface, mode, driver, chipset))

        print()
        print("\033[1;35m╔══════════════════════════════════════════════════╗\033[0m")
        print("\033[1;35m║         📡  WIRELESS ADAPTERS DETECTED           ║\033[0m")
        print("\033[1;35m╠══════════════════════════════════════════════════╣\033[0m")
        for i, (iface, mode, driver, chipset) in enumerate(iface_data, 1):
            mode_color = "\033[1;32m" if mode == "Monitor" else "\033[1;33m"
            info_parts = []
            if driver:
                info_parts.append(driver)
            if chipset:
                info_parts.append(chipset)
            info_str = " | ".join(info_parts) if info_parts else ""
            print(f"\033[1;35m║  \033[1;36m{i}\033[0m) \033[1;32m{iface:<12}\033[0m {mode_color}{mode:<8}\033[0m \033[1;37m{info_str:<22}\033[0m\033[1;35m║\033[0m")
        print("\033[1;35m╚══════════════════════════════════════════════════╝\033[0m")

        # Auto-select if only one interface
        if len(interfaces) == 1:
            self.interface = interfaces[0]
            print(f"\033[1;32m[✓] Auto-selected: {self.interface} (only adapter found)\033[0m")
            return True

        try:
            idx = int(input(f"\n\033[1;36m[?] Select adapter (1-{len(interfaces)}): \033[0m")) - 1
            if 0 <= idx < len(interfaces):
                self.interface = interfaces[idx]
                print(f"\033[1;32m[✓] Selected: {self.interface}\033[0m")
                return True
        except (ValueError, IndexError):
            pass
        print("\033[1;31m[✘] Invalid selection\033[0m")
        return False

    def save_original_config(self):
        r = self.run_command(f"cat /sys/class/net/{self.interface}/address 2>/dev/null")
        self.original_mac = r.stdout.strip() if r and r.stdout.strip() else "unknown"

        self.original_ip = "unknown"
        r = self.run_command(f"ip addr show {self.interface} 2>/dev/null")
        if r and "inet " in r.stdout:
            for line in r.stdout.split('\n'):
                if "inet " in line and "scope global" in line:
                    self.original_ip = line.strip().split()[1].split('/')[0]
                    break
        print(f"\033[1;33m[→] MAC: {self.original_mac}  |  IP: {self.original_ip}\033[0m")

    # ─────────────────────────────────────────────
    # MONITOR MODE
    # ─────────────────────────────────────────────

    def setup_monitor_mode(self):
        print("\033[1;36m[→] Setting up monitor mode...\033[0m")

        # Kill interfering processes
        self.run_command("airmon-ng check kill > /dev/null 2>&1")
        time.sleep(2)

        # Start monitor
        self.run_command(f"airmon-ng start {self.interface} > /dev/null 2>&1")
        time.sleep(2)

        # Find the monitor interface
        r = self.run_command("iwconfig 2>/dev/null | grep 'Mode:Monitor' | awk '{print $1}'")
        if r and r.stdout.strip():
            self.mon_interface = r.stdout.strip().split('\n')[0].strip()
        else:
            candidates = [f"{self.interface}mon", "mon0", "wlan0mon", "wlan1mon", "wlan2mon"]
            for name in candidates:
                r = self.run_command(f"iwconfig {name} 2>/dev/null")
                if r and "Mode:Monitor" in r.stdout:
                    self.mon_interface = name
                    break
            else:
                r = self.run_command(f"iwconfig {self.interface} 2>/dev/null")
                if r and "Mode:Monitor" in r.stdout:
                    self.mon_interface = self.interface
                else:
                    print("\033[1;31m[✘] Monitor mode failed\033[0m")
                    return False

        # Verify
        r = self.run_command(f"iwconfig {self.mon_interface} 2>/dev/null")
        if r and "Mode:Monitor" in r.stdout:
            print(f"\033[1;32m[✓] Monitor mode active: {self.mon_interface}\033[0m")
            self._boost_txpower()
            return True

        print("\033[1;31m[✘] Monitor mode verification failed\033[0m")
        return False

    def _boost_txpower(self):
        """Max out TX power for strongest signal reach."""
        # Try regulatory domain trick first
        self.run_command("iw reg set BO 2>/dev/null")
        time.sleep(0.5)
        # Boost via iw
        r = self.run_command(
            f"iw dev {self.mon_interface} set txpower fixed 3000 2>/dev/null"
        )
        if not (r and r.returncode == 0):
            # Fallback: iwconfig
            self.run_command(
                f"iwconfig {self.mon_interface} txpower 30 2>/dev/null"
            )
        # Also set on physical interface
        self.run_command(
            f"iw dev {self.interface} set txpower fixed 3000 2>/dev/null"
        )
        print("\033[1;32m[✓] TX power maximized\033[0m")

    def stop_monitor_mode(self):
        if self.mon_interface:
            self.run_command(f"airmon-ng stop {self.mon_interface} > /dev/null 2>&1")
            self.run_command("systemctl restart NetworkManager > /dev/null 2>&1")

    # ─────────────────────────────────────────────
    # ANONYMITY / SPOOFING
    # ─────────────────────────────────────────────

    def start_advanced_spoofing(self):
        self.spoofing_active = True
        self.mac_spoof_thread = threading.Thread(target=self._mac_spoof_loop, daemon=True)
        self.ip_spoof_thread = threading.Thread(target=self._ip_refresh_loop, daemon=True)
        self.mac_spoof_thread.start()
        self.ip_spoof_thread.start()
        print("\033[1;32m[✓] Anonymity layer active (MAC rotation every 3 min)\033[0m")

    def _mac_spoof_loop(self):
        while self.spoofing_active:
            time.sleep(180)
            if not self.spoofing_active:
                break
            try:
                self.run_command(f"ip link set {self.mon_interface} down 2>/dev/null")
                self.run_command(f"macchanger -r {self.mon_interface} > /dev/null 2>&1")
                self.run_command(f"ip link set {self.mon_interface} up 2>/dev/null")
                # Re-boost TX power after interface restart
                self.run_command(f"iw dev {self.mon_interface} set txpower fixed 3000 2>/dev/null")
            except Exception:
                pass

    def _ip_refresh_loop(self):
        while self.spoofing_active:
            time.sleep(300)
            if not self.spoofing_active:
                break
            try:
                self.run_command("dhclient -r 2>/dev/null; dhclient 2>/dev/null")
            except Exception:
                pass

    def stop_advanced_spoofing(self):
        self.spoofing_active = False

    # ─────────────────────────────────────────────
    # PROCESS MANAGEMENT
    # ─────────────────────────────────────────────

    def add_attack_process(self, process):
        if process and process.poll() is None:
            self.attack_processes.append(process)

    def stop_all_attacks(self):
        for p in self.attack_processes:
            try:
                if p and p.poll() is None:
                    p.terminate()
                    p.wait(timeout=2)
            except Exception:
                pass
        self.attack_processes = []

        for cmd in [
            "killall airodump-ng aireplay-ng mdk4 reaver bully hostapd dnsmasq hcxdumptool 2>/dev/null",
            "pkill -9 -f 'airodump-ng|aireplay-ng|mdk4|hostapd|dnsmasq|hcxdumptool|hashcat|reaver|bully' 2>/dev/null",
        ]:
            self.run_command(cmd)

    def set_current_operation(self, op):
        self.current_operation = op

    def clear_current_operation(self):
        self.current_operation = None

    # ─────────────────────────────────────────────
    # SIGNAL + CLEANUP
    # ─────────────────────────────────────────────

    def signal_handler(self, sig, frame):
        if self.current_operation:
            print(f"\n\033[1;33m[!] Stopping: {self.current_operation}\033[0m")
            self.stop_all_attacks()
            self.clear_current_operation()
        else:
            print("\n\033[1;33m[!] Exiting...\033[0m")
            self.nuclear_cleanup()

    def nuclear_cleanup(self):
        print("\033[1;35m[→] Cleanup protocol initiated...\033[0m")

        self.stop_all_attacks()
        self.stop_advanced_spoofing()

        # Flush iptables
        for table in ["", "-t nat", "-t mangle", "-t raw"]:
            self.run_command(f"iptables {table} --flush 2>/dev/null")

        self.run_command("echo 0 > /proc/sys/net/ipv4/ip_forward 2>/dev/null")
        self.run_command("ip route flush cache 2>/dev/null")

        self.stop_monitor_mode()

        # Restore original MAC
        if self.original_mac and self.original_mac != "unknown":
            self.run_command(f"ip link set {self.interface} down 2>/dev/null")
            self.run_command(f"macchanger -m {self.original_mac} {self.interface} > /dev/null 2>&1")
            self.run_command(f"ip link set {self.interface} up 2>/dev/null")

        # Remove temp files
        for pattern in [
            "/tmp/ns_*", "/tmp/netstrike_*", "/tmp/*.cap", "/tmp/*.csv",
            "/tmp/*.pcapng", "/tmp/*.hc22000", "/tmp/*.hash", "/tmp/*.log", "/tmp/*.sh",
        ]:
            self.run_command(f"rm -f {pattern} 2>/dev/null")

        self.run_command("systemctl restart NetworkManager > /dev/null 2>&1")

        print("\033[1;32m[✓] Cleanup complete\033[0m")
        sys.exit(0)
