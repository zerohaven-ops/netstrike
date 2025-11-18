#!/usr/bin/env python3
"""
Test script to check all NetStrike imports
"""

import os
import sys

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("🔍 TESTING NETSTRIKE IMPORTS...")

modules = [
    'core_engine',
    'security_daemon', 
    'ui_animations',
    'scanner_advanced',
    'freeze_attack',
    'mass_destruction',
    'router_destroyer',
    'password_cracker',
    'evil_twin_advanced',
    'zero_existence'
]

for module in modules:
    try:
        __import__(module)
        print(f"✅ {module}: SUCCESS")
    except ImportError as e:
        print(f"❌ {module}: FAILED - {e}")
    except Exception as e:
        print(f"⚠️  {module}: ERROR - {e}")

print("\n🎯 TEST COMPLETE")
