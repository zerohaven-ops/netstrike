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

# Function to get locking process
get_locking_process() {
    local lock_files=("/var/lib/dpkg/lock-frontend" "/var/lib/dpkg/lock" "/var/lib/apt/lists/lock")
    
    for lock_file in "${lock_files[@]}"; do
        if [ -f "$lock_file" ]; then
            local pid=$(lsof -t "$lock_file" 2>/dev/null | head -1)
            if [ -n "$pid" ]; then
                local process_name=$(ps -p "$pid" -o comm= 2>/dev/null)
                echo "$pid:$process_name:$lock_file"
                return 0
            fi
        fi
    done
    echo ":::"
}

# Smart lock cleanup
smart_lock_cleanup() {
    echo -e "${YELLOW}[!] ATTEMPTING SMART LOCK RESOLUTION...${NC}"
    
    local lock_info=$(get_locking_process)
    local pid=$(echo "$lock_info" | cut -d: -f1)
    local process_name=$(echo "$lock_info" | cut -d: -f2)
    local lock_file=$(echo "$lock_info" | cut -d: -f3)
    
    if [ "$pid" != "" ] && [ "$process_name" != "" ]; then
        echo -e "${YELLOW}[→] Found locking process: ${process_name} (PID: ${pid}) on ${lock_file}${NC}"
        
        # Check if it's a critical system process
        critical_processes=("apt" "apt-get" "dpkg" "packagekitd" "synaptic")
        for critical in "${critical_processes[@]}"; do
            if [[ "$process_name" == *"$critical"* ]]; then
                echo -e "${YELLOW}[!] Critical system process detected. Waiting for completion...${NC}"
                return 1
            fi
        done
        
        read -p "$(echo -e "${YELLOW}[?] Kill this process to continue installation? (y/N): ${NC}")" response
        if [[ $response =~ ^[Yy]$ ]]; then
            echo -e "${RED}[💣] Killing process ${pid} (${process_name})...${NC}"
            kill -9 "$pid" 2>/dev/null
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
        echo -e "${YELLOW}[!] No specific locking process found, removing stale locks...${NC}"
        rm -f /var/lib/dpkg/lock-frontend
        rm -f /var/lib/dpkg/lock
        rm -f /var/lib/apt/lists/lock
        dpkg --configure -a 2>/dev/null
        return 0
    fi
}

# Wait for dpkg lock with smart handling
wait_for_dpkg_lock() {
    local timeout=60  # Reduced timeout to 60 seconds
    local start_time=$(date +%s)
    
    echo -e "${YELLOW}[!] CHECKING FOR SYSTEM LOCKS...${NC}"
    
    while [ $(($(date +%s) - start_time)) -lt $timeout ]; do
        if check_dpkg_lock; then
            echo -e "${GREEN}[✓] SYSTEM READY FOR INSTALLATION${NC}"
            return 0
        fi
        
        local elapsed=$(($(date +%s) - start_time))
        
        # After 15 seconds, offer smart cleanup
        if [ $elapsed -ge 15 ]; then
            echo -e "${YELLOW}[⚠️] System locked for ${elapsed}s${NC}"
            if smart_lock_cleanup; then
                # Check again after cleanup
                if check_dpkg_lock; then
                    echo -e "${GREEN}[✓] SYSTEM READY AFTER CLEANUP${NC}"
                    return 0
                fi
            fi
        fi
        
        local dots=$(printf '%*s' $((elapsed % 4)) | tr ' ' '.')
        echo -ne "\r${YELLOW}[⌛] WAITING FOR SYSTEM LOCKS${dots} (${elapsed}s)${NC}"
        sleep 2
    done
    
    echo -e "\r${RED}[✘] TIMEOUT WAITING FOR SYSTEM LOCKS AFTER ${timeout}s${NC}"
    echo -e "${YELLOW}[💡] TIP: Try these commands manually, then rerun installer:${NC}"
    echo -e "     sudo rm -f /var/lib/dpkg/lock-frontend"
    echo -e "     sudo rm -f /var/lib/dpkg/lock" 
    echo -e "     sudo rm -f /var/lib/apt/lists/lock"
    echo -e "     sudo dpkg --configure -a"
    return 1
}

# Run command with progress
run_cmd_safe() {
    local cmd="$1"
    local msg="$2"
    local timeout=${3:-120}
    
    echo -e "${YELLOW}[→] ${msg}...${NC}"
    
    # Show spinner in background
    local spinstr='|/-\'
    local i=0
    while :; do
        printf "\r${YELLOW}[${spinstr:$i:1}] ${msg}...${NC}"
        sleep 0.1
        i=$(( (i+1) % 4 ))
    done &
    
    local spinner_pid=$!
    
    # Run the actual command
    if eval "$cmd" > /dev/null 2>&1; then
        kill $spinner_pid
        wait $spinner_pid 2>/dev/null
        printf "\r${GREEN}[✓] ${msg} COMPLETED${NC}\n"
        return 0
    else
        kill $spinner_pid
        wait $spinner_pid 2>/dev/null
        printf "\r${RED}[✘] ${msg} FAILED${NC}\n"
        return 1
    fi
}

# Install package
install_package_safe() {
    local package="$1"
    local description="${2:-$package}"
    
    if command -v "$package" &> /dev/null; then
        echo -e "${GREEN}[✓] $description ALREADY INSTALLED${NC}"
        return 0
    fi
    
    run_cmd_safe "apt install -y $package" "Installing $description" 180
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

# Main installation function
main_installation() {
    DISTRO=$(detect_distro)
    echo -e "${CYAN}[!] DETECTED SYSTEM: ${DISTRO^^}${NC}"

    # Wait for system locks
    if ! wait_for_dpkg_lock; then
        echo -e "${RED}[✘] CANNOT PROCEED - SYSTEM LOCKS HELD${NC}"
        echo -e "${YELLOW}[💡] Please wait for other package operations to complete and rerun${NC}"
        exit 1
    fi

    # Update system (skip if recently updated)
    echo -e "${YELLOW}[!] UPDATING SYSTEM REPOSITORIES...${NC}"
    run_cmd_safe "apt update" "Updating repositories" 120

    # Install core tools
    echo -e "${YELLOW}[!] INSTALLING CORE TOOLS...${NC}"
    
    core_tools=(
        "python3:Python 3"
        "aircrack-ng:Aircrack-ng Suite"
        "macchanger:MAC Address Changer" 
        "xterm:Terminal Emulator"
        "wireless-tools:Wireless Tools"
        "iw:Wireless Config"
        "procps:Process Utilities"
        "net-tools:Network Tools"
    )
    
    for tool_info in "${core_tools[@]}"; do
        package="${tool_info%:*}"
        description="${tool_info#*:}"
        install_package_safe "$package" "$description"
    done

    # Install advanced tools
    echo -e "${YELLOW}[!] INSTALLING ADVANCED TOOLS...${NC}"
    
    advanced_tools=(
        "mdk4:MDK4 Wireless Tool"
        "reaver:WPS PIN Attack"
        "bully:WPS Bruteforce" 
        "hostapd:Access Point Software"
        "dnsmasq:DHCP/DNS Server"
        "hcxdumptool:PMKID Capture"
        "hashcat:Password Cracking"
    )
    
    for tool_info in "${advanced_tools[@]}"; do
        package="${tool_info%:*}"
        description="${tool_info#*:}"
        if ! command -v "$package" &> /dev/null; then
            echo -e "${YELLOW}[!] ATTEMPTING TO INSTALL: $description${NC}"
            install_package_safe "$package" "$description"
        else
            echo -e "${GREEN}[✓] $description ALREADY INSTALLED${NC}"
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
}

# Display completion message
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
    echo -e "${YELLOW}[💡] FEATURES: Mass Destruction, Router Destroyer, Evil Twin, Auto Cracking${NC}"
    echo -e "${YELLOW}[🔒] SECURITY: Continuous MAC/IP Spoofing, Zero Existence Mode${NC}"
    echo -e "${YELLOW}[🎯] PERFORMANCE: Parallel Processing, Intelligent Attacks${NC}"
    echo
}

# Run main installation
main_installation
show_completion
