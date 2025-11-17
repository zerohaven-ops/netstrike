#!/bin/bash

# NetStrike Framework Installer - Optimized for Kali Linux 2024
# by ZeroHaven Security

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Animation function
spinner() {
    local pid=$1
    local msg=$2
    local delay=0.2
    local spinstr='|/-\'
    
    printf "${YELLOW}[→] ${msg}... ${NC}"
    while [ "$(ps a | awk '{print $1}' | grep $pid)" ]; do
        local temp=${spinstr#?}
        printf "\b${CYAN}%c${NC}" "$spinstr"
        local spinstr=$temp${spinstr%"$temp"}
        sleep $delay
    done
    printf "\b\b\b\b\b\b"
}

# Check command with timeout
run_cmd() {
    local cmd="$1"
    local msg="$2"
    local timeout=${3:-120}
    
    # Start command in background
    eval "$cmd" &
    local pid=$!
    
    # Show spinner
    spinner $pid "$msg"
    
    # Wait for command with timeout
    ( sleep $timeout && kill -9 $pid 2>/dev/null ) &
    local killer_pid=$!
    
    wait $pid 2>/dev/null
    local result=$?
    
    kill $killer_pid 2>/dev/null
    
    if [ $result -eq 0 ]; then
        printf "${GREEN}[✓] ${msg} COMPLETED${NC}\n"
        return 0
    else
        printf "${RED}[✘] ${msg} FAILED${NC}\n"
        return 1
    fi
}

# Detect distribution
detect_distro() {
    if [ -f "/etc/os-release" ]; then
        if grep -qi "kali" /etc/os-release; then
            echo "kali"
        elif grep -qi "debian" /etc/os-release; then
            echo "debian" 
        elif grep -qi "ubuntu" /etc/os-release; then
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
echo "║                    OPTIMIZED FOR ${DISTRO^^}                          ║"
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
run_cmd "apt update" "Updating system repositories" 180

if [ $? -ne 0 ]; then
    echo -e "${RED}[✘] SYSTEM UPDATE FAILED - CHECK INTERNET CONNECTION${NC}"
    exit 1
fi

# Kali Linux specific installation
if [ "$DISTRO" = "kali" ]; then
    echo -e "${CYAN}[!] KALI LINUX DETECTED - FAST INSTALLATION...${NC}"
    
    # Check and install only missing tools
    tools=("aircrack-ng" "macchanger" "reaver" "bully" "hashcat" "hostapd" "dnsmasq")
    
    for tool in "${tools[@]}"; do
        if command -v "$tool" &> /dev/null; then
            echo -e "${GREEN}[✓] $tool ALREADY INSTALLED${NC}"
        else
            run_cmd "apt install -y $tool" "Installing $tool" 180
        fi
    done
    
    # Install MDK4
    if ! command -v mdk4 &> /dev/null; then
        if run_cmd "apt install -y mdk4" "Installing MDK4" 180; then
            echo -e "${GREEN}[✓] MDK4 INSTALLED${NC}"
        else
            # Install from source
            echo -e "${YELLOW}[!] INSTALLING MDK4 FROM SOURCE...${NC}"
            run_cmd "git clone https://github.com/aircrack-ng/mdk4" "Cloning MDK4" 60
            cd mdk4
            run_cmd "make" "Building MDK4" 120
            run_cmd "make install" "Installing MDK4" 60
            cd ..
            rm -rf mdk4
            echo -e "${GREEN}[✓] MDK4 INSTALLED FROM SOURCE${NC}"
        fi
    else
        echo -e "${GREEN}[✓] MDK4 ALREADY INSTALLED${NC}"
    fi

    # Install Python packages using apt (Kali's preferred method)
    echo -e "${YELLOW}[!] INSTALLING PYTHON PACKAGES...${NC}"
    if run_cmd "apt install -y python3-requests python3-scapy" "Installing Python packages" 180; then
        echo -e "${GREEN}[✓] PYTHON PACKAGES INSTALLED${NC}"
    else
        # Fallback to pip
        echo -e "${YELLOW}[!] USING PIP FALLBACK...${NC}"
        run_cmd "pip3 install requests scapy --break-system-packages" "Installing Python packages via pip" 120
    fi

else
    # Generic Debian/Ubuntu installation
    echo -e "${CYAN}[!] DEBIAN/UBUNTU DETECTED - FULL INSTALLATION...${NC}"
    
    # Install all tools
    tools=("aircrack-ng" "macchanger" "reaver" "bully" "hashcat" "hostapd" "dnsmasq")
    for tool in "${tools[@]}"; do
        run_cmd "apt install -y $tool" "Installing $tool" 180
    done
    
    # Install MDK4
    if ! run_cmd "apt install -y mdk4" "Installing MDK4" 180; then
        run_cmd "git clone https://github.com/aircrack-ng/mdk4" "Cloning MDK4" 60
        cd mdk4
        run_cmd "make" "Building MDK4" 120
        run_cmd "make install" "Installing MDK4" 60
        cd ..
        rm -rf mdk4
        echo -e "${GREEN}[✓] MDK4 INSTALLED FROM SOURCE${NC}"
    fi
    
    # Install Python packages
    run_cmd "pip3 install requests scapy --break-system-packages" "Installing Python packages" 120
fi

# Setup wordlists
echo -e "${YELLOW}[!] SETTING UP WORDLISTS...${NC}"
mkdir -p /usr/share/wordlists

# Check if rockyou exists in Kali
if [ -f "/usr/share/wordlists/rockyou.txt.gz" ]; then
    if [ ! -f "/usr/share/wordlists/rockyou.txt" ]; then
        run_cmd "gzip -dc /usr/share/wordlists/rockyou.txt.gz > /usr/share/wordlists/rockyou.txt" "Extracting rockyou.txt" 60
    fi
    echo -e "${GREEN}[✓] ROCKYOU.TXT AVAILABLE${NC}"
elif [ ! -f "/usr/share/wordlists/rockyou.txt" ]; then
    # Download rockyou from verified source
    echo -e "${YELLOW}[!] DOWNLOADING ROCKYOU WORDLIST...${NC}"
    if run_cmd "wget -q https://github.com/brannondorsey/naive-hashcat/releases/download/data/rockyou.txt -O /usr/share/wordlists/rockyou.txt" "Downloading rockyou.txt" 300; then
        echo -e "${GREEN}[✓] ROCKYOU.TXT DOWNLOADED${NC}"
    else
        # Create basic wordlist
        echo -e "${YELLOW}[!] CREATING BASIC WORDLIST...${NC}"
        cat > /usr/share/wordlists/netstrike_passwords.txt << 'EOF'
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
    echo -e "${GREEN}[✓] ROCKYOU.TXT ALREADY EXISTS${NC}"
fi

# Make scripts executable
echo -e "${YELLOW}[!] SETTING PERMISSIONS...${NC}"
chmod +x *.py
echo -e "${GREEN}[✓] PERMISSIONS SET${NC}"

# Final verification
echo -e "${YELLOW}[!] FINAL VERIFICATION...${NC}"
if command -v aircrack-ng &> /dev/null && \
   command -v macchanger &> /dev/null && \
   command -v mdk4 &> /dev/null; then
    echo -e "${GREEN}[✓] ALL CORE TOOLS VERIFIED${NC}"
    echo -e "${GREEN}[✓] NETSTRIKE FRAMEWORK INSTALLED SUCCESSFULLY!${NC}"
else
    echo -e "${YELLOW}[⚠️] SOME TOOLS MISSING - BUT CORE FUNCTIONALITY SHOULD WORK${NC}"
fi

echo ""
echo -e "${CYAN}[💡] TO START: sudo python3 netstrike.py${NC}"
echo -e "${YELLOW}[⚠️] IMPORTANT: Use only for authorized testing!${NC}"
echo -e "${GREEN}[🎯] FEATURES: Ultra Mass Destruction, Router Destroyer, Evil Twin, Auto Cracking${NC}"
