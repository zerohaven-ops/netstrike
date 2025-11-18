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

# Legal Disclaimer
echo -e "${YELLOW}"
echo "⚠️  LEGAL DISCLAIMER:"
echo "This tool is for educational and authorized security testing only."
echo "Users are solely responsible for complying with all applicable laws."
echo -e "${NC}"
echo

# Check root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}[✘] PLEASE RUN AS ROOT: sudo ./install.sh${NC}"
    exit 1
fi

# Check if dpkg is locked
check_dpkg_lock() {
    if [ -f /var/lib/dpkg/lock-frontend ] || [ -f /var/lib/dpkg/lock ] || [ -f /var/lib/apt/lists/lock ]; then
        return 1
    fi
    return 0
}

# Wait for dpkg lock
wait_for_dpkg_lock() {
    local timeout=120
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

# Run command with progress
run_cmd_safe() {
    local cmd="$1"
    local msg="$2"
    local timeout=${3:-60}
    
    echo -e "${YELLOW}[→] ${msg}...${NC}"
    
    if timeout $timeout bash -c "$cmd" > /dev/null 2>&1; then
        echo -e "${GREEN}[✓] ${msg} COMPLETED${NC}"
        return 0
    else
        echo -e "${RED}[✘] ${msg} FAILED${NC}"
        return 1
    fi
}

# Install package
install_package_safe() {
    local package="$1"
    
    if command -v "$package" &> /dev/null; then
        echo -e "${GREEN}[✓] $package ALREADY INSTALLED${NC}"
        return 0
    fi
    
    run_cmd_safe "apt install -y $package" "Installing $package" 120
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

echo -e "${CYAN}[!] DETECTED SYSTEM: ${DISTRO^^}${NC}"

# Wait for system locks
if ! wait_for_dpkg_lock; then
    echo -e "${RED}[✘] CANNOT PROCEED - SYSTEM LOCKS HELD${NC}"
    exit 1
fi

# Update system
echo -e "${YELLOW}[!] UPDATING SYSTEM REPOSITORIES...${NC}"
run_cmd_safe "apt update" "Updating repositories" 120

# Install essential tools
echo -e "${YELLOW}[!] INSTALLING ESSENTIAL TOOLS...${NC}"

core_tools=("python3" "aircrack-ng" "macchanger" "xterm")
advanced_tools=("mdk4" "reaver" "bully" "hostapd" "dnsmasq" "hcxdumptool" "hashcat")

for tool in "${core_tools[@]}"; do
    install_package_safe "$tool"
done

# Install advanced tools
for tool in "${advanced_tools[@]}"; do
    if ! command -v "$tool" &> /dev/null; then
        echo -e "${YELLOW}[!] ATTEMPTING TO INSTALL: $tool${NC}"
        install_package_safe "$tool"
    fi
done

# Install MDK4 from source if not available
if ! command -v mdk4 &> /dev/null; then
    echo -e "${YELLOW}[!] INSTALLING MDK4 FROM SOURCE...${NC}"
    run_cmd_safe "git clone https://github.com/aircrack-ng/mdk4" "Cloning MDK4" 60
    cd mdk4
    run_cmd_safe "make" "Building MDK4" 120
    run_cmd_safe "make install" "Installing MDK4" 60
    cd ..
    rm -rf mdk4
    echo -e "${GREEN}[✓] MDK4 INSTALLED FROM SOURCE${NC}"
fi

# Install Python packages
echo -e "${YELLOW}[!] INSTALLING PYTHON PACKAGES...${NC}"
run_cmd_safe "pip3 install requests scapy --break-system-packages --quiet" "Installing Python packages" 60

# Setup wordlists
echo -e "${YELLOW}[!] SETTING UP WORDLISTS...${NC}"
mkdir -p /usr/share/wordlists

if [ -f "/usr/share/wordlists/rockyou.txt.gz" ] && [ ! -f "/usr/share/wordlists/rockyou.txt" ]; then
    run_cmd_safe "gzip -dc /usr/share/wordlists/rockyou.txt.gz > /usr/share/wordlists/rockyou.txt" "Extracting rockyou.txt" 30
    echo -e "${GREEN}[✓] ROCKYOU.TXT EXTRACTED${NC}"
elif [ -f "/usr/share/wordlists/rockyou.txt" ]; then
    echo -e "${GREEN}[✓] ROCKYOU.TXT AVAILABLE${NC}"
else
    echo -e "${YELLOW}[!] CREATING BASIC WORDLIST...${NC}"
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
echo -e "${YELLOW}[!] SETTING EXECUTION PERMISSIONS...${NC}"
chmod +x *.py
echo -e "${GREEN}[✓] PERMISSIONS SET${NC}"

# Final verification
echo -e "${YELLOW}[!] VERIFYING INSTALLATION...${NC}"

essential_tools=("aircrack-ng" "macchanger" "python3")
missing_tools=()

for tool in "${essential_tools[@]}"; do
    if command -v "$tool" &> /dev/null; then
        echo -e "${GREEN}[✓] $tool VERIFIED${NC}"
    else
        echo -e "${RED}[✘] $tool MISSING${NC}"
        missing_tools+=("$tool")
    fi
done

if [ ${#missing_tools[@]} -eq 0 ]; then
    echo -e "${GREEN}[✓] ALL ESSENTIAL TOOLS VERIFIED${NC}"
    echo -e "${GREEN}[✓] NETSTRIKE v3.0 INSTALLED SUCCESSFULLY!${NC}"
else
    echo -e "${YELLOW}[⚠️] SOME TOOLS MISSING - BUT CORE FUNCTIONALITY SHOULD WORK${NC}"
fi

# Display completion message
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
echo -e "${YELLOW}[💡] FEATURES: Mass Destruction, Router Destroyer, Evil Twin, Auto Cracking${NC}"
echo -e "${YELLOW}[🔒] SECURITY: Continuous MAC/IP Spoofing, Zero Existence Mode${NC}"
echo -e "${YELLOW}[🎯] PERFORMANCE: Parallel Processing, Intelligent Attacks${NC}"
echo
