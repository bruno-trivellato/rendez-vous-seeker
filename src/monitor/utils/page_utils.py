"""
Page utilities for the monitor
"""
import time
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

from ...utils import logger


class PageUtils:
    """Utilities for page operations"""
    
    @staticmethod
    def load_page_async(driver: WebDriver, url: str, driver_manager) -> None:
        """Loads a page asynchronously and waits for essential elements."""
        try:
            logger.info(f"🌐 Loading page asynchronously: {url}")
            
            # Define conditions to check for
            def check_page_loaded():
                try:
                    # Check if page has basic structure
                    return driver.execute_script("return document.readyState") in ["interactive", "complete"]
                except:
                    return False
            
            def check_captcha_available():
                try:
                    # Check if captcha image is available
                    captcha_selectors = [
                        "img[src*='captcha']",
                        "img[alt*='captcha']",
                        "img[class*='captcha']",
                        "img[id*='captcha']",
                        ".captcha img",
                        "#captcha img"
                    ]
                    for selector in captcha_selectors:
                        elements = driver.find_elements(By.CSS_SELECTOR, selector)
                        if elements:
                            return True
                    return False
                except:
                    return False
            
            # Load page first
            driver.get(url)
            logger.info("🚀 Page load started")
            
            # Then wait for conditions
            success = driver_manager.wait_for_conditions_async(
                check_conditions=[check_page_loaded, check_captcha_available],
                max_wait=10,
                check_interval=0.5
            )
            
            if success:
                logger.info("✅ Page loaded asynchronously with essential elements")
            else:
                logger.warning("⚠️  Page loaded but some elements may not be ready")
                
        except TimeoutException:
            logger.info(f"⏰ Async page load timeout for {url} - this is normal, continuing with monitoring...")
            # Don't treat timeout as an error - it's expected behavior
            # The page might still be partially loaded and usable
        except Exception as e:
            logger.error(f"❌ Failed to load page {url} asynchronously: {e}")
            import traceback
            logger.debug(f"📋 Async page load traceback: {traceback.format_exc()}")

    @staticmethod
    def refresh_page_fast(driver: WebDriver) -> None:
        """Refreshes the current page without using driver.get()"""
        try:
            logger.debug("🔄 Refreshing current page...")
            
            # Use JavaScript to refresh the page (more efficient than driver.get())
            driver.execute_script("location.reload();")
            logger.debug("✅ Page refresh initiated")
            
            # Small wait for the refresh to start
            time.sleep(1)
            
        except Exception as e:
            logger.warning(f"⚠️  Error refreshing page: {e}")
            # Fallback to driver.get() if JavaScript refresh fails
            try:
                current_url = driver.current_url
                logger.debug(f"🔄 Fallback: Using driver.get() for {current_url}")
                driver.get(current_url)
            except Exception as fallback_error:
                logger.error(f"❌ Failed to refresh page: {fallback_error}")

    @staticmethod
    def load_page_fast(driver: WebDriver, url: str) -> None:
        """Loads a page without waiting for full page load."""
        try:
            logger.info(f"🌐 Loading page: {url} (fast mode)")
            
            # Set a very short page load timeout for this specific load
            original_timeout = driver.timeouts.page_load
            driver.set_page_load_timeout(5)  # 5 seconds max
            
            try:
                driver.get(url)
                logger.info("✅ Page loaded (fast mode)")
            except TimeoutException:
                logger.info(f"⏰ Fast page load timeout for {url} - this is expected, continuing...")
                # Continue anyway - the page might be partially loaded
            except Exception as e:
                logger.warning(f"⚠️  Unexpected error in fast page load: {e}")
                # Continue anyway - the page might be partially loaded
            finally:
                # Restore original timeout
                driver.set_page_load_timeout(original_timeout)
                
        except Exception as e:
            logger.error(f"❌ Failed to load page {url} (fast mode): {e}")
            import traceback
            logger.debug(f"📋 Fast page load traceback: {traceback.format_exc()}") 