#!/bin/bash

# NetStrike Framework Installer - Kali Linux Optimized
# by ZeroHaven Security

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Detect distribution
detect_distro() {
    if [ -f "/etc/os-release" ]; then
        if grep -q "Kali" /etc/os-release; then
            echo "kali"
        elif grep -q "Debian" /etc/os-release; then
            echo "debian" 
        elif grep -q "Ubuntu" /etc/os-release; then
            echo "ubuntu"
        else
            echo "unknown"
        fi
    else
        echo "unknown"
    fi
}

DISTRO=$(detect_distro)

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                                                                  ║"
echo "║                   NETSTRIKE FRAMEWORK INSTALLER                  ║"
echo "║                         KALI LINUX EDITION                       ║"
echo "║                         DETECTED: ${DISTRO^^}                             ║"
echo "║                                                                  ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}[✘] PLEASE RUN AS ROOT: sudo ./install.sh${NC}"
    exit 1
fi

echo -e "${YELLOW}[!] STARTING NETSTRIKE INSTALLATION FOR ${DISTRO^^}...${NC}"

# Update system
echo -e "${YELLOW}[!] UPDATING SYSTEM...${NC}"
if [ "$DISTRO" = "kali" ]; then
    apt update
else
    apt-get update
fi

if [ $? -eq 0 ]; then
    echo -e "${GREEN}[✓] SYSTEM UPDATED${NC}"
else
    echo -e "${RED}[✘] UPDATE FAILED${NC}"
    exit 1
fi

# Function to check and install tool
install_tool() {
    local tool=$1
    if command -v "$tool" &> /dev/null; then
        echo -e "${GREEN}[✓] $tool ALREADY INSTALLED${NC}"
        return 0
    fi
    
    echo -e "${YELLOW}[!] INSTALLING $tool...${NC}"
    
    if [ "$DISTRO" = "kali" ]; then
        apt install -y "$tool"
    else
        apt-get install -y "$tool"
    fi
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}[✓] $tool INSTALLED${NC}"
        return 0
    else
        echo -e "${RED}[✘] $tool INSTALLATION FAILED${NC}"
        return 1
    fi
}

# Kali Linux specific installation
if [ "$DISTRO" = "kali" ]; then
    echo -e "${CYAN}[!] KALI LINUX DETECTED - OPTIMIZING INSTALLATION...${NC}"
    
    # Kali has most tools pre-installed, just check and install missing ones
    tools_to_check=("aircrack-ng" "macchanger" "reaver" "bully" "hashcat" "hostapd" "dnsmasq")
    
    for tool in "${tools_to_check[@]}"; do
        install_tool "$tool"
    done
    
    # Install MDK4 if not present
    if ! command -v mdk4 &> /dev/null; then
        echo -e "${YELLOW}[!] INSTALLING MDK4...${NC}"
        if apt install -y mdk4; then
            echo -e "${GREEN}[✓] MDK4 INSTALLED${NC}"
        else
            # Install from source
            git clone https://github.com/aircrack-ng/mdk4
            cd mdk4
            make && make install
            cd ..
            rm -rf mdk4
            echo -e "${GREEN}[✓] MDK4 INSTALLED FROM SOURCE${NC}"
        fi
    else
        echo -e "${GREEN}[✓] MDK4 ALREADY INSTALLED${NC}"
    fi

else
    # Generic Debian/Ubuntu installation
    echo -e "${CYAN}[!] DEBIAN/UBUNTU DETECTED - FULL INSTALLATION...${NC}"
    
    # Install all tools
    core_tools=("aircrack-ng" "macchanger" "reaver" "bully" "hashcat" "hostapd" "dnsmasq")
    for tool in "${core_tools[@]}"; do
        install_tool "$tool"
    done
    
    # Install MDK4
    if ! install_tool "mdk4"; then
        git clone https://github.com/aircrack-ng/mdk4
        cd mdk4
        make && make install
        cd ..
        rm -rf mdk4
        echo -e "${GREEN}[✓] MDK4 INSTALLED FROM SOURCE${NC}"
    fi
fi

# Install Python packages
echo -e "${YELLOW}[!] INSTALLING PYTHON PACKAGES...${NC}"
pip3 install requests scapy

if [ $? -eq 0 ]; then
    echo -e "${GREEN}[✓] PYTHON PACKAGES INSTALLED${NC}"
else
    # Try with user install
    pip3 install requests scapy --user
    echo -e "${GREEN}[✓] PYTHON PACKAGES INSTALLED FOR USER${NC}"
fi

# Setup wordlists
echo -e "${YELLOW}[!] SETTING UP WORDLISTS...${NC}"
mkdir -p /usr/share/wordlists

# Check if rockyou exists in Kali
if [ -f "/usr/share/wordlists/rockyou.txt.gz" ]; then
    if [ ! -f "/usr/share/wordlists/rockyou.txt" ]; then
        gzip -dc /usr/share/wordlists/rockyou.txt.gz > /usr/share/wordlists/rockyou.txt
        echo -e "${GREEN}[✓] ROCKYOU.TXT EXTRACTED${NC}"
    else
        echo -e "${GREEN}[✓] ROCKYOU.TXT ALREADY EXISTS${NC}"
    fi
elif [ ! -f "/usr/share/wordlists/rockyou.txt" ]; then
    # Download rockyou
    echo -e "${YELLOW}[!] DOWNLOADING ROCKYOU WORDLIST...${NC}"
    wget -q https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt -O /usr/share/wordlists/rockyou.txt
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}[✓] ROCKYOU.TXT DOWNLOADED${NC}"
    else
        # Create basic wordlist
        echo -e "${YELLOW}[!] CREATING BASIC WORDLIST...${NC}"
        cat > /usr/share/wordlists/basic_passwords.txt << 'EOF'
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
fi

# Make scripts executable
echo -e "${YELLOW}[!] SETTING PERMISSIONS...${NC}"
chmod +x *.py
echo -e "${GREEN}[✓] PERMISSIONS SET${NC}"

# Verification
echo -e "${YELLOW}[!] VERIFYING INSTALLATION...${NC}"
if command -v aircrack-ng && command -v macchanger && command -v mdk4; then
    echo -e "${GREEN}[✓] CORE TOOLS VERIFIED${NC}"
    echo -e "${GREEN}[✓] NETSTRIKE FRAMEWORK INSTALLED SUCCESSFULLY!${NC}"
else
    echo -e "${RED}[✘] SOME TOOLS MISSING - BUT CORE FUNCTIONALITY SHOULD WORK${NC}"
fi

echo ""
echo -e "${CYAN}[💡] TO START: sudo python3 netstrike.py${NC}"
echo -e "${YELLOW}[⚠️] IMPORTANT: Use only for authorized testing!${NC}"
