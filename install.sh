#!/bin/bash

# NetStrike Framework Installer v3.0
# Enhanced with Smart Lock Handling
# by ZeroHaven Security

# Modern Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Animation function
show_animation() {
    local frames=("⠋" "⠙" "⠹" "⠸" "⠼" "⠴" "⠦" "⠧" "⠇" "⠏")
    local message=$1
    local pid=$2
    local delay=0.1
    
    while kill -0 $pid 2>/dev/null; do
        for frame in "${frames[@]}"; do
            echo -ne "\r${CYAN}[${frame}]${NC} ${message}"
            sleep $delay
        done
    done
    echo -ne "\r${GREEN}[✅]${NC} ${message} completed\n"
}

# Check tool availability
check_tool() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}[✅] $1 available${NC}"
        return 0
    else
        echo -e "${YELLOW}[⚠️] $1 missing${NC}"
        return 1
    fi
}

# Fast installation function
install_tool_fast() {
    local tool=$1
    echo -e "${CYAN}[→] Installing $tool...${NC}"
    
    if command -v $tool &> /dev/null; then
        echo -e "${GREEN}[✅] $tool already installed${NC}"
        return 0
    fi
    
    if [ "$DISTRO" = "kali" ]; then
        apt install -y $tool > /dev/null 2>&1 &
    else
        apt-get install -y $tool > /dev/null 2>&1 &
    fi
    
    local pid=$!
    show_animation "Installing $tool" $pid
    wait $pid
    
    if command -v $tool &> /dev/null; then
        echo -e "${GREEN}[✅] $tool installed successfully${NC}"
        return 0
    else
        echo -e "${YELLOW}[⚠️] $tool installation may have failed${NC}"
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

# Modern Banner
echo -e "${PURPLE}"
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                                                                  ║"
echo "║                   NETSTRIKE FRAMEWORK v3.0                       ║"
echo "║                   ENHANCED INSTALLATION                          ║"
echo "║                         DETECTED: ${DISTRO^^}                          ║"
echo "║                                                                  ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}[✘] Please run as root: sudo ./install.sh${NC}"
    exit 1
fi

echo -e "${CYAN}[→] Starting enhanced installation for ${DISTRO^^}...${NC}"

# Essential tools list
ESSENTIAL_TOOLS=("aircrack-ng" "macchanger" "xterm" "iwconfig")
OPTIONAL_TOOLS=("mdk4" "reaver" "hostapd" "dnsmasq" "hashcat")

# Check available tools first
echo -e "${CYAN}[→] Checking available tools...${NC}"
AVAILABLE_TOOLS=()
MISSING_TOOLS=()

for tool in "${ESSENTIAL_TOOLS[@]}" "${OPTIONAL_TOOLS[@]}"; do
    if check_tool $tool; then
        AVAILABLE_TOOLS+=($tool)
    else
        MISSING_TOOLS+=($tool)
    fi
done

echo -e "${GREEN}[✅] ${#AVAILABLE_TOOLS[@]} tools available${NC}"
echo -e "${YELLOW}[⚠️] ${#MISSING_TOOLS[@]} tools need installation${NC}"

# If all tools available, skip installation
if [ ${#MISSING_TOOLS[@]} -eq 0 ]; then
    echo -e "${GREEN}[✅] All required tools are already installed!${NC}"
else
    # Quick system update
    echo -e "${CYAN}[→] Quick system update...${NC}"
    apt update > /dev/null 2>&1 &
    pid=$!
    show_animation "Updating system" $pid
    wait $pid
    
    # Install missing tools
    echo -e "${CYAN}[→] Installing missing tools...${NC}"
    for tool in "${MISSING_TOOLS[@]}"; do
        install_tool_fast $tool
    done
fi

# Python packages
echo -e "${CYAN}[→] Checking Python packages...${NC}"
if python3 -c "import requests" 2>/dev/null && python3 -c "import scapy" 2>/dev/null; then
    echo -e "${GREEN}[✅] Python packages available${NC}"
else
    echo -e "${CYAN}[→] Installing Python packages...${NC}"
    pip3 install requests scapy --break-system-packages --quiet > /dev/null 2>&1 &
    pid=$!
    show_animation "Installing Python packages" $pid
    wait $pid
    echo -e "${GREEN}[✅] Python packages installed${NC}"
fi

# Setup wordlists
echo -e "${CYAN}[→] Setting up wordlists...${NC}"
mkdir -p /usr/share/wordlists

if [ -f "/usr/share/wordlists/rockyou.txt.gz" ] && [ ! -f "/usr/share/wordlists/rockyou.txt" ]; then
    gzip -dc /usr/share/wordlists/rockyou.txt.gz > /usr/share/wordlists/rockyou.txt 2>/dev/null &
    pid=$!
    show_animation "Extracting rockyou.txt" $pid
    wait $pid
    echo -e "${GREEN}[✅] ROCKYOU.TXT extracted${NC}"
elif [ -f "/usr/share/wordlists/rockyou.txt" ]; then
    echo -e "${GREEN}[✅] ROCKYOU.TXT available${NC}"
else
    # Create basic wordlist
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
admin
welcome
passw0rd
master
hello
EOF
    echo -e "${GREEN}[✅] Basic wordlist created${NC}"
fi

# Set permissions
echo -e "${CYAN}[→] Setting permissions...${NC}"
chmod +x *.py
echo -e "${GREEN}[✅] Permissions set${NC}"

# Final verification
echo -e "${CYAN}[→] Final verification...${NC}"
VERIFIED=true
for tool in "${ESSENTIAL_TOOLS[@]}"; do
    if ! command -v $tool &> /dev/null; then
        echo -e "${RED}[✘] $tool missing${NC}"
        VERIFIED=false
    fi
done

if $VERIFIED; then
    echo -e "${GREEN}[✅] All core tools verified${NC}"
    echo -e "${GREEN}[🎉] NetStrike Framework v3.0 installed successfully!${NC}"
else
    echo -e "${YELLOW}[⚠️] Some tools missing - but core functionality should work${NC}"
fi

# Display completion message
echo ""
echo -e "${PURPLE}╔══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${PURPLE}║                         QUICK START GUIDE                        ║${NC}"
echo -e "${PURPLE}╠══════════════════════════════════════════════════════════════════╣${NC}"
echo -e "${PURPLE}║                                                                  ║${NC}"
echo -e "${PURPLE}║  1. ${CYAN}sudo python3 netstrike.py${PURPLE}                                  ║${NC}"
echo -e "${PURPLE}║  2. ${CYAN}Select your wireless interface${PURPLE}                             ║${NC}"
echo -e "${PURPLE}║  3. ${CYAN}Choose operation from modern menu${PURPLE}                          ║${NC}"
echo -e "${PURPLE}║  4. ${CYAN}Press Ctrl+C to stop any operation${PURPLE}                         ║${NC}"
echo -e "${PURPLE}║                                                                  ║${NC}"
echo -e "${PURPLE}║  ${GREEN}Available Operations:${PURPLE}                                         ║${NC}"
echo -e "${PURPLE}║  ${YELLOW}• Single WiFi Jamming${PURPLE}                                       ║${NC}"
echo -e "${PURPLE}║  ${YELLOW}• Mass WiFi Disruption${PURPLE}                                      ║${NC}"
echo -e "${PURPLE}║  ${YELLOW}• Password Cracking${PURPLE}                                         ║${NC}"
echo -e "${PURPLE}║  ${YELLOW}• Advanced Evil Twin${PURPLE}                                        ║${NC}"
echo -e "${PURPLE}║  ${YELLOW}• Network Scanning${PURPLE}                                          ║${NC}"
echo -e "${PURPLE}║  ${YELLOW}• Router Stress Testing${PURPLE}                                     ║${NC}"
echo -e "${PURPLE}║                                                                  ║${NC}"
echo -e "${PURPLE}╚══════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}[⚠️] IMPORTANT: Use only for authorized testing and educational purposes!${NC}"
echo -e "${GREEN}[🔒] Enhanced Features: Modern UI, Better Attacks, Improved Security${NC}"
echo ""
