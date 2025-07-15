"""
ChromeDriver manager with Mac ARM64 support and anti-detection
"""
import platform
import os
import subprocess
import time
import json
import pickle
from typing import Optional, List, Callable
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

from .config import config
from .utils import logger, anti_detection


class DriverManager:
    """ChromeDriver manager with advanced configurations"""
    
    def __init__(self):
        self.driver: Optional[uc.Chrome] = None
        self.cookies_file = "saved_cookies.pkl"
    
    def setup_driver(self) -> uc.Chrome:
        """Configures and returns a ChromeDriver instance (now undetected-chromedriver)"""
        try:
            logger.debug("🔧 Creating Chrome options...")
            chrome_options = self._create_chrome_options()
            logger.info("🚀 Starting undetected ChromeDriver...")
            logger.debug(f"🔧 Options count: {len(chrome_options.arguments)}")
            self.driver = uc.Chrome(options=chrome_options, headless=False)
            
            # Configure timeouts
            logger.info(f"⏱️  Setting page load timeout: {config.monitoring.timeout} seconds")
            self.driver.set_page_load_timeout(config.monitoring.timeout)
            logger.info("⏱️  Setting implicit wait: 2 seconds")
            self.driver.implicitly_wait(2)
            
            # Load saved cookies if available
            self._load_cookies()
            
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
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-notifications")
        
        # Enable all content types including images and JavaScript
        logger.debug("🔧 Enabling all content types...")
        prefs = {
            "profile.managed_default_content_settings.images": 1,  # Enable images
            "profile.default_content_setting_values.notifications": 2,  # Disable notifications
            "profile.managed_default_content_settings.stylesheets": 1,  # Enable CSS
            "profile.managed_default_content_settings.cookies": 1,  # Enable cookies
            "profile.managed_default_content_settings.javascript": 1,  # Enable JavaScript
            "profile.managed_default_content_settings.plugins": 1,  # Enable plugins
            "profile.managed_default_content_settings.popups": 2,  # Disable popups
            "profile.managed_default_content_settings.geolocation": 2,  # Disable geolocation
            "profile.managed_default_content_settings.media_stream": 2,  # Disable media stream
        }
        options.add_experimental_option("prefs", prefs)
        
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

    def load_page_async(self, url: str, check_conditions: List[Callable], max_wait: int = 10, check_interval: float = 0.5) -> bool:
        """
        Loads a page asynchronously and checks if specific conditions are met.
        
        Args:
            url: The URL to load
            check_conditions: List of functions that return True when the condition is met
            max_wait: Maximum time to wait in seconds
            check_interval: How often to check conditions in seconds
            
        Returns:
            True if any condition was met, False if timeout
        """
        if not self.driver:
            logger.error("❌ Driver not available for async page load")
            return False
            
        try:
            logger.info(f"🌐 Loading page asynchronously: {url}")
            logger.info(f"⏱️  Max wait time: {max_wait}s, check interval: {check_interval}s")
            
            # Start loading the page (non-blocking)
            self.driver.get(url)
            logger.info("🚀 Page load started")
            
            # Wait and check conditions
            start_time = time.time()
            while time.time() - start_time < max_wait:
                try:
                    # Check each condition
                    for i, condition in enumerate(check_conditions):
                        try:
                            if condition():
                                logger.info(f"✅ Condition {i+1} met after {time.time() - start_time:.2f}s")
                                return True
                        except Exception as e:
                            logger.debug(f"⚠️  Condition {i+1} check failed: {e}")
                    
                    # Wait before next check
                    time.sleep(check_interval)
                    
                except Exception as e:
                    logger.debug(f"⚠️  Error during condition check: {e}")
                    time.sleep(check_interval)
            
            logger.warning(f"⏰ Timeout after {max_wait}s - no conditions met")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error in async page load: {e}")
            return False

    def wait_for_conditions_async(self, check_conditions: List[Callable], max_wait: int = 10, check_interval: float = 0.5) -> bool:
        """
        Waits for specific conditions to be met on the current page.
        
        Args:
            check_conditions: List of functions that return True when the condition is met
            max_wait: Maximum time to wait in seconds
            check_interval: How often to check conditions in seconds
            
        Returns:
            True if any condition was met, False if timeout
        """
        if not self.driver:
            logger.error("❌ Driver not available for condition check")
            return False
            
        try:
            logger.info(f"⏱️  Waiting for conditions (max: {max_wait}s, interval: {check_interval}s)")
            
            # Wait and check conditions
            start_time = time.time()
            while time.time() - start_time < max_wait:
                try:
                    # Check each condition
                    for i, condition in enumerate(check_conditions):
                        try:
                            if condition():
                                logger.info(f"✅ Condition {i+1} met after {time.time() - start_time:.2f}s")
                                return True
                        except Exception as e:
                            logger.debug(f"⚠️  Condition {i+1} check failed: {e}")
                    
                    # Wait before next check
                    time.sleep(check_interval)
                    
                except Exception as e:
                    logger.debug(f"⚠️  Error during condition check: {e}")
                    time.sleep(check_interval)
            
            logger.warning(f"⏰ Timeout after {max_wait}s - no conditions met")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error in condition check: {e}")
            return False

    def wait_for_element_async(self, by: By, value: str, max_wait: int = 10, check_interval: float = 0.5) -> bool:
        """
        Waits for a specific element to appear in the DOM asynchronously.
        
        Args:
            by: Selenium By strategy
            value: Element selector
            max_wait: Maximum time to wait in seconds
            check_interval: How often to check in seconds
            
        Returns:
            True if element found, False if timeout
        """
        if not self.driver:
            return False
            
        def check_element():
            try:
                if self.driver:
                    elements = self.driver.find_elements(str(by), value)
                    return len(elements) > 0
                return False
            except:
                return False
        
        # Create a simple condition check without loading a new page
        start_time = time.time()
        while time.time() - start_time < max_wait:
            try:
                if check_element():
                    logger.info(f"✅ Element found after {time.time() - start_time:.2f}s")
                    return True
                time.sleep(check_interval)
            except Exception as e:
                logger.debug(f"⚠️  Error checking element: {e}")
                time.sleep(check_interval)
        
        logger.warning(f"⏰ Timeout after {max_wait}s - element not found")
        return False

    def wait_for_captcha_image(self, max_wait: int = 10) -> bool:
        """
        Waits for captcha image to appear in the DOM.
        
        Args:
            max_wait: Maximum time to wait in seconds
            
        Returns:
            True if captcha image found, False if timeout
        """
        logger.info("🔍 Waiting for captcha image to appear...")
        
        def check_captcha():
            try:
                # Look for common captcha image selectors
                captcha_selectors = [
                    "img[src*='captcha']",
                    "img[alt*='captcha']",
                    "img[class*='captcha']",
                    "img[id*='captcha']",
                    ".captcha img",
                    "#captcha img",
                    "img[src*='recaptcha']",
                    "img[src*='security']"
                ]
                
                for selector in captcha_selectors:
                    if self.driver:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        if elements:
                            logger.info(f"✅ Captcha image found with selector: {selector}")
                            return True
                
                return False
            except Exception as e:
                logger.debug(f"⚠️  Error checking for captcha: {e}")
                return False
        
        # Create a simple condition check without loading a new page
        start_time = time.time()
        while time.time() - start_time < max_wait:
            try:
                if check_captcha():
                    return True
                time.sleep(0.5)
            except Exception as e:
                logger.debug(f"⚠️  Error checking for captcha: {e}")
                time.sleep(0.5)
        
        logger.warning(f"⏰ Timeout after {max_wait}s - captcha image not found")
        return False
    
    def rotate_session(self):
        """Rotates the driver session (closes and reopens)"""
        if self.driver:
            try:
                logger.info("🔄 Rotating ChromeDriver session...")
                self.driver.quit()
                logger.info("⏳ Waiting 2 seconds for driver closure...")
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
                # Save cookies before closing
                self._save_cookies()
                self.driver.quit()
                logger.info("🛑 ChromeDriver closed")
            except Exception as e:
                logger.error(f"❌ Error closing ChromeDriver: {e}")
    
    def _save_cookies(self):
        """Saves cookies to file for reuse"""
        try:
            if not self.driver:
                return
                
            cookies = self.driver.get_cookies()
            if cookies:
                with open(self.cookies_file, 'wb') as f:
                    pickle.dump(cookies, f)
                logger.info(f"🍪 Saved {len(cookies)} cookies to {self.cookies_file}")
            else:
                logger.info("🍪 No cookies to save")
                
        except Exception as e:
            logger.warning(f"⚠️  Could not save cookies: {e}")
    
    def _load_cookies(self):
        """Loads cookies from file if available"""
        try:
            if not os.path.exists(self.cookies_file):
                logger.info("🍪 No saved cookies found")
                return
                
            with open(self.cookies_file, 'rb') as f:
                cookies = pickle.load(f)
            
            if cookies and self.driver:
                # Load cookies into the driver
                for cookie in cookies:
                    try:
                        self.driver.add_cookie(cookie)
                    except Exception as e:
                        logger.debug(f"⚠️  Could not load cookie {cookie.get('name', 'unknown')}: {e}")
                
                logger.info(f"🍪 Loaded {len(cookies)} cookies from {self.cookies_file}")
            else:
                logger.info("🍪 No valid cookies found in file")
                
        except Exception as e:
            logger.warning(f"⚠️  Could not load cookies: {e}")
    
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
                
            logger.info("🍪 Verifying cookies are enabled...")
            
            # Test cookies by setting a test cookie
            logger.info("🍪 Loading test page for cookie verification...")
            self.driver.get("data:text/html,<html><body>Cookie Test</body></html>")
            logger.info("🍪 Setting test cookie...")
            self.driver.add_cookie({
                'name': 'test_cookie',
                'value': 'enabled'
            })
            
            # Verify cookie was set
            logger.info("🍪 Verifying test cookie was set...")
            cookies = self.driver.get_cookies()
            test_cookie = next((c for c in cookies if c['name'] == 'test_cookie'), None)
            
            if test_cookie:
                logger.info("✅ Cookies are working properly")
            else:
                logger.warning("⚠️  Cookies may not be working properly")
                
        except Exception as e:
            logger.warning(f"⚠️  Could not verify cookies: {e}") 