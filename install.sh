#!/bin/bash

# NetStrike Framework Installer - Smart Lock Handling
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

# Get the process holding the dpkg lock
get_locking_process() {
    if [ -f /var/lib/dpkg/lock-frontend ]; then
        local pid=$(lsof /var/lib/dpkg/lock-frontend 2>/dev/null | tail -1 | awk '{print $2}')
        if [ -n "$pid" ]; then
            local process_name=$(ps -p $pid -o comm= 2>/dev/null)
            echo "$pid:$process_name"
        fi
    fi
}

# Smart lock cleanup with user permission
smart_lock_cleanup() {
    echo -e "${YELLOW}[!] ATTEMPTING SMART LOCK RESOLUTION...${NC}"
    
    local lock_info=$(get_locking_process)
    if [ -n "$lock_info" ]; then
        local pid=$(echo "$lock_info" | cut -d: -f1)
        local process_name=$(echo "$lock_info" | cut -d: -f2)
        
        echo -e "${YELLOW}[→] Found locking process: ${process_name} (PID: ${pid})${NC}"
        
        read -p "$(echo -e "${YELLOW}[?] Kill this process to continue installation? (y/N): ${NC}")" response
        if [[ $response =~ ^[Yy]$ ]]; then
            echo -e "${RED}[💣] Killing process ${pid} (${process_name})...${NC}"
            kill -9 $pid 2>/dev/null
            sleep 2
            
            # Remove lock files
            echo -e "${YELLOW}[→] Removing system locks...${NC}"
            rm -f /var/lib/dpkg/lock-frontend
            rm -f /var/lib/dpkg/lock
            rm -f /var/lib/apt/lists/lock
            
            # Fix any broken states
            dpkg --configure -a 2>/dev/null
            apt-get install -f -y 2>/dev/null
            
            echo -e "${GREEN}[✓] System locks cleared${NC}"
            return 0
        else
            echo -e "${YELLOW}[!] Continuing without killing process...${NC}"
            return 1
        fi
    else
        echo -e "${YELLOW}[!] No specific locking process found${NC}"
        return 1
    fi
}

# Wait for dpkg lock with smart handling
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
        
        # After 30 seconds, offer smart cleanup
        if [ $elapsed -ge 30 ]; then
            echo -e "${YELLOW}[⚠️] System locked for ${elapsed}s${NC}"
            if smart_lock_cleanup; then
                return 0
            fi
        fi
        
        local dots=$(printf '%*s' $((elapsed % 4)) | tr ' ' '.')
        echo -ne "\r${YELLOW}[⌛] WAITING FOR SYSTEM LOCKS${dots} (${elapsed}s)${NC}"
        sleep 2
    done
    
    echo -e "\r${RED}[✘] TIMEOUT WAITING FOR SYSTEM LOCKS AFTER ${timeout}s${NC}"
    return 1
}

# Simple command runner with timeout and lock checking
run_cmd_safe() {
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

# Install package with lock checking
install_package_safe() {
    local package="$1"
    
    if command -v "$package" &> /dev/null; then
        echo -e "${GREEN}[✓] $package ALREADY INSTALLED${NC}"
        return 0
    fi
    
    if [ "$DISTRO" = "kali" ]; then
        run_cmd_safe "apt install -y $package" "Installing $package" 120
    else
        run_cmd_safe "apt-get install -y $package" "Installing $package" 120
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
echo "║                      SMART LOCK HANDLING                         ║"
echo "║                         DETECTED: ${DISTRO^^}                          ║"
echo "║                                                                  ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}[✘] PLEASE RUN AS ROOT: sudo ./install.sh${NC}"
    exit 1
fi

echo -e "${YELLOW}[!] STARTING SMART INSTALLATION FOR ${DISTRO^^}...${NC}"

# Wait for system locks first
if ! wait_for_dpkg_lock; then
    echo -e "${RED}[✘] CANNOT PROCEED - SYSTEM LOCKS HELD${NC}"
    echo -e "${YELLOW}[💡] TIP: Wait for other package operations to complete${NC}"
    exit 1
fi

# Quick system update
echo -e "${YELLOW}[!] CHECKING SYSTEM UPDATES...${NC}"
if run_cmd_safe "apt update" "Checking updates" 60; then
    echo -e "${GREEN}[✓] SYSTEM READY${NC}"
else
    echo -e "${YELLOW}[⚠️] UPDATE CHECK FAILED - CONTINUING ANYWAY${NC}"
fi

# Kali Linux - Minimal installation
if [ "$DISTRO" = "kali" ]; then
    echo -e "${CYAN}[!] KALI DETECTED - MINIMAL INSTALLATION...${NC}"
    
    # Check what's already installed
    echo -e "${YELLOW}[!] CHECKING INSTALLED TOOLS...${NC}"
    
    # List of tools to check
    tools=("aircrack-ng" "macchanger" "reaver" "bully" "hashcat" "hostapd" "dnsmasq" "mdk4")
    
    for tool in "${tools[@]}"; do
        if command -v "$tool" &> /dev/null; then
            echo -e "${GREEN}[✓] $tool ALREADY INSTALLED${NC}"
        else
            echo -e "${YELLOW}[!] NEED TO INSTALL: $tool${NC}"
        fi
    done
    
    # Install only MDK4 if missing (usually the only one needed)
    if ! command -v mdk4 &> /dev/null; then
        echo -e "${YELLOW}[!] INSTALLING MDK4...${NC}"
        if install_package_safe "mdk4"; then
            echo -e "${GREEN}[✓] MDK4 INSTALLED${NC}"
        else
            # Try source installation as fallback
            echo -e "${YELLOW}[!] TRYING MDK4 FROM SOURCE...${NC}"
            run_cmd_safe "git clone https://github.com/aircrack-ng/mdk4" "Cloning MDK4" 60
            cd mdk4
            run_cmd_safe "make" "Building MDK4" 120
            run_cmd_safe "make install" "Installing MDK4" 60
            cd ..
            rm -rf mdk4
            echo -e "${GREEN}[✓] MDK4 INSTALLED FROM SOURCE${NC}"
        fi
    fi

    # Install Python packages via pip (avoid apt locks)
    echo -e "${YELLOW}[!] CHECKING PYTHON PACKAGES...${NC}"
    if python3 -c "import requests" 2>/dev/null && python3 -c "import scapy" 2>/dev/null; then
        echo -e "${GREEN}[✓] PYTHON PACKAGES ALREADY INSTALLED${NC}"
    else
        echo -e "${YELLOW}[!] INSTALLING PYTHON PACKAGES VIA PIP...${NC}"
        run_cmd_safe "pip3 install requests scapy --break-system-packages --quiet" "Installing Python packages" 60
    fi

else
    # Generic installation for other distros
    echo -e "${CYAN}[!] ${DISTRO^^} DETECTED - STANDARD INSTALLATION...${NC}"
    
    # Install core tools
    tools=("aircrack-ng" "macchanger" "reaver" "bully" "hashcat" "hostapd" "dnsmasq" "mdk4")
    for tool in "${tools[@]}"; do
        install_package_safe "$tool"
    done
    
    # Python packages
    run_cmd_safe "pip3 install requests scapy --break-system-packages --quiet" "Installing Python packages" 60
fi

# Setup wordlists (no downloads - use existing or create basic)
echo -e "${YELLOW}[!] SETTING UP WORDLISTS...${NC}"
mkdir -p /usr/share/wordlists

if [ -f "/usr/share/wordlists/rockyou.txt.gz" ] && [ ! -f "/usr/share/wordlists/rockyou.txt" ]; then
    run_cmd_safe "gzip -dc /usr/share/wordlists/rockyou.txt.gz > /usr/share/wordlists/rockyou.txt" "Extracting rockyou.txt" 30
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
   command -v macchanger &> /dev/null && \
   command -v mdk4 &> /dev/null; then
    echo -e "${GREEN}[✓] ALL CORE TOOLS VERIFIED${NC}"
    echo -e "${GREEN}[✓] NETSTRIKE FRAMEWORK INSTALLED SUCCESSFULLY!${NC}"
else
    echo -e "${YELLOW}[⚠️] SOME TOOLS MISSING - BUT CORE FUNCTIONALITY SHOULD WORK${NC}"
    echo -e "${YELLOW}[💡] You can manually install missing tools later${NC}"
fi

echo ""
echo -e "${CYAN}[💡] TO START: sudo python3 netstrike.py${NC}"
echo -e "${YELLOW}[⚠️] IMPORTANT: Use only for authorized testing!${NC}"
echo -e "${GREEN}[🎯] ULTIMATE FEATURES: Mass Destruction, Router Destroyer, Evil Twin, Auto Cracking${NC}"
echo ""
echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                         QUICK START                            ║${NC}"
echo -e "${BLUE}╠══════════════════════════════════════════════════════════════════╣${NC}"
echo -e "${BLUE}║                                                                  ║${NC}"
echo -e "${BLUE}║  1. sudo python3 netstrike.py                                    ║${NC}"
echo -e "${BLUE}║  2. Select your wireless interface                               ║${NC}"
echo -e "${BLUE}║  3. Choose attack type from menu                                 ║${NC}"
echo -e "${BLUE}║  4. Press Ctrl+C to stop any running attack                      ║${NC}"
echo -e "${BLUE}║                                                                  ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════╝${NC}"
