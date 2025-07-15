# 🎵 Custom Audio Setup

## How to use your own notification sound

The system now supports a custom sound when appointment slots are found!

### 📁 Audio Files

- **Availability sound**: `notification_sound.mp3`
- **CAPTCHA sound**: `captcha_sound.mp3`
- **Location**: `assets/` folder in the project root
- **Format**: MP3 (recommended)

### 🔧 How to configure

1. **Place your audio files** in the `assets/` folder with the exact names
2. **The system will automatically detect** and use your custom sounds
3. **If the files don't exist**, the system will use the default system sound

### 🎯 When the sounds play

- **Availability sound**: When appointment slots are found (3x)
- **CAPTCHA sound**: When CAPTCHA is detected (1x)
- **Default sound**: For other notifications

### 💡 Tips

- Use MP3 files for better compatibility
- Keep the file small (< 1MB) for fast loading
- Test the sound before using: `python -c "from src.utils import notification_utils; notification_utils.play_sound(1, 'availability')"`

### 🚫 Ignored files

Audio files are automatically ignored by Git (won't be committed) to keep the repository clean. 