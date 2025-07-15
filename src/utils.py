"""
Utilities for the Rendez-vous Monitor
"""
import time
import random
import logging
import os
import subprocess
from datetime import datetime
from typing import Optional
from logging.handlers import RotatingFileHandler
from .config import config


class Logger:
    """Custom logger for the monitor"""
    
    def __init__(self, name: str = "RDVMonitor"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(config.logging.level.value)
        
        # Prevent duplicate handlers
        if self.logger.handlers:
            return
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(config.logging.level.value)
        
        # Log format
        formatter = logging.Formatter(config.logging.log_format)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler with rotation (if configured)
        if config.logging.log_to_file:
            try:
                file_handler = RotatingFileHandler(
                    config.logging.log_file,
                    maxBytes=config.logging.max_log_size,
                    backupCount=config.logging.backup_count
                )
                file_handler.setLevel(config.logging.level.value)
                file_handler.setFormatter(formatter)
                self.logger.addHandler(file_handler)
                self.logger.info(f"📝 File logging enabled: {config.logging.log_file}")
            except Exception as e:
                self.logger.error(f"❌ Failed to setup file logging: {e}")
        
        # Log startup information
        self.logger.info("🚀 Logger initialized")
        self.logger.debug(f"🔧 Log level: {config.logging.level.value}")
        self.logger.debug(f"📁 Log file: {config.logging.log_file if config.logging.log_to_file else 'Disabled'}")
    
    def info(self, message: str):
        """Information log"""
        self.logger.info(message)
    
    def warning(self, message: str):
        """Warning log"""
        self.logger.warning(message)
    
    def error(self, message: str):
        """Error log"""
        self.logger.error(message)
    
    def debug(self, message: str):
        """Debug log"""
        self.logger.debug(message)


class AntiDetectionUtils:
    """Utilities to avoid bot detection"""
    
    def __init__(self):
        self.current_user_agent_index = 0
        self.request_count = 0
        self.session_start_time = time.time()
    
    def get_random_delay(self) -> float:
        """Returns a random delay between min and max"""
        if not config.anti_detection.enable_random_delays:
            return 0
        
        return random.uniform(
            config.monitoring.min_random_delay,
            config.monitoring.max_random_delay
        )
    
    def get_next_user_agent(self) -> str:
        """Returns the next user agent from the list (rotation)"""
        if not config.anti_detection.enable_user_agent_rotation:
            return config.chrome.user_agents[0] if config.chrome.user_agents else ""
        
        if config.chrome.user_agents:
            user_agent = config.chrome.user_agents[self.current_user_agent_index]
            self.current_user_agent_index = (self.current_user_agent_index + 1) % len(config.chrome.user_agents)
            return user_agent
        return ""
    
    def should_rotate_session(self) -> bool:
        """Checks if session should be rotated"""
        if not config.anti_detection.enable_session_rotation:
            return False
        
        self.request_count += 1
        return (
            self.request_count % config.anti_detection.session_rotation_interval == 0 or
            time.time() - self.session_start_time > 3600  # 1 hour
        )
    
    def reset_session(self):
        """Resets session counters"""
        self.request_count = 0
        self.session_start_time = time.time()


class TimeUtils:
    """Time-related utilities"""
    
    @staticmethod
    def get_timestamp() -> str:
        """Returns formatted timestamp"""
        return datetime.now().strftime("%H:%M:%S")
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """Formats duration in seconds to readable string"""
        if seconds < 60:
            return f"{seconds:.1f}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}m"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}h"


class HashUtils:
    """Utilities for hash and content comparison"""
    
    @staticmethod
    def normalize_content(content: str) -> str:
        """Normalizes content by removing dynamic elements"""
        import re
        
        # Remove timestamps
        content = re.sub(r'\d{1,2}:\d{2}:\d{2}', '', content)
        content = re.sub(r'\d{4}-\d{2}-\d{2}', '', content)
        
        # Remove dynamic IDs
        content = re.sub(r'id="[^"]*"', '', content)
        content = re.sub(r'data-[^=]*="[^"]*"', '', content)
        
        # Remove extra spaces
        content = re.sub(r'\s+', ' ', content)
        
        return content.strip()
    
    @staticmethod
    def calculate_similarity(hash1: str, hash2: str) -> float:
        """Calculates similarity between two hashes"""
        if hash1 == hash2:
            return 1.0
        
        # Simple implementation - can be improved
        return 0.0


class NotificationUtils:
    """Utilities for notifications"""
    
    @staticmethod
    def play_sound(times: int = 1, sound_type: str = "default"):
        """Plays a notification sound"""
        try:
            for i in range(times):
                # Try different sound commands based on system
                if os.name == 'posix':  # macOS/Linux
                    if sound_type == "availability":
                        # Use custom sound for availability
                        sound_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "notification_sound.mp3")
                        if os.path.exists(sound_file):
                            subprocess.run(['afplay', sound_file], 
                                         capture_output=True, timeout=10)
                        else:
                            # Fallback to default sound
                            subprocess.run(['afplay', '/System/Library/Sounds/Ping.aiff'], 
                                         capture_output=True, timeout=5)
                    elif sound_type == "appointment_check":
                        # Use custom sound for appointment check (every 10 checks) - randomly choose between v1 and v2
                        import random
                        sound_files = [
                            os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "appointment_check_sound.mp3"),
                            os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "appointment_check_sound_v2.mp3")
                        ]
                        
                        # Filter only existing files
                        existing_sounds = [f for f in sound_files if os.path.exists(f)]
                        
                        if existing_sounds:
                            # Randomly choose one of the available sounds
                            chosen_sound = random.choice(existing_sounds)
                            subprocess.run(['afplay', chosen_sound], 
                                         capture_output=True, timeout=10)
                        else:
                            # Fallback to default sound
                            subprocess.run(['afplay', '/System/Library/Sounds/Ping.aiff'], 
                                         capture_output=True, timeout=5)
                    elif sound_type == "captcha":
                        # Use custom sound for captcha
                        sound_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "captcha_sound.mp3")
                        if os.path.exists(sound_file):
                            subprocess.run(['afplay', sound_file], 
                                         capture_output=True, timeout=10)
                        else:
                            # Fallback to default sound
                            subprocess.run(['afplay', '/System/Library/Sounds/Ping.aiff'], 
                                         capture_output=True, timeout=5)
                    else:
                        # Default sound for other notifications
                        subprocess.run(['afplay', '/System/Library/Sounds/Ping.aiff'], 
                                     capture_output=True, timeout=5)
                else:  # Windows
                    # Try PowerShell to play sound
                    subprocess.run(['powershell', '-c', '[console]::beep(800,500)'], 
                                 capture_output=True, timeout=5)
                
                # Small delay between sounds if playing multiple times
                if i < times - 1:  # Don't sleep after the last sound
                    time.sleep(0.3)
        except Exception as e:
            logger.debug(f"⚠️  Could not play sound: {e}")
    
    @staticmethod
    def show_notification(title: str, message: str):
        """Shows system notification"""
        try:
            if os.name == 'posix':  # macOS/Linux
                subprocess.run(['osascript', '-e', 
                              f'display notification "{message}" with title "{title}"'], 
                             capture_output=True, timeout=5)
            else:  # Windows
                subprocess.run(['powershell', '-c', 
                              f'[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null; [Windows.UI.Notifications.ToastNotification, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null; [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null; $template = \'<toast><visual><binding template="ToastText01"><text id="1">{message}</text></binding></visual></toast>\'; $xml = New-Object Windows.Data.Xml.Dom.XmlDocument; $xml.LoadXml($template); $toast = New-Object Windows.UI.Notifications.ToastNotification $xml; [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("{title}").Show($toast);'], 
                             capture_output=True, timeout=10)
        except Exception as e:
            logger.debug(f"⚠️  Could not show notification: {e}")


# Global instances
logger = Logger()
anti_detection = AntiDetectionUtils()
time_utils = TimeUtils()
hash_utils = HashUtils()
notification_utils = NotificationUtils() 