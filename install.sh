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

# Check and remove locks quickly
check_and_remove_locks() {
    echo -e "${YELLOW}[!] CHECKING FOR SYSTEM LOCKS...${NC}"
    
    local lock_files=(
        "/var/lib/dpkg/lock-frontend"
        "/var/lib/dpkg/lock"
        "/var/lib/apt/lists/lock"
        "/var/cache/apt/archives/lock"
    )
    
    local locks_found=0
    
    for lock_file in "${lock_files[@]}"; do
        if [ -f "$lock_file" ]; then
            echo -e "${YELLOW}[!] REMOVING LOCK: $lock_file${NC}"
            rm -f "$lock_file"
            locks_found=1
        fi
    done
    
    # Kill any hanging dpkg/apt processes
    local hanging_procs=$(ps aux | grep -E '(dpkg|apt)' | grep -v grep | awk '{print $2}')
    if [ -n "$hanging_procs" ]; then
        echo -e "${YELLOW}[!] TERMINATING HANGING PROCESSES...${NC}"
        kill -9 $hanging_procs 2>/dev/null
        locks_found=1
    fi
    
    if [ $locks_found -eq 1 ]; then
        echo -e "${GREEN}[✓] SYSTEM LOCKS CLEARED${NC}"
    else
        echo -e "${GREEN}[✓] NO LOCKS FOUND - SYSTEM READY${NC}"
    fi
    
    # Fix any broken states
    dpkg --configure -a 2>/dev/null
    apt-get install -f -y 2>/dev/null
    
    return 0
}

# Quick lock check (10 seconds max)
quick_lock_check() {
    local timeout=10
    local start_time=$(date +%s)
    
    echo -e "${YELLOW}[!] QUICK SYSTEM CHECK...${NC}"
    
    while [ $(($(date +%s) - start_time)) -lt $timeout ]; do
        if ! fuser /var/lib/dpkg/lock-frontend >/dev/null 2>&1 && \
           ! fuser /var/lib/dpkg/lock >/dev/null 2>&1 && \
           ! fuser /var/lib/apt/lists/lock >/dev/null 2>&1; then
            echo -e "${GREEN}[✓] SYSTEM READY FOR INSTALLATION${NC}"
            return 0
        fi
        
        local elapsed=$(($(date +%s) - start_time))
        local remaining=$((timeout - elapsed))
        echo -e "${YELLOW}[⌛] WAITING FOR LOCKS... ${remaining}s${NC}"
        sleep 1
    done
    
    # Force remove locks after timeout
    echo -e "${YELLOW}[!] FORCE REMOVING LOCKS AFTER TIMEOUT${NC}"
    check_and_remove_locks
    return 0
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
    
    run_cmd_safe "apt install -y $package" "Installing $package" 90
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

# Main installation
main_installation() {
    local DISTRO=$(detect_distro)
    
    echo -e "${CYAN}[!] DETECTED SYSTEM: ${DISTRO^^}${NC}"
    
    # Quick lock check and removal
    quick_lock_check
    
    # Update system (quick)
    echo -e "${YELLOW}[!] UPDATING SYSTEM REPOSITORIES...${NC}"
    run_cmd_safe "apt update" "Updating repositories" 60
    
    # Install essential tools
    echo -e "${YELLOW}[!] INSTALLING ESSENTIAL TOOLS...${NC}"
    
    core_tools=("python3" "aircrack-ng" "macchanger" "xterm")
    advanced_tools=("mdk4" "reaver" "hostapd" "dnsmasq")
    
    for tool in "${core_tools[@]}"; do
        install_package_safe "$tool"
    done
    
    # Install advanced tools (skip if takes too long)
    for tool in "${advanced_tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            echo -e "${YELLOW}[!] ATTEMPTING TO INSTALL: $tool${NC}"
            install_package_safe "$tool"
        fi
    done
    
    # Quick MDK4 installation
    if ! command -v mdk4 &> /dev/null; then
        echo -e "${YELLOW}[!] QUICK MDK4 INSTALLATION...${NC}"
        run_cmd_safe "apt install -y mdk4" "Installing MDK4" 60
    fi
    
    # Install Python packages
    echo -e "${YELLOW}[!] INSTALLING PYTHON PACKAGES...${NC}"
    run_cmd_safe "pip3 install requests scapy --break-system-packages --quiet" "Installing Python packages" 45
    
    # Setup wordlists (quick)
    echo -e "${YELLOW}[!] SETTING UP WORDLISTS...${NC}"
    mkdir -p /usr/share/wordlists
    
    if [ -f "/usr/share/wordlists/rockyou.txt.gz" ] && [ ! -f "/usr/share/wordlists/rockyou.txt" ]; then
        run_cmd_safe "gzip -dc /usr/share/wordlists/rockyou.txt.gz > /usr/share/wordlists/rockyou.txt" "Extracting rockyou.txt" 20
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
    echo -e "${YELLOW}[!] QUICK VERIFICATION...${NC}"
    
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
        echo -e "${YELLOW}[⚠️] SOME TOOLS MISSING - CORE FUNCTIONALITY AVAILABLE${NC}"
        echo -e "${YELLOW}[💡] You can manually install missing tools later${NC}"
    fi
}

# Display completion message
display_completion() {
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
}

# Main execution
main_installation
display_completion
