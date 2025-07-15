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
            logger.debug("🔧 Creating Chrome options...")
            chrome_options = self._create_chrome_options()
            logger.debug("🔧 Creating Chrome service...")
            service = self._create_chrome_service()
            
            logger.info("🚀 Starting ChromeDriver...")
            logger.debug(f"🔧 Service path: {service.path}")
            logger.debug(f"🔧 Options count: {len(chrome_options.arguments)}")
            
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Configure timeouts
            logger.debug(f"⏱️  Setting page load timeout: {config.monitoring.timeout}s")
            self.driver.set_page_load_timeout(config.monitoring.timeout)
            logger.debug("⏱️  Setting implicit wait: 10s")
            self.driver.implicitly_wait(10)
            
            logger.info("✅ ChromeDriver started successfully")
            logger.debug(f"🔧 Driver capabilities: {self.driver.capabilities}")
            return self.driver
            
        except Exception as e:
            logger.error(f"❌ Error setting up ChromeDriver: {e}")
            import traceback
            logger.debug(f"📋 Driver setup traceback: {traceback.format_exc()}")
            raise
    
    def _create_chrome_options(self) -> Options:
        """Creates Chrome options with anti-detection configurations"""
        logger.debug("🔧 Creating Chrome options...")
        options = Options()
        
        # Basic configurations
        logger.debug("🔧 Adding basic configurations...")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument(f"--window-size={config.chrome.window_size}")
        
        # Rotating user agent
        user_agent = anti_detection.get_next_user_agent()
        logger.debug(f"🔧 Using user agent: {user_agent[:50]}...")
        options.add_argument(f"--user-agent={user_agent}")
        
        # Disable images to load faster
        if config.chrome.disable_images:
            logger.debug("🔧 Disabling images for faster loading...")
            prefs = {"profile.managed_default_content_settings.images": 2}
            options.add_experimental_option("prefs", prefs)
        
        # Anti-detection configurations
        logger.debug("🔧 Adding anti-detection configurations...")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Additional headers
        if config.anti_detection.additional_headers:
            logger.debug(f"🔧 Adding {len(config.anti_detection.additional_headers)} additional headers...")
            for key, value in config.anti_detection.additional_headers.items():
                options.add_argument(f"--header={key}: {value}")
        
        # Network configurations
        logger.debug("🔧 Adding network configurations...")
        options.add_argument("--disable-web-security")
        options.add_argument("--allow-running-insecure-content")
        
        logger.debug(f"🔧 Chrome options created with {len(options.arguments)} arguments")
        
        # Log all arguments for debugging
        logger.debug("🔧 Chrome arguments:")
        for i, arg in enumerate(options.arguments):
            logger.debug(f"🔧   {i+1:2d}. {arg}")
        
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
    
    def log_request_details(self, url: Optional[str] = None):
        """Logs detailed request and response information"""
        if not self.driver:
            return
        
        try:
            if url is None:
                url = self.driver.current_url
            
            logger.debug("📊 === REQUEST/RESPONSE DETAILS ===")
            logger.debug(f"🌐 URL: {url}")
            
            # Get current page info
            try:
                title = self.driver.title
                logger.debug(f"📄 Page title: {title}")
            except Exception as e:
                logger.debug(f"❌ Could not get title: {e}")
            
            # Get page source length
            try:
                page_source = self.driver.page_source
                logger.debug(f"📄 Page source length: {len(page_source)} characters")
                
                # Log first 500 characters of page source for analysis
                preview = page_source[:500].replace('\n', ' ').replace('\r', ' ')
                logger.debug(f"📄 Page preview: {preview}...")
                
            except Exception as e:
                logger.debug(f"❌ Could not get page source: {e}")
            
            # Try to get response headers (limited in Selenium)
            try:
                # Get cookies
                cookies = self.driver.get_cookies()
                logger.debug(f"🍪 Cookies count: {len(cookies)}")
                for cookie in cookies[:3]:  # Log first 3 cookies
                    logger.debug(f"🍪 Cookie: {cookie.get('name', 'unknown')} = {cookie.get('value', 'unknown')[:50]}...")
                
            except Exception as e:
                logger.debug(f"❌ Could not get cookies: {e}")
            
            # Log current Chrome options
            try:
                capabilities = self.driver.capabilities
                logger.debug(f"🔧 Browser: {capabilities.get('browserName', 'unknown')}")
                logger.debug(f"🔧 Version: {capabilities.get('browserVersion', 'unknown')}")
                logger.debug(f"🔧 Platform: {capabilities.get('platformName', 'unknown')}")
            except Exception as e:
                logger.debug(f"❌ Could not get capabilities: {e}")
            
            logger.debug("📊 === END REQUEST/RESPONSE DETAILS ===")
            
        except Exception as e:
            logger.error(f"❌ Error logging request details: {e}")
    
    def log_blocked_page_content(self):
        """Logs detailed content when page is blocked"""
        if not self.driver:
            return
        
        try:
            logger.debug("🚫 === BLOCKED PAGE ANALYSIS ===")
            
            # Get full page source
            page_source = self.driver.page_source
            
            # Look for specific Cloudflare indicators
            cloudflare_indicators = [
                "cloudflare",
                "attention required",
                "sorry, you have been blocked",
                "security service",
                "cf-wrapper",
                "cf-error-details",
                "ray id",
                "cloudflare-nginx"
            ]
            
            page_source_lower = page_source.lower()
            found_indicators = []
            
            for indicator in cloudflare_indicators:
                if indicator in page_source_lower:
                    found_indicators.append(indicator)
            
            logger.debug(f"🚫 Cloudflare indicators found: {found_indicators}")
            
            # Extract potential error messages
            import re
            error_patterns = [
                r'<title[^>]*>([^<]+)</title>',
                r'<h1[^>]*>([^<]+)</h1>',
                r'<h2[^>]*>([^<]+)</h2>',
                r'<p[^>]*>([^<]+)</p>'
            ]
            
            for pattern in error_patterns:
                matches = re.findall(pattern, page_source, re.IGNORECASE)
                for match in matches[:3]:  # Limit to first 3 matches
                    clean_match = match.strip()
                    if len(clean_match) > 10:  # Only meaningful text
                        logger.debug(f"🚫 Error text found: {clean_match}")
            
            # Look for Ray ID (Cloudflare tracking)
            ray_id_match = re.search(r'ray id[:\s]*([a-f0-9]+)', page_source, re.IGNORECASE)
            if ray_id_match:
                logger.debug(f"🚫 Cloudflare Ray ID: {ray_id_match.group(1)}")
            
            logger.debug("🚫 === END BLOCKED PAGE ANALYSIS ===")
            
        except Exception as e:
            logger.error(f"❌ Error analyzing blocked page: {e}") 