#!/bin/bash

# NetStrike Framework Installer - Lock-Aware Minimal Installation
# by ZeroHaven Security

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Check if dpkg is locked
check_dpkg_lock() {
    if [ -f /var/lib/dpkg/lock-frontend ] || [ -f /var/lib/dpkg/lock ] || [ -f /var/lib/apt/lists/lock ]; then
        return 1
    fi
    return 0
}

# Wait for dpkg lock to be released
wait_for_dpkg_lock() {
    local timeout=300
    local start_time=$(date +%s)
    
    echo -e "${YELLOW}[!] CHECKING FOR SYSTEM LOCKS...${NC}"
    
    while [ $(($(date +%s) - start_time)) -lt $timeout ]; do
        if check_dpkg_lock; then
            echo -e "${GREEN}[✓] SYSTEM READY FOR INSTALLATION${NC}"
            return 0
        fi
        local elapsed=$(($(date +%s) - start_time))
        local dots=$(printf '%*s' $((elapsed % 4)) | tr ' ' '.')
        echo -ne "\r${YELLOW}[⌛] WAITING FOR SYSTEM LOCKS${dots} (${elapsed}s)${NC}"
        sleep 2
    done
    
    echo -e "\r${RED}[✘] TIMEOUT WAITING FOR SYSTEM LOCKS AFTER ${timeout}s${NC}"
    return 1
}

# Simple command runner with timeout
run_cmd_simple() {
    local cmd="$1"
    local msg="$2"
    local timeout=${3:-60}
    
    echo -e "${YELLOW}[→] ${msg}...${NC}"
    
    # Check for locks first
    if ! check_dpkg_lock; then
        echo -e "${RED}[✘] ${msg} - SYSTEM LOCKED${NC}"
        return 1
    fi
    
    # Run command with timeout
    if timeout $timeout bash -c "$cmd" > /dev/null 2>&1; then
        echo -e "${GREEN}[✓] ${msg} COMPLETED${NC}"
        return 0
    else
        echo -e "${RED}[✘] ${msg} FAILED${NC}"
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
echo "║                    LOCK-AWARE MINIMAL INSTALL                    ║"
echo "║                         DETECTED: ${DISTRO^^}                          ║"
echo "║                                                                  ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}[✘] PLEASE RUN AS ROOT: sudo ./install.sh${NC}"
    exit 1
fi

echo -e "${YELLOW}[!] STARTING MINIMAL INSTALLATION FOR ${DISTRO^^}...${NC}"

# Wait for system locks first
if ! wait_for_dpkg_lock; then
    echo -e "${RED}[✘] CANNOT PROCEED - SYSTEM LOCKS HELD${NC}"
    echo -e "${YELLOW}[💡] TIP: Wait for other package operations to complete${NC}"
    exit 1
fi

# Update system (quick check only)
echo -e "${YELLOW}[!] CHECKING SYSTEM UPDATES...${NC}"
if run_cmd_simple "apt update" "Checking updates" 30; then
    echo -e "${GREEN}[✓] SYSTEM READY${NC}"
else
    echo -e "${YELLOW}[⚠️] UPDATE CHECK FAILED - CONTINUING ANYWAY${NC}"
fi

# Kali Linux - Minimal installation (skip most tools as they're pre-installed)
if [ "$DISTRO" = "kali" ]; then
    echo -e "${CYAN}[!] KALI DETECTED - MINIMAL INSTALLATION...${NC}"
    
    # Only install MDK4 if missing (usually the only missing tool)
    if ! command -v mdk4 &> /dev/null; then
        echo -e "${YELLOW}[!] INSTALLING MDK4...${NC}"
        if run_cmd_simple "apt install -y mdk4" "Installing MDK4" 120; then
            echo -e "${GREEN}[✓] MDK4 INSTALLED${NC}"
        else
            # Try source installation as fallback
            echo -e "${YELLOW}[!] TRYING MDK4 FROM SOURCE...${NC}"
            run_cmd_simple "git clone https://github.com/aircrack-ng/mdk4" "Cloning MDK4" 60
            cd mdk4 && make && make install && cd .. && rm -rf mdk4
            echo -e "${GREEN}[✓] MDK4 INSTALLED FROM SOURCE${NC}"
        fi
    else
        echo -e "${GREEN}[✓] MDK4 ALREADY INSTALLED${NC}"
    fi

    # Install Python packages via pip (avoid apt locks)
    echo -e "${YELLOW}[!] CHECKING PYTHON PACKAGES...${NC}"
    if python3 -c "import requests" 2>/dev/null && python3 -c "import scapy" 2>/dev/null; then
        echo -e "${GREEN}[✓] PYTHON PACKAGES ALREADY INSTALLED${NC}"
    else
        echo -e "${YELLOW}[!] INSTALLING PYTHON PACKAGES VIA PIP...${NC}"
        run_cmd_simple "pip3 install requests scapy --break-system-packages --quiet" "Installing Python packages" 60
    fi

else
    # Generic installation for other distros
    echo -e "${CYAN}[!] ${DISTRO^^} DETECTED - STANDARD INSTALLATION...${NC}"
    
    # Install core tools
    tools=("aircrack-ng" "macchanger" "reaver" "mdk4")
    for tool in "${tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            run_cmd_simple "apt install -y $tool" "Installing $tool" 120
        else
            echo -e "${GREEN}[✓] $tool ALREADY INSTALLED${NC}"
        fi
    done
    
    # Python packages
    run_cmd_simple "pip3 install requests scapy --break-system-packages --quiet" "Installing Python packages" 60
fi

# Setup wordlists (no downloads - use existing or create basic)
echo -e "${YELLOW}[!] SETTING UP WORDLISTS...${NC}"
mkdir -p /usr/share/wordlists

if [ -f "/usr/share/wordlists/rockyou.txt.gz" ] && [ ! -f "/usr/share/wordlists/rockyou.txt" ]; then
    run_cmd_simple "gzip -dc /usr/share/wordlists/rockyou.txt.gz > /usr/share/wordlists/rockyou.txt" "Extracting rockyou.txt" 30
    echo -e "${GREEN}[✓] ROCKYOU.TXT EXTRACTED${NC}"
elif [ -f "/usr/share/wordlists/rockyou.txt" ]; then
    echo -e "${GREEN}[✓] ROCKYOU.TXT AVAILABLE${NC}"
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

# Make scripts executable
echo -e "${YELLOW}[!] SETTING PERMISSIONS...${NC}"
chmod +x *.py
echo -e "${GREEN}[✓] PERMISSIONS SET${NC}"

# Final verification
echo -e "${YELLOW}[!] FINAL VERIFICATION...${NC}"
if command -v aircrack-ng &> /dev/null && \
   command -v macchanger &> /dev/null; then
    echo -e "${GREEN}[✓] CORE FUNCTIONALITY VERIFIED${NC}"
    echo -e "${GREEN}[✓] NETSTRIKE FRAMEWORK READY!${NC}"
else
    echo -e "${RED}[✘] CORE TOOLS MISSING${NC}"
    echo -e "${YELLOW}[⚠️] INSTALLATION MAY BE INCOMPLETE${NC}"
fi

echo ""
echo -e "${CYAN}[💡] TO START: sudo python3 netstrike.py${NC}"
echo -e "${YELLOW}[⚠️] IMPORTANT: Use only for authorized testing!${NC}"
echo -e "${GREEN}[🎯] ULTIMATE FEATURES: Mass Destruction, Router Destroyer, Evil Twin${NC}"
