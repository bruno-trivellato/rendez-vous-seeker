# 🎯 Rendez-vous Monitor

**Automated appointment availability monitor for French city hall scheduling using Selenium WebDriver.**

## What it does

This system is a **Chrome bot** that automatically monitors the Boulogne-Billancourt city hall appointment page and alerts you when slots become available for **Titre de Séjour** scheduling.

### How it works technically

1. **Opens Chrome browser** using Selenium WebDriver (undetected-chromedriver)
2. **Navigates to the appointment page** automatically
3. **Refreshes the page continuously** (like pressing F5 repeatedly)
4. **Detects when slots become available** by monitoring page content
5. **Alerts you immediately** with sound and notifications when appointments are found

## When to use it

### ⏰ **Optimal Usage Time**
According to the prefecture (sp-boulogne@hauts-de-seine.gouv.fr), appointments are typically released:
- **Every Monday between 4:00 PM and 7:00 PM**
- If Monday is a holiday, appointments are released the next business day

**Recommendation**: Start the monitor 15-30 minutes before the expected release time.

## Quick Start

### First time setup
```bash
# Run the setup script (creates virtual environment and installs dependencies)
./setup.sh
```

### Run the monitor
```bash
# Option 1: Use the start script
./start_monitor.sh

# Option 2: Manual activation
source .venv/bin/activate
python main.py
```

## How to use

1. **Start the monitor** using one of the methods above
2. **When CAPTCHA appears**, solve it manually in the browser window
3. **The system continues monitoring** automatically after CAPTCHA
4. **When you hear the alert sound**, slots are available!
5. **IMPORTANT**: Close the bot and open the appointment link in a **normal Chrome browser**
6. **Press `Ctrl+C`** to stop the monitor

### ⚠️ **Critical Tip**
When the system alerts you that slots are available:
- **Close the bot immediately**
- **Open the appointment link in a normal Chrome browser** (not the bot's browser)
- This avoids potential bot detection issues during the actual booking process

## Required Information for Appointment

When booking your appointment, you'll need to provide:

### Personal Information
- **First Name** (Prénom)
- **Last Name** (Nom)
- **Email Address**
- **Phone Number**

### Official Documents
- **N° Étranger** (10-digit number)
  - Get this from: https://administration-etrangers-en-france.interieur.gouv.fr/
  - This is your official foreigner number

### ⚠️ **Important Note for Boulogne-Billancourt**
The Boulogne appointment system has an **incorrect instruction** asking for the **FTE number** (passport number). Be aware of this discrepancy.

### After Booking
- **Check your email** for appointment confirmation
- **Confirm the appointment** by clicking the link in the email

## Features

- 🎵 **Custom sounds** for different events (availability, CAPTCHA, periodic checks)
- 🛡️ **Anti-detection** with random delays and user-agent rotation
- 🔄 **Smart state management** to avoid unnecessary refreshes
- 📱 **System notifications** when slots are available
- 📊 **Detailed logging** with timestamps and check counters

## Configuration

Edit `src/config.py` to customize:
- Check intervals
- URLs
- Anti-detection settings
- Logging preferences

**Configuration files:**
- `src/config.py` - Main configuration
- `config_example.py` - Example configuration file
- `requirements.txt` - Python dependencies

## Requirements

- **macOS** (tested on M4 MacBook Pro)
- **Python 3.8+**
- **Chrome browser**


## Project Structure

```
src/
├── monitor/           # Main monitoring logic
│   ├── core.py       # RDVMonitor class
│   ├── states.py     # State management
│   ├── handlers/     # Event handlers
│   │   ├── availability_handler.py
│   │   ├── captcha_handler.py
│   │   └── page_handlers.py
│   └── utils/        # Utilities
│       ├── delay_utils.py
│       └── page_utils.py
├── config.py         # Configuration
├── driver_manager.py # Chrome driver
├── page_detector.py  # Page type detection
└── utils.py          # General utilities
```




---

**Good luck with your appointment! 🍀** 