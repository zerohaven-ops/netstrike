#!/bin/bash

# NetStrike Framework Installer
# by ZeroHaven Security

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                                                                  ║"
echo "║    ███╗   ██╗███████╗████████╗███████╗████████╗██████╗ ██╗██╗   ║"
echo "║    ████╗  ██║██╔════╝╚══██╔══╝██╔════╝╚══██╔══╝██╔══██╗██║██║   ║"
echo "║    ██╔██╗ ██║█████╗     ██║   █████╗     ██║   ██████╔╝██║██║   ║"
echo "║    ██║╚██╗██║██╔══╝     ██║   ██╔══╝     ██║   ██╔══██╗██║██║   ║"
echo "║    ██║ ╚████║███████╗   ██║   ███████╗   ██║   ██║  ██║██║███████╗"
echo "║    ╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝╚══════╝"
echo "║                                                                  ║"
echo "║                   INSTALLATION SCRIPT v2.0                       ║"
echo "║                                                                  ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}[✘] Please run as root: sudo ./install.sh${NC}"
    exit 1
fi

echo -e "${YELLOW}[!] Starting NetStrike Framework Installation...${NC}"

# Update system
echo -e "${YELLOW}[!] Updating system packages...${NC}"
apt update > /dev/null 2>&1

# Install Python3 if not present
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}[!] Installing Python3...${NC}"
    apt install -y python3 > /dev/null 2>&1
    echo -e "${GREEN}[✓] Python3 installed${NC}"
fi

# Install required tools
echo -e "${YELLOW}[!] Installing required tools...${NC}"

# WiFi tools
wifi_tools=("aircrack-ng" "macchanger" "xterm" "reaver" "bully" "wash" "wireless-tools")
for tool in "${wifi_tools[@]}"; do
    if ! dpkg -l | grep -q $tool; then
        echo -e "${YELLOW}[!] Installing $tool...${NC}"
        apt install -y $tool > /dev/null 2>&1
        echo -e "${GREEN}[✓] $tool installed${NC}"
    fi
done

# Bluetooth tools
bt_tools=("bluetooth" "bluez" "blueman" "hcitool" "l2ping")
for tool in "${bt_tools[@]}"; do
    if ! dpkg -l | grep -q $tool; then
        echo -e "${YELLOW}[!] Installing $tool...${NC}"
        apt install -y $tool > /dev/null 2>&1
        echo -e "${GREEN}[✓] $tool installed${NC}"
    fi
done

# Make Python files executable
echo -e "${YELLOW}[!] Setting up NetStrike files...${NC}"
chmod +x *.py

# Install MDK4 if not present
if ! command -v mdk4 &> /dev/null; then
    echo -e "${YELLOW}[!] Installing MDK4...${NC}"
    git clone https://github.com/aircrack-ng/mdk4 > /dev/null 2>&1
    cd mdk4
    make > /dev/null 2>&1
    make install > /dev/null 2>&1
    cd ..
    rm -rf mdk4
    echo -e "${GREEN}[✓] MDK4 installed${NC}"
fi

echo -e "${GREEN}[✓] Installation completed successfully!${NC}"
echo ""
echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                     QUICK START GUIDE                          ║${NC}"
echo -e "${BLUE}╠══════════════════════════════════════════════════════════════════╣${NC}"
echo -e "${BLUE}║                                                                  ║${NC}"
echo -e "${BLUE}║  To start NetStrike:                                            ║${NC}"
echo -e "${BLUE}║    ${GREEN}sudo python3 netstrike.py${BLUE}                                   ║${NC}"
echo -e "${BLUE}║                                                                  ║${NC}"
echo -e "${BLUE}║  Important:                                                     ║${NC}"
echo -e "${BLUE}║  • Use only for authorized security testing                     ║${NC}"
echo -e "${BLUE}║  • Test only on networks you own                                ║${NC}"
echo -e "${BLUE}║  • Follow all applicable laws                                   ║${NC}"
echo -e "${BLUE}║                                                                  ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════╝${NC}"
echo ""
