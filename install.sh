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

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install package with timeout
install_package() {
    local package=$1
    if dpkg -l | grep -q "^ii  $package "; then
        echo -e "${GREEN}[✓] $package ALREADY INSTALLED${NC}"
        return 0
    fi
    
    echo -e "${YELLOW}[!] INSTALLING $package...${NC}"
    timeout 300 apt install -y "$package" > /dev/null 2>&1
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}[✓] $package INSTALLED${NC}"
        return 0
    else
        echo -e "${RED}[✘] $package INSTALLATION FAILED${NC}"
        return 1
    fi
}

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                                                                  ║"
echo "║                   NETSTRIKE FRAMEWORK INSTALLER                  ║"
echo "║                         ULTIMATE EDITION                         ║"
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

# Install essential dependencies
echo -e "${YELLOW}[!] INSTALLING ESSENTIAL DEPENDENCIES...${NC}"
essential_deps=("git" "build-essential" "libssl-dev" "zlib1g-dev" "libpcap-dev")
for dep in "${essential_deps[@]}"; do
    install_package "$dep"
done

# Install Python3 if not present
if ! command_exists python3; then
    echo -e "${YELLOW}[!] INSTALLING PYTHON3...${NC}"
    install_package "python3"
fi

# Install pip if not present
if ! command_exists pip3; then
    echo -e "${YELLOW}[!] INSTALLING PYTHON3-PIP...${NC}"
    install_package "python3-pip"
fi

# Install core WiFi tools
echo -e "${YELLOW}[!] INSTALLING CORE WI-FI TOOLS...${NC}"
core_tools=("aircrack-ng" "macchanger" "wireless-tools" "iw" "iproute2" "net-tools")
for tool in "${core_tools[@]}"; do
    install_package "$tool"
done

# Install WPS tools (reaver and bully instead of wash)
echo -e "${YELLOW}[!] INSTALLING WPS ATTACK TOOLS...${NC}"
wps_tools=("reaver" "bully")
for tool in "${wps_tools[@]}"; do
    if ! install_package "$tool"; then
        echo -e "${YELLOW}[!] ATTEMPTING TO INSTALL $tool FROM SOURCE...${NC}"
        
        if [ "$tool" == "reaver" ]; then
            # Install reaver from source
            git clone https://github.com/t6x/reaver-wps-fork-t6x.git > /dev/null 2>&1
            if [ $? -eq 0 ]; then
                cd reaver-wps-fork-t6x/src
                ./configure > /dev/null 2>&1
                make > /dev/null 2>&1
                make install > /dev/null 2>&1
                cd ../..
                rm -rf reaver-wps-fork-t6x
                echo -e "${GREEN}[✓] REAVER INSTALLED FROM SOURCE${NC}"
            fi
        elif [ "$tool" == "bully" ]; then
            # Install bully from source
            git clone https://github.com/aanarchyy/bully.git > /dev/null 2>&1
            if [ $? -eq 0 ]; then
                cd bully/src
                make > /dev/null 2>&1
                make install > /dev/null 2>&1
                cd ../..
                rm -rf bully
                echo -e "${GREEN}[✓] BULLY INSTALLED FROM SOURCE${NC}"
            fi
        fi
    fi
done

# Install advanced tools
echo -e "${YELLOW}[!] INSTALLING ADVANCED TOOLS...${NC}"
advanced_tools=("hashcat" "hostapd" "dnsmasq")
for tool in "${advanced_tools[@]}"; do
    install_package "$tool"
done

# Install Bluetooth tools
echo -e "${YELLOW}[!] INSTALLING BLUETOOTH TOOLS...${NC}"
bt_tools=("bluetooth" "bluez" "blueman" "hcitool" "l2ping" "bluetoothctl")
for tool in "${bt_tools[@]}"; do
    install_package "$tool"
done

# Install Python packages
echo -e "${YELLOW}[!] INSTALLING PYTHON PACKAGES...${NC}"
pip_packages=("requests" "scapy")
for package in "${pip_packages[@]}"; do
    echo -e "${YELLOW}[!] INSTALLING $package...${NC}"
    if pip3 install "$package" > /dev/null 2>&1; then
        echo -e "${GREEN}[✓] $package INSTALLED${NC}"
    else
        # Try with break-system-packages
        pip3 install "$package" --break-system-packages > /dev/null 2>&1
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}[✓] $package INSTALLED${NC}"
        else
            echo -e "${RED}[✘] $package INSTALLATION FAILED${NC}"
        fi
    fi
done

# Install MDK4
if ! command_exists mdk4; then
    echo -e "${YELLOW}[!] INSTALLING MDK4...${NC}"
    if install_package "mdk4"; then
        echo -e "${GREEN}[✓] MDK4 INSTALLED${NC}"
    else
        # Install from source
        git clone https://github.com/aircrack-ng/mdk4 > /dev/null 2>&1
        if [ $? -eq 0 ]; then
            cd mdk4
            make > /dev/null 2>&1
            make install > /dev/null 2>&1
            cd ..
            rm -rf mdk4
            echo -e "${GREEN}[✓] MDK4 INSTALLED FROM SOURCE${NC}"
        else
            echo -e "${RED}[✘] MDK4 INSTALLATION FAILED${NC}"
        fi
    fi
else
    echo -e "${GREEN}[✓] MDK4 ALREADY INSTALLED${NC}"
fi

# Install hcxtools from source
if ! command_exists hcxdumptool; then
    echo -e "${YELLOW}[!] INSTALLING HCXTOOLS...${NC}"
    git clone https://github.com/ZerBea/hcxtools.git > /dev/null 2>&1
    git clone https://github.com/ZerBea/hcxdumptool.git > /dev/null 2>&1
    
    if [ -d "hcxtools" ]; then
        cd hcxtools
        make > /dev/null 2>&1
        make install > /dev/null 2>&1
        cd ..
        rm -rf hcxtools
    fi
    
    if [ -d "hcxdumptool" ]; then
        cd hcxdumptool
        make > /dev/null 2>&1
        make install > /dev/null 2>&1
        cd ..
        rm -rf hcxdumptool
    fi
    
    if command_exists hcxdumptool; then
        echo -e "${GREEN}[✓] HCXTOOLS INSTALLED${NC}"
    else
        echo -e "${RED}[✘] HCXTOOLS INSTALLATION FAILED${NC}"
    fi
else
    echo -e "${GREEN}[✓] HCXTOOLS ALREADY INSTALLED${NC}"
fi

# Download wordlists
echo -e "${YELLOW}[!] DOWNLOADING WORDLISTS...${NC}"
mkdir -p /usr/share/wordlists

# Download rockyou wordlist
if [ ! -f "/usr/share/wordlists/rockyou.txt" ]; then
    if wget -q https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt.gz -O /tmp/rockyou.txt.gz; then
        gzip -dc /tmp/rockyou.txt.gz > /usr/share/wordlists/rockyou.txt
        rm /tmp/rockyou.txt.gz
        echo -e "${GREEN}[✓] ROCKYOU WORDLIST DOWNLOADED${NC}"
    else
        # Create basic wordlist
        echo -e "${YELLOW}[!] CREATING BASIC WORDLIST...${NC}"
        cat > /usr/share/wordlists/basic_passwords.txt << EOF
123456
password
12345678
qwerty
123456789
12345
1234
111111
1234567
dragon
123123
baseball
abc123
football
monkey
letmein
696969
shadow
master
666666
EOF
        echo -e "${GREEN}[✓] BASIC WORDLIST CREATED${NC}"
    fi
else
    echo -e "${GREEN}[✓] ROCKYOU WORDLIST ALREADY EXISTS${NC}"
fi

# Make Python files executable
echo -e "${YELLOW}[!] SETTING UP NETSTRIKE FILES...${NC}"
chmod +x *.py
echo -e "${GREEN}[✓] EXECUTION PERMISSIONS SET${NC}"

echo -e "${GREEN}[✓] NETSTRIKE FRAMEWORK DEPLOYMENT COMPLETED!${NC}"
echo ""
echo -e "${CYAN}[💡] TO START: sudo python3 netstrike.py${NC}"
echo -e "${YELLOW}[⚠️] IMPORTANT: Use only for authorized testing!${NC}"
