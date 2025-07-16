# 🎯 Rendez-vous Monitor

Automated appointment availability monitor for French city hall scheduling.

## What it does

Monitors the Boulogne-Billancourt city hall appointment page and alerts you when slots become available for **Titre de Séjour** scheduling.

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

## How it works

1. **Automatically navigates** to the appointment page
2. **Handles CAPTCHA** - stops and waits for manual input
3. **Monitors continuously** for available slots
4. **Alerts you** with sound and notifications when slots are found

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

- macOS (tested on M4 MacBook Pro)
- Python 3.8+
- Chrome browser
- Internet connection

## Usage

1. Run `./start_monitor.sh` or `python main.py`
2. When CAPTCHA appears, solve it manually in the browser
3. The system will continue monitoring automatically
4. Press `Ctrl+C` to stop

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

## Audio Files

The system includes custom sounds in `assets/`:
- `availability_alert_sound.mp3` - When slots are found
- `appointment_check_sound.mp3` - Periodic checks (version 1)
- `appointment_check_sound_v2.mp3` - Periodic checks (version 2, random selection)
- `captcha_sound.mp3` - When CAPTCHA appears

## Troubleshooting

- **ChromeDriver issues**: The system downloads it automatically
- **Permission errors**: Run `chmod +x main.py`
- **Page not loading**: Check internet connection and URL validity

---

**Good luck with your appointment! 🍀** 