"""
ChromeDriver manager with Mac ARM64 support and anti-detection
"""
import platform
import os
import subprocess
import time
from typing import Optional
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .config import config
from .utils import logger, anti_detection


class DriverManager:
    """ChromeDriver manager with advanced configurations"""
    
    def __init__(self):
        self.driver: Optional[uc.Chrome] = None
    
    def setup_driver(self) -> uc.Chrome:
        """Configures and returns a ChromeDriver instance (now undetected-chromedriver)"""
        try:
            logger.debug("🔧 Creating Chrome options...")
            chrome_options = self._create_chrome_options()
            logger.info("🚀 Starting undetected ChromeDriver...")
            logger.debug(f"🔧 Options count: {len(chrome_options.arguments)}")
            self.driver = uc.Chrome(options=chrome_options, headless=False)
            
            # Configure timeouts
            logger.debug(f"⏱️  Setting page load timeout: {config.monitoring.timeout}s")
            self.driver.set_page_load_timeout(config.monitoring.timeout)
            logger.debug("⏱️  Setting implicit wait: 10s")
            self.driver.implicitly_wait(10)
            
            # Enable cookies and verify they work
            self._ensure_cookies_enabled()
            
            logger.info("✅ undetected ChromeDriver started successfully")
            logger.debug(f"🔧 Driver capabilities: {self.driver.capabilities}")
            return self.driver
            
        except Exception as e:
            logger.error(f"❌ Error setting up ChromeDriver: {e}")
            import traceback
            logger.debug(f"📋 Driver setup traceback: {traceback.format_exc()}")
            raise
    
    def _create_chrome_options(self) -> uc.ChromeOptions:
        """Creates Chrome options with anti-detection configurations (for undetected-chromedriver)"""
        logger.debug("🔧 Creating Chrome options...")
        options = uc.ChromeOptions()
        
        # Basic configurations
        logger.debug("🔧 Adding basic configurations...")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument(f"--window-size={config.chrome.window_size}")
        
        # Enable cookies and local storage (important for Cloudflare)
        logger.debug("🔧 Enabling cookies and storage...")
        options.add_argument("--enable-cookies")
        options.add_argument("--enable-local-storage")
        options.add_argument("--enable-session-storage")
        
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
        
        # Additional headers
        if config.anti_detection.additional_headers:
            logger.debug(f"🔧 Adding {len(config.anti_detection.additional_headers)} additional headers...")
            for key, value in config.anti_detection.additional_headers.items():
                options.add_argument(f"--header={key}: {value}")
        
        # Network configurations
        logger.debug("🔧 Adding network configurations...")
        options.add_argument("--disable-web-security")
        options.add_argument("--allow-running-insecure-content")
        
        # Additional human-like behaviors
        logger.debug("🔧 Adding human-like behaviors...")
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--disable-backgrounding-occluded-windows")
        options.add_argument("--disable-renderer-backgrounding")
        options.add_argument("--disable-features=TranslateUI")
        options.add_argument("--disable-ipc-flooding-protection")
        
        logger.debug(f"🔧 Chrome options created with {len(options.arguments)} arguments")
        
        # Log all arguments for debugging
        logger.debug("🔧 Chrome arguments:")
        for i, arg in enumerate(options.arguments):
            logger.debug(f"🔧   {i+1:2d}. {arg}")
        
        return options
    
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
    
    def get_driver(self) -> Optional[uc.Chrome]:
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
                
                # Log complete page source for debugging
                logger.debug("📄 === COMPLETE PAGE SOURCE ===")
                logger.debug(page_source)
                logger.debug("📄 === END COMPLETE PAGE SOURCE ===")
                
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
            
            # Log complete blocked page source
            logger.debug("🚫 === COMPLETE BLOCKED PAGE SOURCE ===")
            logger.debug(page_source)
            logger.debug("🚫 === END COMPLETE BLOCKED PAGE SOURCE ===")
            
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

    def _ensure_cookies_enabled(self):
        """Ensures cookies are properly enabled and working"""
        try:
            if not self.driver:
                logger.warning("⚠️  Driver not available for cookie verification")
                return
                
            logger.debug("🍪 Verifying cookies are enabled...")
            
            # Test cookies by setting a test cookie
            self.driver.get("data:text/html,<html><body>Cookie Test</body></html>")
            self.driver.add_cookie({
                'name': 'test_cookie',
                'value': 'enabled'
            })
            
            # Verify cookie was set
            cookies = self.driver.get_cookies()
            test_cookie = next((c for c in cookies if c['name'] == 'test_cookie'), None)
            
            if test_cookie:
                logger.debug("✅ Cookies are working properly")
            else:
                logger.warning("⚠️  Cookies may not be working properly")
                
        except Exception as e:
            logger.warning(f"⚠️  Could not verify cookies: {e}") 