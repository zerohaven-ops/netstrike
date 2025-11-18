#!/bin/bash

# NetStrike v3.0 Force Installer
# ULTIMATE LOCK BREAKER - NO WAITING, NO MERCY

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${RED}"
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                                                                  ║"
echo "║                   🚀 FORCE INSTALLER v3.0                        ║"
echo "║                     NO LOCKS CAN STOP US                         ║"
echo "║                                                                  ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}[✘] PLEASE RUN AS ROOT: sudo ./force_install.sh${NC}"
    exit 1
fi

# NUCLEAR LOCK CLEANUP
echo -e "${RED}[💀] INITIATING NUCLEAR LOCK CLEANUP...${NC}"

# Kill EVERYTHING that could be locking
echo -e "${YELLOW}[→] Terminating ALL package processes...${NC}"
pkill -9 -f apt
pkill -9 -f dpkg
pkill -9 -f packagekit
pkill -9 -f synaptic
pkill -9 -f software-center
pkill -9 -f update-notifier

# Remove ALL lock files
echo -e "${YELLOW}[→] Removing ALL lock files...${NC}"
rm -f /var/lib/dpkg/lock*
rm -f /var/lib/apt/lists/lock*
rm -f /var/cache/apt/archives/lock*

# Fix package states
echo -e "${YELLOW}[→] Fixing package states...${NC}"
dpkg --configure -a
apt-get install -f -y

echo -e "${GREEN}[✓] LOCKS DESTROYED - PROCEEDING WITH INSTALLATION${NC}"

# Now run the main installer
./install.sh
