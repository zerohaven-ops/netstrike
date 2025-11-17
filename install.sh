#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

check_lock() {
    local locks=(/var/lib/dpkg/lock-frontend /var/lib/dpkg/lock /var/lib/apt/lists/lock)
    for l in "${locks[@]}"; do
        if [ -f "$l" ]; then return 1; fi
    done
    return 0
}

wait_lock() {
    local timeout=300
    local start=$(date +%s)
    while [ $(($(date +%s)-start)) -lt $timeout ]; do
        if check_lock; then
            echo -e "${GREEN}[✓] SYSTEM READY${NC}"
            return 0
        fi
        sleep 2
    done
    echo -e "${RED}[✘] SYSTEM LOCKED - TIMEOUT${NC}"
    return 1
}

run_cmd() {
    local cmd="$1"; local msg="$2"; local t=${3:-120}
    echo -e "${YELLOW}[→] $msg...${NC}"
    if ! check_lock; then
        echo -e "${RED}[✘] $msg - SYSTEM LOCKED${NC}"
        return 1
    fi
    timeout $t bash -c "$cmd" > /dev/null 2>&1 && echo -e "${GREEN}[✓] $msg${NC}" || echo -e "${RED}[✘] $msg FAILED${NC}"
}

DISTRO=$(grep -qi "kali" /etc/os-release && echo "kali" || grep -qi "ubuntu" /etc/os-release && echo "ubuntu" || echo "unknown")
[ "$EUID" -ne 0 ] && echo -e "${RED}[✘] RUN AS ROOT${NC}" && exit 1
wait_lock || exit 1

run_cmd "apt update -y || apt-get update -y" "Updating system" 180

if [ "$DISTRO" = "kali" ]; then
    command -v mdk4 >/dev/null || run_cmd "apt install -y mdk4 || apt-get install -y mdk4" "Installing MDK4" 180
else
    for tool in aircrack-ng macchanger reaver mdk4; do
        command -v $tool >/dev/null || run_cmd "apt install -y $tool || apt-get install -y $tool" "Installing $tool" 180
    done
fi

for py in requests scapy; do
    python3 -c "import $py" 2>/dev/null || run_cmd "pip3 install $py --break-system-packages --quiet" "Installing $py" 120
done

mkdir -p /usr/share/wordlists
if [ -f /usr/share/wordlists/rockyou.txt.gz ] && [ ! -f /usr/share/wordlists/rockyou.txt ]; then
    run_cmd "gzip -dc /usr/share/wordlists/rockyou.txt.gz > /usr/share/wordlists/rockyou.txt" "Extracting rockyou.txt" 60
elif [ ! -f /usr/share/wordlists/rockyou.txt ]; then
    cat > /usr/share/wordlists/netstrike_passwords.txt <<'EOF'
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

chmod +x *.py
echo -e "${GREEN}[✓] INSTALLATION COMPLETE${NC}"
