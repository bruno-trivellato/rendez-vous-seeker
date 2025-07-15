"""
ChromeDriver manager with Mac ARM64 support and anti-detection
"""
import platform
import os
import subprocess
import time
from typing import Optional
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from .config import config
from .utils import logger, anti_detection


class DriverManager:
    """ChromeDriver manager with advanced configurations"""
    
    def __init__(self):
        self.driver: Optional[webdriver.Chrome] = None
        self.driver_path: Optional[str] = None
    
    def setup_driver(self) -> webdriver.Chrome:
        """Configures and returns a ChromeDriver instance"""
        try:
            chrome_options = self._create_chrome_options()
            service = self._create_chrome_service()
            
            logger.info("🚀 Starting ChromeDriver...")
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Configure timeouts
            self.driver.set_page_load_timeout(config.monitoring.timeout)
            self.driver.implicitly_wait(10)
            
            logger.info("✅ ChromeDriver started successfully")
            return self.driver
            
        except Exception as e:
            logger.error(f"❌ Error setting up ChromeDriver: {e}")
            raise
    
    def _create_chrome_options(self) -> Options:
        """Creates Chrome options with anti-detection configurations"""
        options = Options()
        
        # Basic configurations
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument(f"--window-size={config.chrome.window_size}")
        
        # Rotating user agent
        user_agent = anti_detection.get_next_user_agent()
        options.add_argument(f"--user-agent={user_agent}")
        
        # Disable images to load faster
        if config.chrome.disable_images:
            prefs = {"profile.managed_default_content_settings.images": 2}
            options.add_experimental_option("prefs", prefs)
        
        # Anti-detection configurations
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Additional headers
        if config.anti_detection.additional_headers:
            for key, value in config.anti_detection.additional_headers.items():
                options.add_argument(f"--header={key}: {value}")
        
        # Network configurations
        options.add_argument("--disable-web-security")
        options.add_argument("--allow-running-insecure-content")
        
        return options
    
    def _create_chrome_service(self) -> Service:
        """Creates Chrome service with Mac ARM64 support"""
        try:
            # Detect if it's Mac ARM
            if platform.system() == "Darwin" and platform.machine() == "arm64":
                logger.info("🍎 Mac ARM64 detected - Configuring specific ChromeDriver...")
                return self._setup_mac_arm_driver()
            else:
                logger.info("🖥️  System detected - Using standard ChromeDriver...")
                return self._setup_standard_driver()
                
        except Exception as e:
            logger.error(f"❌ Error creating Chrome service: {e}")
            raise
    
    def _setup_mac_arm_driver(self) -> Service:
        """Configures specific ChromeDriver for Mac ARM64"""
        try:
            # Clear previous cache if it exists
            cache_path = os.path.expanduser("~/.wdm")
            if os.path.exists(cache_path):
                import shutil
                shutil.rmtree(cache_path)
                logger.info("🧹 webdriver-manager cache cleared")
            
            # Download ChromeDriver
            driver_path = ChromeDriverManager().install()
            logger.info(f"✅ ChromeDriver downloaded: {driver_path}")
            
            # Fix path if necessary
            if "THIRD_PARTY_NOTICES" in driver_path:
                correct_path = driver_path.replace("THIRD_PARTY_NOTICES.chromedriver", "chromedriver")
                logger.info(f"🔧 Fixing path to: {correct_path}")
                driver_path = correct_path
            
            # Fix permissions
            self._fix_driver_permissions(driver_path)
            
            self.driver_path = driver_path
            return Service(driver_path)
            
        except Exception as e:
            logger.error(f"❌ Error setting up Mac ARM driver: {e}")
            raise
    
    def _setup_standard_driver(self) -> Service:
        """Configures standard ChromeDriver for other systems"""
        try:
            driver_path = ChromeDriverManager().install()
            logger.info(f"✅ ChromeDriver downloaded: {driver_path}")
            
            self.driver_path = driver_path
            return Service(driver_path)
            
        except Exception as e:
            logger.error(f"❌ Error setting up standard driver: {e}")
            raise
    
    def _fix_driver_permissions(self, driver_path: str):
        """Fixes ChromeDriver permissions"""
        try:
            # Check if file exists
            if not os.path.exists(driver_path):
                logger.error(f"❌ Driver file not found: {driver_path}")
                return
            
            # Check current permissions
            stat = os.stat(driver_path)
            if not (stat.st_mode & 0o111):  # If not executable
                logger.info(f"🔧 Fixing permissions for: {driver_path}")
                
                # Try with normal chmod
                try:
                    subprocess.run(["chmod", "+x", driver_path], check=True)
                    logger.info("✅ Permissions fixed")
                except subprocess.CalledProcessError:
                    # If it fails, try with sudo
                    logger.warning("⚠️  Trying to fix permissions with sudo...")
                    subprocess.run(["sudo", "chmod", "+x", driver_path], check=True)
                    logger.info("✅ Permissions fixed with sudo")
            
        except Exception as e:
            logger.error(f"❌ Error fixing permissions: {e}")
    
    def rotate_session(self):
        """Rotates the driver session (closes and reopens)"""
        if self.driver:
            try:
                logger.info("🔄 Rotating ChromeDriver session...")
                self.driver.quit()
                time.sleep(2)  # Wait for closure
                
                # Reset anti-detection counters
                anti_detection.reset_session()
                
                # Recreate driver
                self.setup_driver()
                logger.info("✅ Session rotated successfully")
                
            except Exception as e:
                logger.error(f"❌ Error rotating session: {e}")
    
    def quit(self):
        """Closes the driver"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("🛑 ChromeDriver closed")
            except Exception as e:
                logger.error(f"❌ Error closing ChromeDriver: {e}")
    
    def get_driver(self) -> Optional[webdriver.Chrome]:
        """Returns the current driver instance"""
        return self.driver
    
    def is_healthy(self) -> bool:
        """Checks if the driver is working"""
        if not self.driver:
            return False
        
        try:
            # Tries to execute a simple command
            self.driver.current_url
            return True
        except Exception:
            return False 