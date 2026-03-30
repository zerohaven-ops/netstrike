#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════
# NETSTRIKE v5.0 BEAST EDITION — Universal Kali Linux Installer
# Supports: Kali 2019.1 → 2026+, Kali Purple, NetHunter, Parrot, Debian
# Usage: sudo bash install.sh
# ═══════════════════════════════════════════════════════════════════════

RED='\033[1;31m'
GRN='\033[1;32m'
YLW='\033[1;33m'
CYN='\033[1;36m'
MGN='\033[1;35m'
WHT='\033[1;37m'
RST='\033[0m'

INSTALL_DIR="/opt/netstrike"
BIN_LINK="/usr/local/bin/netstrike"
SESSION_DIR="$HOME/netstrike"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ─── Root check ───────────────────────────────────────────────────────
if [ "$(id -u)" -ne 0 ]; then
    echo -e "${RED}[✘] Root required: sudo bash install.sh${RST}"
    exit 1
fi

# ─── apt required ─────────────────────────────────────────────────────
if ! command -v apt-get &>/dev/null; then
    echo -e "${RED}[✘] This installer requires a Debian/Kali-based system${RST}"
    exit 1
fi

clear
echo -e "${MGN}"
cat << 'BANNER'
╔══════════════════════════════════════════════════════════════════╗
║  ███╗   ██╗███████╗████████╗███████╗████████╗██████╗ ██╗██╗  ██╗║
║  ████╗  ██║██╔════╝╚══██╔══╝██╔════╝╚══██╔══╝██╔══██╗██║██║ ██╔╝║
║  ██╔██╗ ██║█████╗     ██║   ███████╗   ██║   ██████╔╝██║█████╔╝ ║
║  ██║╚██╗██║██╔══╝     ██║   ╚════██║   ██║   ██╔══██╗██║██╔═██╗ ║
║  ██║ ╚████║███████╗   ██║   ███████║   ██║   ██║  ██║██║██║  ██╗║
║  ╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝╚═╝  ╚═╝║
║                                                                  ║
║     ⚡  BEAST EDITION v5.0 — SYSTEM INSTALLER  ⚡               ║
╚══════════════════════════════════════════════════════════════════╝
BANNER
echo -e "${RST}"

# ─── Detect OS ────────────────────────────────────────────────────────
OS_ID=$(grep -oP '(?<=^ID=).+' /etc/os-release 2>/dev/null | tr -d '"' || echo "unknown")
VERSION_ID=$(grep -oP '(?<=^VERSION_ID=).+' /etc/os-release 2>/dev/null | tr -d '"' || echo "")
echo -e "${CYN}[→] System: ${WHT}${OS_ID} ${VERSION_ID}${RST}"

# ─── dpkg lock handler ────────────────────────────────────────────────
wait_apt() {
    local retries=30
    while fuser /var/lib/dpkg/lock-frontend /var/lib/apt/lists/lock &>/dev/null 2>&1; do
        echo -ne "\r${YLW}[⌛] Waiting for apt lock... (${retries}s)${RST}"
        sleep 3
        retries=$((retries - 1))
        [ "$retries" -le 0 ] && { echo -e "\n${RED}[✘] apt lock timeout — kill other apt processes${RST}"; exit 1; }
    done
    echo -ne "\r                                              \r"
}

# ─── Package install helper ───────────────────────────────────────────
install_pkg() {
    local pkg="$1"
    wait_apt
    DEBIAN_FRONTEND=noninteractive apt-get install -y -qq "$pkg" \
        -o Dpkg::Options::="--force-confdef" \
        -o Dpkg::Options::="--force-confold" \
        2>/dev/null
}

# ─── Update ───────────────────────────────────────────────────────────
echo -e "${CYN}[→] Updating package list...${RST}"
wait_apt
apt-get update -qq 2>/dev/null || echo -e "${YLW}[!] Update had warnings (continuing)${RST}"

# ─── Tools map: binary → apt package ─────────────────────────────────
# Tested across Kali 2019.x, 2020.x, 2021.x, 2022.x, 2023.x, 2024.x, 2025.x, 2026.x
declare -A TOOL_MAP=(
    ["airmon-ng"]="aircrack-ng"
    ["airodump-ng"]="aircrack-ng"
    ["aireplay-ng"]="aircrack-ng"
    ["aircrack-ng"]="aircrack-ng"
    ["mdk4"]="mdk4"
    ["macchanger"]="macchanger"
    ["hostapd"]="hostapd"
    ["dnsmasq"]="dnsmasq"
    ["hcxdumptool"]="hcxdumptool"
    ["hcxpcapngtool"]="hcxtools"
    ["hashcat"]="hashcat"
    ["reaver"]="reaver"
    ["bully"]="bully"
    ["wash"]="reaver"
    ["iwconfig"]="wireless-tools"
    ["iw"]="iw"
    ["ip"]="iproute2"
    ["python3"]="python3"
    ["wget"]="wget"
    ["curl"]="curl"
)

FAILED=()
echo -e "${CYN}[→] Installing toolkit...${RST}"

for binary in "${!TOOL_MAP[@]}"; do
    pkg="${TOOL_MAP[$binary]}"
    if command -v "$binary" &>/dev/null; then
        echo -e "  ${GRN}[✓]${RST} $binary"
    else
        echo -ne "  ${YLW}[→]${RST} $pkg ... "
        if install_pkg "$pkg"; then
            echo -e "${GRN}OK${RST}"
        else
            echo -e "${RED}FAILED${RST}"
            FAILED+=("$pkg")
        fi
    fi
done

# ─── mdk4 source fallback ─────────────────────────────────────────────
if ! command -v mdk4 &>/dev/null; then
    echo -e "${YLW}[!] mdk4 not in apt — building from source...${RST}"
    install_pkg "build-essential" 2>/dev/null
    install_pkg "libpcap-dev" 2>/dev/null
    install_pkg "git" 2>/dev/null
    TMP=$(mktemp -d)
    if git clone --depth 1 https://github.com/aircrack-ng/mdk4.git "$TMP/mdk4" 2>/dev/null; then
        make -C "$TMP/mdk4" -j"$(nproc)" 2>/dev/null && make -C "$TMP/mdk4" install 2>/dev/null && \
            echo -e "  ${GRN}[✓]${RST} mdk4 built from source" || \
            echo -e "  ${RED}[✘]${RST} mdk4 build failed"
    else
        echo -e "  ${YLW}[!]${RST} git clone failed (no internet?) — install mdk4 manually"
    fi
    rm -rf "$TMP"
fi

# ─── hcxtools: try alternate package names across Kali versions ────────
if ! command -v hcxpcapngtool &>/dev/null; then
    for alt in hcxtools hcx-tools; do
        install_pkg "$alt" 2>/dev/null && break || true
    done
fi

# ─── Optional but useful extras ───────────────────────────────────────
for pkg in net-tools ethtool; do
    install_pkg "$pkg" 2>/dev/null || true
done

# ─── rockyou.txt ──────────────────────────────────────────────────────
ROCKYOU="/usr/share/wordlists/rockyou.txt"
ROCKYOU_GZ="${ROCKYOU}.gz"
mkdir -p /usr/share/wordlists
if [ ! -f "$ROCKYOU" ]; then
    if [ -f "$ROCKYOU_GZ" ]; then
        echo -e "${CYN}[→] Extracting rockyou.txt...${RST}"
        gzip -dk "$ROCKYOU_GZ" && echo -e "  ${GRN}[✓]${RST} rockyou.txt ready"
    else
        install_pkg "wordlists" 2>/dev/null && [ -f "$ROCKYOU_GZ" ] && gzip -dk "$ROCKYOU_GZ" 2>/dev/null || true
    fi
fi
[ -f "$ROCKYOU" ] && \
    echo -e "  ${GRN}[✓]${RST} rockyou.txt ($(wc -l < "$ROCKYOU") lines)" || \
    echo -e "  ${YLW}[!]${RST} rockyou.txt absent — built-in wordlists will be used"

# ─── Max TX power — regulatory domain ─────────────────────────────────
if command -v iw &>/dev/null; then
    iw reg set BO 2>/dev/null || true
    # Persist across reboots via udev
    mkdir -p /etc/udev/rules.d
    echo 'ACTION=="add", SUBSYSTEM=="ieee80211", RUN+="/sbin/iw reg set BO"' \
        > /etc/udev/rules.d/99-netstrike-regdomain.rules 2>/dev/null || true
    # crda config (older Kali)
    if [ -f /etc/default/crda ]; then
        sed -i 's/^REGDOMAIN=.*/REGDOMAIN=BO/' /etc/default/crda
    else
        echo "REGDOMAIN=BO" > /etc/default/crda 2>/dev/null || true
    fi
    echo -e "  ${GRN}[✓]${RST} Regulatory domain set to BO (max TX power)"
fi

# ─── Session directory ────────────────────────────────────────────────
mkdir -p "$SESSION_DIR"
echo -e "${CYN}[→] Session dir: ${WHT}${SESSION_DIR}${RST}"

# ─── Install files ────────────────────────────────────────────────────
echo -e "${CYN}[→] Installing to ${WHT}${INSTALL_DIR}${RST}..."
mkdir -p "$INSTALL_DIR"
cp "$SCRIPT_DIR"/*.py "$INSTALL_DIR/" 2>/dev/null || true
[ -f "$SCRIPT_DIR/install.sh" ] && cp "$SCRIPT_DIR/install.sh" "$INSTALL_DIR/"
chmod +x "$INSTALL_DIR/netstrike.py" 2>/dev/null || true

# ─── System launcher ──────────────────────────────────────────────────
cat > "$BIN_LINK" << 'LAUNCHER'
#!/bin/bash
if [ "$(id -u)" -ne 0 ]; then
    echo -e "\033[1;31m[✘] NetStrike requires root: sudo netstrike\033[0m"
    exit 1
fi
cd /opt/netstrike && exec python3 netstrike.py "$@"
LAUNCHER
chmod +x "$BIN_LINK"
echo -e "  ${GRN}[✓]${RST} System command: ${WHT}sudo netstrike${RST}"

# ─── Kali application menu entry ─────────────────────────────────────
if [ -d /usr/share/applications ]; then
    cat > /usr/share/applications/netstrike.desktop << 'DESKTOP'
[Desktop Entry]
Name=NetStrike BEAST
Comment=Professional Wireless Security Testing Suite v5.0
Exec=bash -c "sudo netstrike; echo 'Press Enter...'; read"
Icon=kali-menu
Terminal=true
Type=Application
Categories=08-exploitation-tools;
DESKTOP
    echo -e "  ${GRN}[✓]${RST} Kali menu entry added"
fi

# ─── Bash + Zsh completion ────────────────────────────────────────────
cat > /etc/bash_completion.d/netstrike << 'COMP'
_netstrike() {
    local cur="${COMP_WORDS[COMP_CWORD]}"
    COMPREPLY=($(compgen -W "--help --version" -- "$cur"))
}
complete -F _netstrike netstrike
COMP

# ─── Uninstall script ─────────────────────────────────────────────────
cat > "$INSTALL_DIR/uninstall.sh" << 'UNINSTALL'
#!/bin/bash
echo "Removing NetStrike BEAST..."
rm -f /usr/local/bin/netstrike
rm -f /usr/share/applications/netstrike.desktop
rm -f /etc/bash_completion.d/netstrike
rm -f /etc/udev/rules.d/99-netstrike-regdomain.rules
rm -rf /opt/netstrike
echo "Uninstall complete. Session data in ~/netstrike/ is preserved."
UNINSTALL
chmod +x "$INSTALL_DIR/uninstall.sh"

# ─── Final verification ───────────────────────────────────────────────
echo ""
echo -e "${CYN}[→] Verifying critical tools...${RST}"
CRITICAL=(airmon-ng airodump-ng aireplay-ng mdk4 python3)
MISS_CRIT=()
for b in "${CRITICAL[@]}"; do
    if command -v "$b" &>/dev/null; then
        echo -e "  ${GRN}[✓]${RST} $b"
    else
        echo -e "  ${RED}[✘]${RST} $b — MISSING"
        MISS_CRIT+=("$b")
    fi
done

# ─── Summary ─────────────────────────────────────────────────────────
echo ""
echo -e "${MGN}╔══════════════════════════════════════════════════════════════════╗${RST}"

if [ ${#MISS_CRIT[@]} -gt 0 ]; then
    echo -e "${MGN}║${RST}  ${RED}[!] Missing critical: ${MISS_CRIT[*]}${RST}"
    echo -e "${MGN}║${RST}  ${YLW}Run: apt-get install aircrack-ng mdk4${RST}"
    echo -e "${MGN}╠══════════════════════════════════════════════════════════════════╣${RST}"
else
    echo -e "${MGN}║${RST}             ${GRN}✓ ALL CRITICAL TOOLS VERIFIED${RST}                     ${MGN}║${RST}"
    echo -e "${MGN}╠══════════════════════════════════════════════════════════════════╣${RST}"
fi

echo -e "${MGN}║${RST}                                                                  ${MGN}║${RST}"
echo -e "${MGN}║${RST}  ${GRN}Run from anywhere:${RST}  ${WHT}sudo netstrike${RST}                           ${MGN}║${RST}"
echo -e "${MGN}║${RST}  ${GRN}Session results:${RST}    ${WHT}${SESSION_DIR}/${RST}                    ${MGN}║${RST}"
echo -e "${MGN}║${RST}  ${GRN}Installed at:${RST}       ${WHT}${INSTALL_DIR}/${RST}              ${MGN}║${RST}"
echo -e "${MGN}║${RST}  ${GRN}Uninstall:${RST}          ${WHT}bash ${INSTALL_DIR}/uninstall.sh${RST}  ${MGN}║${RST}"
echo -e "${MGN}║${RST}                                                                  ${MGN}║${RST}"
echo -e "${MGN}╚══════════════════════════════════════════════════════════════════╝${RST}"
echo ""
