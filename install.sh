#!/bin/bash

# NetStrike Framework Installer
# by ZeroHaven Security

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Animation function
show_animation() {
    local frames=("▰▰▰▰▰▰▰▰" "▰▰▰▰▰▰▰▱" "▰▰▰▰▰▰▱▱" "▰▰▰▰▰▱▱▱" "▰▰▰▰▱▱▱▱" "▰▰▰▱▱▱▱▱" "▰▰▱▱▱▱▱▱" "▰▱▱▱▱▱▱▱" "▱▱▱▱▱▱▱▱")
    for frame in "${frames[@]}"; do
        echo -ne "\r${CYAN}[${frame}] ${YELLOW}DEPLOYING NETSTRIKE...${NC}"
        sleep 0.1
    done
    echo -ne "\r${GREEN}[▰▰▰▰▰▰▰▰] ${GREEN}DEPLOYMENT COMPLETE!${NC}\n"
}

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
echo "║                  ADVANCED DEPLOYMENT SYSTEM                      ║"
echo "║                                                                  ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}[✘] PLEASE RUN AS ROOT: sudo ./install.sh${NC}"
    exit 1
fi

echo -e "${YELLOW}[!] STARTING NETSTRIKE FRAMEWORK DEPLOYMENT...${NC}"

# Update system
echo -e "${YELLOW}[!] UPDATING SYSTEM REPOSITORIES...${NC}"
apt update > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}[✓] SYSTEM UPDATED${NC}"
else
    echo -e "${RED}[✘] UPDATE FAILED - CHECK INTERNET CONNECTION${NC}"
    exit 1
fi

# Install Python3 if not present
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}[!] INSTALLING PYTHON3...${NC}"
    apt install -y python3 > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}[✓] PYTHON3 INSTALLED${NC}"
    else
        echo -e "${RED}[✘] PYTHON3 INSTALLATION FAILED${NC}"
    fi
fi

# Install pip if not present
if ! command -v pip3 &> /dev/null; then
    echo -e "${YELLOW}[!] INSTALLING PYTHON3-PIP...${NC}"
    apt install -y python3-pip > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}[✓] PYTHON3-PIP INSTALLED${NC}"
    else
        echo -e "${RED}[✘] PIP INSTALLATION FAILED${NC}"
    fi
fi

# Install required tools
echo -e "${YELLOW}[!] INSTALLING REQUIRED TOOLS...${NC}"

# WiFi tools
wifi_tools=("aircrack-ng" "macchanger" "xterm" "reaver" "bully" "wash" "wireless-tools" "hostapd" "dnsmasq")
for tool in "${wifi_tools[@]}"; do
    if ! dpkg -l | grep -q $tool; then
        echo -e "${YELLOW}[!] INSTALLING $tool...${NC}"
        apt install -y $tool > /dev/null 2>&1
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}[✓] $tool INSTALLED${NC}"
        else
            echo -e "${RED}[✘] $tool INSTALLATION FAILED${NC}"
        fi
    else
        echo -e "${GREEN}[✓] $tool ALREADY INSTALLED${NC}"
    fi
done

# Advanced cracking tools
advanced_tools=("hashcat" "hcxdumptool" "hcxtools")
for tool in "${advanced_tools[@]}"; do
    if ! dpkg -l | grep -q $tool; then
        echo -e "${YELLOW}[!] INSTALLING $tool...${NC}"
        apt install -y $tool > /dev/null 2>&1
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}[✓] $tool INSTALLED${NC}"
        else
            echo -e "${RED}[✘] $tool INSTALLATION FAILED${NC}"
        fi
    else
        echo -e "${GREEN}[✓] $tool ALREADY INSTALLED${NC}"
    fi
done

# Bluetooth tools
bt_tools=("bluetooth" "bluez" "blueman" "hcitool" "l2ping" "bluetoothctl")
for tool in "${bt_tools[@]}"; do
    if ! dpkg -l | grep -q $tool; then
        echo -e "${YELLOW}[!] INSTALLING $tool...${NC}"
        apt install -y $tool > /dev/null 2>&1
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}[✓] $tool INSTALLED${NC}"
        else
            echo -e "${RED}[✘] $tool INSTALLATION FAILED${NC}"
        fi
    else
        echo -e "${GREEN}[✓] $tool ALREADY INSTALLED${NC}"
    fi
done

# Python packages
echo -e "${YELLOW}[!] INSTALLING PYTHON PACKAGES...${NC}"
pip3 install requests scapy > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}[✓] PYTHON PACKAGES INSTALLED${NC}"
else
    echo -e "${RED}[✘] PYTHON PACKAGES INSTALLATION FAILED${NC}"
fi

# Make Python files executable
echo -e "${YELLOW}[!] SETTING UP NETSTRIKE FILES...${NC}"
chmod +x *.py
if [ $? -eq 0 ]; then
    echo -e "${GREEN}[✓] EXECUTION PERMISSIONS SET${NC}"
else
    echo -e "${RED}[✘] PERMISSION SETTING FAILED${NC}"
fi

# Install MDK4 if not present
if ! command -v mdk4 &> /dev/null; then
    echo -e "${YELLOW}[!] INSTALLING MDK4...${NC}"
    git clone https://github.com/aircrack-ng/mdk4 > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        cd mdk4
        make > /dev/null 2>&1
        make install > /dev/null 2>&1
        cd ..
        rm -rf mdk4
        echo -e "${GREEN}[✓] MDK4 INSTALLED${NC}"
    else
        echo -e "${RED}[✘] MDK4 INSTALLATION FAILED${NC}"
        echo -e "${YELLOW}[!] TRYING PACKAGE INSTALLATION...${NC}"
        apt install -y mdk4 > /dev/null 2>&1
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}[✓] MDK4 INSTALLED VIA PACKAGE${NC}"
        else
            echo -e "${RED}[✘] MDK4 INSTALLATION COMPLETELY FAILED${NC}"
        fi
    fi
else
    echo -e "${GREEN}[✓] MDK4 ALREADY INSTALLED${NC}"
fi

# Download wordlists
echo -e "${YELLOW}[!] DOWNLOADING ENHANCED WORDLISTS...${NC}"
mkdir -p /usr/share/wordlists
if [ ! -f "/usr/share/wordlists/rockyou.txt" ]; then
    wget -q https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt -O /usr/share/wordlists/rockyou.txt
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}[✓] ROCKYOU WORDLIST DOWNLOADED${NC}"
    else
        echo -e "${RED}[✘] ROCKYOU DOWNLOAD FAILED${NC}"
    fi
else
    echo -e "${GREEN}[✓] ROCKYOU WORDLIST ALREADY EXISTS${NC}"
fi

# Show completion animation
show_animation

echo -e "${GREEN}[✓] NETSTRIKE FRAMEWORK DEPLOYMENT COMPLETED SUCCESSFULLY!${NC}"
echo ""
echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                     QUICK START GUIDE                          ║${NC}"
echo -e "${BLUE}╠══════════════════════════════════════════════════════════════════╣${NC}"
echo -e "${BLUE}║                                                                  ║${NC}"
echo -e "${BLUE}║  ${CYAN}TO START NETSTRIKE:${BLUE}                                            ║${NC}"
echo -e "${BLUE}║    ${GREEN}sudo python3 netstrike.py${BLUE}                                   ║${NC}"
echo -e "${BLUE}║                                                                  ║${NC}"
echo -e "${BLUE}║  ${CYAN}NEW FEATURES:${BLUE}                                                 ║${NC}"
echo -e "${BLUE}║    ${GREEN}• Auto Password Cracking${BLUE} - Tries all methods automatically  ║${NC}"
echo -e "${BLUE}║    ${GREEN}• Evil Twin Attack${BLUE} - Rogue access point creation           ║${NC}"
echo -e "${BLUE}║    ${GREEN}• PMKID Attacks${BLUE} - New attack vector without handshake     ║${NC}"
echo -e "${BLUE}║    ${GREEN}• Enhanced Bluetooth${BLUE} - Better scanning & attacks          ║${NC}"
echo -e "${BLUE}║    ${GREEN}• Mass Destruction${BLUE} - Improved network annihilation        ║${NC}"
echo -e "${BLUE}║                                                                  ║${NC}"
echo -e "${BLUE}║  ${CYAN}IMPORTANT:${BLUE}                                                     ║${NC}"
echo -e "${BLUE}║  ${YELLOW}• Use only for authorized security testing${BLUE}                     ║${NC}"
echo -e "${BLUE}║  ${YELLOW}• Test only on networks you own${BLUE}                                ║${NC}"
echo -e "${BLUE}║  ${YELLOW}• Follow all applicable laws${BLUE}                                  ║${NC}"
echo -e "${BLUE}║                                                                  ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${CYAN}[💡] TIP: Run 'sudo python3 netstrike.py' to launch the framework${NC}"
