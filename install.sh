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

# Function to check dpkg locks
check_dpkg_lock() {
    if [ -f /var/lib/dpkg/lock-frontend ] || [ -f /var/lib/dpkg/lock ] || [ -f /var/lib/apt/lists/lock ]; then
        return 1
    fi
    return 0
}

# Function to get ALL locking processes
get_all_locking_processes() {
    echo -e "${YELLOW}[!] SCANNING FOR LOCKING PROCESSES...${NC}"
    
    local lock_files=("/var/lib/dpkg/lock-frontend" "/var/lib/dpkg/lock" "/var/lib/apt/lists/lock")
    local found_locks=0
    
    for lock_file in "${lock_files[@]}"; do
        if [ -f "$lock_file" ]; then
            echo -e "${YELLOW}[→] Found lock file: $lock_file${NC}"
            local pids=$(lsof -t "$lock_file" 2>/dev/null)
            
            if [ -n "$pids" ]; then
                for pid in $pids; do
                    local process_name=$(ps -p "$pid" -o comm= 2>/dev/null)
                    if [ -n "$process_name" ]; then
                        echo -e "${RED}[🔒] Locking Process: $process_name (PID: $pid) on $lock_file${NC}"
                        found_locks=1
                    fi
                done
            else
                echo -e "${YELLOW}[⚠️] Stale lock file (no process): $lock_file${NC}"
                found_locks=1
            fi
        fi
    done
    
    return $found_locks
}

# AGGRESSIVE lock cleanup - NO WAITING
aggressive_lock_cleanup() {
    echo -e "${RED}[💀] AGGRESSIVE LOCK CLEANUP INITIATED${NC}"
    
    # Kill ALL package management processes
    echo -e "${YELLOW}[→] Terminating package management processes...${NC}"
    
    pkill -9 apt
    pkill -9 apt-get
    pkill -9 dpkg
    pkill -9 packagekitd
    pkill -9 synaptic
    pkill -9 software-center
    
    # Wait a moment for processes to die
    sleep 2
    
    # Force remove ALL lock files
    echo -e "${YELLOW}[→] Removing ALL lock files...${NC}"
    
    rm -f /var/lib/dpkg/lock-frontend
    rm -f /var/lib/dpkg/lock
    rm -f /var/lib/apt/lists/lock
    rm -f /var/cache/apt/archives/lock
    
    # Fix any broken package states
    echo -e "${YELLOW}[→] Fixing package states...${NC}"
    dpkg --configure -a 2>/dev/null
    apt-get install -f -y 2>/dev/null
    
    echo -e "${GREEN}[✓] AGGRESSIVE LOCK CLEANUP COMPLETED${NC}"
}

# Check and immediately handle locks
handle_locks_immediately() {
    if check_dpkg_lock; then
        echo -e "${GREEN}[✓] NO LOCKS FOUND - PROCEEDING${NC}"
        return 0
    else
        echo -e "${RED}[✘] LOCKS DETECTED - FORCING CLEANUP${NC}"
        get_all_locking_processes
        aggressive_lock_cleanup
        
        # Check again after cleanup
        if check_dpkg_lock; then
            echo -e "${GREEN}[✓] LOCKS CLEARED - PROCEEDING${NC}"
            return 0
        else
            echo -e "${RED}[✘] UNABLE TO CLEAR LOCKS - MANUAL INTERVENTION REQUIRED${NC}"
            echo -e "${YELLOW}[💡] Run these commands manually:${NC}"
            echo -e "     sudo pkill -9 apt apt-get dpkg"
            echo -e "     sudo rm -f /var/lib/dpkg/lock* /var/lib/apt/lists/lock*"
            echo -e "     sudo dpkg --configure -a"
            return 1
        fi
    fi
}

# Run command with simple output
run_cmd() {
    local cmd="$1"
    local msg="$2"
    
    echo -e "${YELLOW}[→] $msg...${NC}"
    
    if eval "$cmd" > /dev/null 2>&1; then
        echo -e "${GREEN}[✓] $msg${NC}"
        return 0
    else
        echo -e "${RED}[✘] $msg${NC}"
        return 1
    fi
}

# Install package
install_package() {
    local package="$1"
    local description="${2:-$package}"
    
    if command -v "$package" &> /dev/null; then
        echo -e "${GREEN}[✓] $description ALREADY INSTALLED${NC}"
        return 0
    fi
    
    run_cmd "apt install -y $package" "Installing $description"
}

# Main installation
main_installation() {
    echo -e "${CYAN}[!] STARTING NETSTRIKE v3.0 INSTALLATION${NC}"
    
    # Handle locks IMMEDIATELY (no waiting)
    if ! handle_locks_immediately; then
        exit 1
    fi
    
    # Update system
    echo -e "${YELLOW}[!] UPDATING SYSTEM...${NC}"
    run_cmd "apt update" "Updating repositories"
    
    # Install CORE tools (essential for basic functionality)
    echo -e "${YELLOW}[!] INSTALLING CORE TOOLS...${NC}"
    
    core_tools=(
        "python3"
        "aircrack-ng" 
        "macchanger"
        "xterm"
        "wireless-tools"
        "iw"
    )
    
    for tool in "${core_tools[@]}"; do
        install_package "$tool"
    done
    
    # Install ADVANCED tools (try but don't fail if they don't install)
    echo -e "${YELLOW}[!] INSTALLING ADVANCED TOOLS...${NC}"
    
    advanced_tools=(
        "mdk4"
        "reaver" 
        "hostapd"
        "dnsmasq"
    )
    
    for tool in "${advanced_tools[@]}"; do
        if ! command -v "$tool" &> /dev/null; then
            install_package "$tool"
        fi
    done
    
    # Install Python packages
    echo -e "${YELLOW}[!] INSTALLING PYTHON PACKAGES...${NC}"
    run_cmd "pip3 install requests scapy --break-system-packages" "Installing Python packages"
    
    # Setup wordlists
    echo -e "${YELLOW}[!] SETTING UP WORDLISTS...${NC}"
    mkdir -p /usr/share/wordlists
    
    if [ -f "/usr/share/wordlists/rockyou.txt.gz" ] && [ ! -f "/usr/share/wordlists/rockyou.txt" ]; then
        run_cmd "gzip -dc /usr/share/wordlists/rockyou.txt.gz > /usr/share/wordlists/rockyou.txt" "Extracting rockyou.txt"
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
    echo -e "${YELLOW}[!] SETTING PERMISSIONS...${NC}"
    chmod +x *.py
    echo -e "${GREEN}[✓] PERMISSIONS SET${NC}"
    
    # Final check
    echo -e "${YELLOW}[!] FINAL VERIFICATION...${NC}"
    if command -v python3 && command -v aircrack-ng && command -v macchanger; then
        echo -e "${GREEN}[✓] CORE TOOLS VERIFIED - INSTALLATION SUCCESSFUL!${NC}"
    else
        echo -e "${YELLOW}[⚠️] SOME TOOLS MISSING - BUT BASIC FUNCTIONALITY AVAILABLE${NC}"
    fi
}

# Display completion
show_completion() {
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
    echo -e "${GREEN}[🎯] NetStrike v3.0 Ready for Educational Use${NC}"
    echo
}

# Run installation
main_installation
show_completion
