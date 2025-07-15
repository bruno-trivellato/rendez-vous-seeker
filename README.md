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
Edit the `rdv_monitor.py` file and change the line:
```python
refresh_interval = 5  # seconds
```

### Customize Availability Indicators
Edit the `availability_indicators` list in the `check_for_availability()` method.

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

---

**Good luck with your appointment! 🍀** 