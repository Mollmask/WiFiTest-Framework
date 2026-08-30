from setuptools import setup, find_packages

setup(
    name="wifitest",
    version="1.0.0",
    description="Authorized WiFi security testing framework for labs and red team engagements",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Security Research Team",
    license="MIT",
    python_requires=">=3.10",
    packages=find_packages(exclude=["tests", "docs"]),
    install_requires=[
        "click>=8.1.0",
        "rich>=13.0.0",
        "scapy>=2.5.0",
        "psutil>=5.9.0",
        "jinja2>=3.1.0",
    ],
    extras_require={
        "dev": ["pytest>=7.0.0", "pytest-cov"],
    },
    entry_points={
        "console_scripts": [
            "wifitest=wifitest.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Security",
    ],
)
# Installation

## System Requirements

- Kali Linux 2024+ (or Debian/Ubuntu with wireless tools)
- Python 3.10+
- Wireless adapter supporting monitor mode

## Steps

1. Install system deps:
   ```bash
   sudo apt-get install -y hostapd dnsmasq aircrack-ng iw python3-scapy
   ```

2. Clone and install:
   ```bash
   git clone https://github.com/yourorg/wifitest.git
   cd wifitest
   python3 -m venv venv && source venv/bin/activate
   pip install -r requirements.txt
   pip install -e .
   ```

3. Verify:
   ```bash
   wifitest --version
   ```
   # Usage Guide

## Interactive Mode (Beginners)

```bash
sudo wifitest interactive
```

Guides you through each step with prompts.

## CLI Mode (Advanced)

```bash
# List adapters
sudo wifitest adapters

# Scan
sudo wifitest scan -i wlan0 -d 15

# Evil Twin
sudo wifitest evil-twin -i wlan0 -s "TargetSSID" -c 6 --scenario router-update

# KARMA
sudo wifitest karma -i wlan0

# Known Beacons
sudo wifitest known-beacons -i wlan0 --list custom.txt

# Generate report
wifitest report --session logs/session.json --format markdown -o report.md
```

## Safety Features

- Authorization confirmation required
- No password storage
- No malware delivery
- All activity logged to JSON
# Training Scenarios

## Router Update Page

Simulates a router admin page prompting firmware update.
- Shows clear "training scenario" banner
- Form submissions are discarded
- No data stored

## Login Page

Generic captive portal login simulation.
- Email + password fields (not stored)
- Visual indicator that this is a demo
- Useful for teaching phishing awareness

## Adding Custom Scenarios

Create a new module in `wifitest/scenarios/`
