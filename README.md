# 🎯 Rendez-vous Monitor - Boulogne-Billancourt

Automated system to monitor appointment availability at the Boulogne-Billancourt city hall for **Titre de Séjour** scheduling.

## 🚀 How It Works

The system monitors the city hall's appointment page with an intelligent state-based approach:

### 🔄 **Smart Navigation Flow**
1. **Initial State**: Loads the main page and automatically clicks "Prendre un rendez-vous"
2. **Navigation State**: Waits for the page to load after clicking the button
3. **Captcha Wait State**: When captcha appears, stops refreshing and waits for manual input
4. **Monitoring State**: After captcha, monitors the appointment page for availability changes

### 🛡️ **Anti-Detection Features**
- **Smart refresh** with random delays (10-15 seconds)
- **User-Agent rotation** to appear more human-like
- **Session rotation** to avoid blocks
- **Realistic headers** simulating a real browser
- **Change detection** in the page DOM
- **State-based monitoring** to avoid unnecessary refreshes during captcha

## 🏗️ **Architecture (Refactored)**

The system has been refactored following modern Python development practices:

```
src/
├── monitor/                 # Main monitor package
│   ├── core.py             # RDVMonitor class (main orchestrator)
│   ├── states.py           # MonitorState enum
│   ├── handlers/           # Specialized handlers
│   │   ├── captcha_handler.py      # Captcha detection & handling
│   │   ├── availability_handler.py # Availability detection
│   │   └── page_handlers.py        # Page type handlers
│   └── utils/              # Utilities
│       ├── delay_utils.py  # Delay management
│       └── page_utils.py   # Page operations
├── config.py               # Configuration management
├── driver_manager.py       # Chrome driver management
├── page_detector.py        # Page type detection
└── utils/                  # General utilities
```

### **Benefits of Refactoring**
- **Separation of Concerns**: Each handler has a specific responsibility
- **Maintainability**: Changes are isolated to specific modules
- **Testability**: Each component can be tested independently
- **Readability**: Smaller, focused methods and classes
- **Reusability**: Utilities can be reused across the system

### **Key Components**

#### **RDVMonitor (core.py)**
- Main orchestrator class that manages the entire monitoring process
- Handles state transitions and coordinates between different handlers
- Manages the main monitoring loop and error handling

#### **Handlers**
- **CaptchaHandler**: Detects and manages captcha challenges
- **AvailabilityHandler**: Monitors for available appointment slots
- **PageHandlers**: Handles different page types (blocked, maintenance, error, etc.)

#### **Utilities**
- **DelayManager**: Manages different types of delays (smart, captcha, availability)
- **PageUtils**: Handles page loading, refreshing, and navigation operations

## 📋 Prerequisites

- **macOS** (tested on MacBook Pro M4)
- **Python 3.8+**
- **Chrome** installed
- **pip3** to install dependencies

## ⚙️ Installation

1. **Clone or download the files** to a folder
2. **Run the setup script**:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

The script will:
- Check if Python 3 is installed
- Install all necessary dependencies
- Configure the environment

## 🎮 How to Use

### Run the Monitor
```bash
python3 main.py
```

### 🔄 **New Smart Flow**
1. **Automatic Navigation**: The system automatically clicks "Prendre un rendez-vous"
2. **Captcha Handling**: When captcha appears, the system stops refreshing and waits
3. **Manual Captcha**: Type the captcha manually in the browser
4. **Press Enter**: After completing captcha, press Enter in the terminal
5. **Automatic Monitoring**: The system resumes monitoring for available slots

### Stop the Monitor
Press **Ctrl+C** at any time to stop gracefully.

## 🔧 Features

### ✅ Smart Monitoring
- **Smart refresh** with random delays (10-15 seconds)
- **Change detection** in the page DOM
- **Availability analysis** based on French keywords
- **Page hash** to detect real changes
- **Automatic rotation** of sessions and User-Agents

### 🎯 Availability Detection
The system looks for:
- Buttons with text: "disponible", "réserver", "choisir", "creneau"
- Appointment links
- Availability messages
- Elements indicating free time slots

### 🛑 Easy Control
- **Ctrl+C** to stop instantly
- **Detailed logs** with timestamp
- **Check counter**
- **Clear notifications** when changes are detected

## 📊 Example Output

```
🎯 RENDEZ-VOUS MONITOR - BOULOGNE-BILLANCOURT
============================================================
🚀 Starting Rendez-vous monitor...
📍 URL: https://www.rdv-prefecture.interieur.gouv.fr/rdvpref/reservation/demarche/3720/creneau/
⏱️  Check interval: 5 seconds
🛑 Press Ctrl+C to stop

✅ Page loaded initially
[14:30:15] Check #1 (State: initial) - INITIAL PAGE DETECTED!
🔘 Found button: 'Prendre un rendez-vous'
🔘 Successfully clicked 'Prendre un rendez-vous'
⏳ Navigating to appointment page...

[14:30:20] Check #2 (State: navigating) - Navigated to appointment page
✅ Starting availability monitoring...

[14:30:25] Check #3 (State: monitoring) - No changes

🔐 [14:30:30] CAPTCHA DETECTED! (Check #4)
🔐 Type the captcha manually and press Enter to continue...
[User types captcha and presses Enter]
✅ Captcha completed! Starting availability monitoring...

[14:30:35] Check #5 (State: monitoring) - No changes
[14:30:40] Check #6 (State: monitoring) - No changes

🔄 [14:30:45] CHANGE DETECTED! (Check #7)
🎉 AVAILABLE SLOTS FOUND!
📝 Details: Button found: Réserver
🔗 Open the browser manually to schedule!
```

## ⚡ Advanced Settings

### Change Check Interval
Edit the `config.py` file and modify the monitoring settings:
```python
monitoring = {
    "base_interval": 5,  # seconds
    "url": "https://www.rdv-prefecture.interieur.gouv.fr/rdvpref/reservation/demarche/3720/creneau/"
}
```

### Customize Availability Detection
Edit the `availability_handler.py` file to modify availability detection logic:
```python
# In src/monitor/handlers/availability_handler.py
def check_availability(driver: WebDriver) -> Tuple[bool, str]:
    # Customize your availability detection logic here
```

### Modify Delay Behavior
Edit the `delay_utils.py` file to customize delay strategies:
```python
# In src/monitor/utils/delay_utils.py
class DelayManager:
    # Customize delay intervals and strategies
```

## 🔍 Troubleshooting

### Error: "ChromeDriver not found"
- The system downloads ChromeDriver automatically
- If it fails, install manually: `brew install chromedriver`

### Error: "Permission denied"
- Run: `chmod +x rdv_monitor.py`

### Page doesn't load
- Check your internet connection
- The URL may have changed - check the official website

## 🎯 Usage Tips

1. **Run in background** while working
2. **Keep the terminal visible** to see notifications
3. **Have the official site open** in another tab for quick scheduling
4. **Use during peak hours** (mornings, beginning of week)

## 📝 Logs

The system maintains detailed logs:
- Timestamp of each check
- Check number
- Detected changes
- Errors (if any)

## 🔒 Security

- **Does not store personal data**
- **Does not perform automatic login**
- **Only monitors the public page**
- **Stops immediately with Ctrl+C**

## 🆘 Support

If you encounter problems:
1. Check if all dependencies are installed
2. Confirm Chrome is updated
3. Test the URL manually in the browser
4. Check if the URL hasn't changed on the official website

## 🛠️ Development

### **Code Structure**
The codebase follows modern Python practices with clear separation of concerns:

- **Modular Design**: Each component has a single responsibility
- **Type Hints**: Full type annotation for better IDE support
- **Error Handling**: Comprehensive error handling and logging
- **Configuration**: Centralized configuration management

### **Adding New Features**
1. **New Page Types**: Add to `page_detector.py` and create handler in `page_handlers.py`
2. **New Delay Strategies**: Extend `DelayManager` in `delay_utils.py`
3. **New Availability Logic**: Modify `AvailabilityHandler` in `availability_handler.py`

### **Testing**
Each component can be tested independently:
```python
# Test availability detection
from src.monitor.handlers.availability_handler import AvailabilityHandler
# Test captcha handling
from src.monitor.handlers.captcha_handler import CaptchaHandler
# Test page operations
from src.monitor.utils.page_utils import PageUtils
```

---

**Good luck with your appointment! 🍀** 