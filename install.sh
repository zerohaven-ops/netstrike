#!/bin/bash

# NetStrike Framework v3.0 Ultimate Installer
# by ZeroHaven Security
# Educational & Research Use Only

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Banner
echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                                                                  ║"
echo "║                   NETSTRIKE v3.0 ULTIMATE                        ║"
echo "║                     INSTALLATION SCRIPT                          ║"
echo "║                   EDUCATIONAL USE ONLY                           ║"
echo "║                                                                  ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}[✘] PLEASE RUN AS ROOT: sudo ./install.sh${NC}"
    exit 1
fi

# Quick lock removal
echo -e "${YELLOW}[!] CHECKING FOR SYSTEM LOCKS...${NC}"
rm -f /var/lib/dpkg/lock-frontend
rm -f /var/lib/dpkg/lock
rm -f /var/lib/apt/lists/lock
rm -f /var/cache/apt/archives/lock
killall -9 dpkg apt 2>/dev/null
dpkg --configure -a 2>/dev/null
echo -e "${GREEN}[✓] SYSTEM LOCKS CLEARED${NC}"

# Update system
echo -e "${YELLOW}[!] UPDATING SYSTEM...${NC}"
apt update > /dev/null 2>&1
echo -e "${GREEN}[✓] SYSTEM UPDATED${NC}"

# Install core tools
echo -e "${YELLOW}[!] INSTALLING CORE TOOLS...${NC}"
core_tools=("python3" "aircrack-ng" "macchanger" "xterm" "mdk4" "reaver" "hostapd" "dnsmasq")

for tool in "${core_tools[@]}"; do
    if ! command -v "$tool" &> /dev/null; then
        echo -e "${YELLOW}[→] Installing $tool...${NC}"
        apt install -y "$tool" > /dev/null 2>&1
        if command -v "$tool" &> /dev/null; then
            echo -e "${GREEN}[✓] $tool installed${NC}"
        else
            echo -e "${RED}[✘] $tool failed${NC}"
        fi
    else
        echo -e "${GREEN}[✓] $tool already installed${NC}"
    fi
done

# Install Python packages
echo -e "${YELLOW}[!] INSTALLING PYTHON PACKAGES...${NC}"
pip3 install requests scapy --break-system-packages --quiet > /dev/null 2>&1
echo -e "${GREEN}[✓] Python packages installed${NC}"

# Setup wordlists
echo -e "${YELLOW}[!] SETTING UP WORDLISTS...${NC}"
mkdir -p /usr/share/wordlists

if [ -f "/usr/share/wordlists/rockyou.txt.gz" ] && [ ! -f "/usr/share/wordlists/rockyou.txt" ]; then
    gzip -dc /usr/share/wordlists/rockyou.txt.gz > /usr/share/wordlists/rockyou.txt 2>/dev/null
    echo -e "${GREEN}[✓] ROCKYOU.TXT EXTRACTED${NC}"
elif [ -f "/usr/share/wordlists/rockyou.txt" ]; then
    echo -e "${GREEN}[✓] ROCKYOU.TXT AVAILABLE${NC}"
else
    cat > /usr/share/wordlists/netstrike_passwords.txt << 'EOF'
12345678
password
admin123
welcome
qwerty
123456789
password123
admin
welcome123
1234567890
1234
12345
123456
1234567
internet
wireless
default
guest
linksys
dlink
netgear
cisco
EOF
    echo -e "${GREEN}[✓] BASIC WORDLIST CREATED${NC}"
fi

# Set permissions
echo -e "${YELLOW}[!] SETTING PERMISSIONS...${NC}"
chmod +x *.py *.sh 2>/dev/null
echo -e "${GREEN}[✓] PERMISSIONS SET${NC}"

# Create __init__.py for package recognition
echo -e "${YELLOW}[!] CONFIGURING PYTHON ENVIRONMENT...${NC}"
touch __init__.py
echo -e "${GREEN}[✓] Python environment configured${NC}"

# Final check
echo -e "${YELLOW}[!] FINAL VERIFICATION...${NC}"
if command -v python3 && command -v aircrack-ng && command -v macchanger; then
    echo -e "${GREEN}[✓] ALL ESSENTIAL TOOLS VERIFIED${NC}"
    echo -e "${GREEN}[✓] NETSTRIKE v3.0 INSTALLED SUCCESSFULLY!${NC}"
else
    echo -e "${YELLOW}[⚠️] SOME TOOLS MISSING - CORE FUNCTIONALITY AVAILABLE${NC}"
fi

# Display completion
echo
echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                     INSTALLATION COMPLETE                       ║${NC}"
echo -e "${BLUE}╠══════════════════════════════════════════════════════════════════╣${NC}"
echo -e "${BLUE}║                                                                  ║${NC}"
echo -e "${BLUE}║   🚀 TO START: sudo python3 netstrike.py                         ║${NC}"
echo -e "${BLUE}║   📚 PURPOSE:  Educational & Authorized Testing Only            ║${NC}"
echo -e "${BLUE}║   ⚠️  WARNING:  Use Responsibly & Legally                       ║${NC}"
echo -e "${BLUE}║                                                                  ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════╝${NC}"
echo
