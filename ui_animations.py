#!/usr/bin/env python3
"""
NETSTRIKE v3.0 UI ANIMATIONS
Cinematic Cyber Interface & Visual Effects
"""

import time
import random
import sys
import os

class CyberUI:
    def __init__(self):
        self.colors = {
            'green': '\033[1;32m',
            'red': '\033[1;31m', 
            'yellow': '\033[1;33m',
            'blue': '\033[1;34m',
            'magenta': '\033[1;35m',
            'cyan': '\033[1;36m',
            'white': '\033[1;37m',
            'reset': '\033[0m'
        }
        
    def matrix_rain(self, duration=5):
        """Matrix-style digital rain effect"""
        chars = "01█▓▒░"
        lines = []
        
        start_time = time.time()
        while time.time() - start_time < duration:
            line = "".join(random.choice(chars) for _ in range(80))
            lines.append(line)
            
            if len(lines) > 20:
                lines.pop(0)
                
            os.system('clear')
            for line in lines:
                print(f"\033[1;32m{line}\033[0m")
                
            time.sleep(0.1)
            
        os.system('clear')
        
    def type_effect(self, text, speed=0.05):
        """Matrix typing effect"""
        for char in text:
            print(char, end='', flush=True)
            time.sleep(speed)
        print()
        
    def animated_text(self, text, speed=0.05):
        """Animated text with cyber effect"""
        colors = ['\033[1;32m', '\033[1;36m', '\033[1;35m']
        current_color = random.choice(colors)
        
        print(f"{current_color}[⚡]", end='', flush=True)
        time.sleep(0.3)
        
        for char in text:
            print(char, end='', flush=True)
            time.sleep(speed)
            
        print("\033[0m")
        
    def progress_bar(self, title, duration=5, width=50):
        """Cinematic progress bar"""
        print(f"\n\033[1;36m[→] {title}\033[0m")
        
        for i in range(width + 1):
            progress = i / width
            bar = "█" * i + "░" * (width - i)
            percentage = int(progress * 100)
            
            # Cycling colors for cyber effect
            color_cycle = ['\033[1;32m', '\033[1;36m', '\033[1;35m']
            color = color_cycle[i % len(color_cycle)]
            
            print(f"\r{color}[{bar}] {percentage}%\033[0m", end='', flush=True)
            time.sleep(duration / width)
            
        print()
        
    def attack_header(self, title):
        """Cinematic attack header"""
        os.system('clear')
        border = "╔" + "═" * 60 + "╗"
        middle = "║" + " " * 60 + "║"
        title_line = f"║{title:^60}║"
        
        print(f"\033[1;31m{border}")
        print(middle)
        print(title_line)
        print(middle)
        print(f"{border}\033[0m\n")
        
    def animate_spoofing_status(self):
        """Animated spoofing status indicator"""
        frames = ["🔄", "⚡", "🔒", "🎭", "👻"]
        for _ in range(10):
            for frame in frames:
                print(f"\r\033[1;36m[{frame}] SPOOFING ACTIVE - Identity rotation in progress...\033[0m", end='', flush=True)
                time.sleep(0.3)
        print("\r" + " " * 80 + "\r", end='', flush=True)
        
    def success_message(self, message):
        """Success message with animation"""
        print(f"\n\033[1;32m[✅] {message}\033[0m")
        
    def error_message(self, message):
        """Error message with animation"""
        print(f"\n\033[1;31m[❌] {message}\033[0m")
        
    def warning_message(self, message):
        """Warning message with animation"""
        print(f"\n\033[1;33m[⚠️] {message}\033[0m")
