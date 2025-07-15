"""
Page detector for the Rendez-vous system
Identifies which state/page we are on in the city hall system
"""
from enum import Enum
from typing import Optional, Tuple
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

from .utils import logger


class PageType(Enum):
    """Possible page types in the system"""
    UNKNOWN = "unknown"
    BLOCKED = "blocked"  # Cloudflare blocking page
    MAINTENANCE = "maintenance"  # Maintenance page
    ERROR = "error"  # Generic error page
    LOADING = "loading"  # Loading page
    AVAILABLE = "available"  # Page with available slots
    UNAVAILABLE = "unavailable"  # Page without slots
    LOGIN_REQUIRED = "login_required"  # Page asking for login
    CAPTCHA = "captcha"  # Page with captcha
    INITIAL = "initial"  # Initial page


class PageDetector:
    """Page detector for the system"""
    
    def __init__(self):
        self.blocked_indicators = [
            "cloudflare",
            "attention required",
            "sorry, you have been blocked",
            "you are unable to access",
            "security service",
            "cf-wrapper",
            "cf-error-details"
        ]
        
        self.maintenance_indicators = [
            "maintenance",
            "maintenance",
            "indisponible",
            "temporairement",
            "service temporairement indisponible",
            "maintenance en cours"
        ]
        
        self.error_indicators = [
            "erreur",
            "error",
            "page not found",
            "404",
            "500",
            "503",
            "service unavailable"
        ]
        
        self.loading_indicators = [
            "chargement",
            "loading",
            "veuillez patienter",
            "please wait"
        ]
        
        self.availability_indicators = [
            "disponible",
            "available",
            "libre",
            "free",
            "réserver",
            "reserve",
            "choisir",
            "select",
            "creneau",
            "slot",
            "rendez-vous",
            "appointment",
            "horaire",
            "schedule",
            "placer",
            "place"
        ]
        
        self.login_indicators = [
            "connexion",
            "login",
            "se connecter",
            "identifiant",
            "mot de passe",
            "password"
        ]
        
        self.captcha_indicators = [
            "captcha",
            "code de sécurité",
            "recopier le code",
            "captchaformulaireextinput",
            "captchaid",
            "captchausercode"
        ]
        
        self.initial_indicators = [
            "que souhaitez-vous faire",
            "prendre un rendez-vous",
            "gérer mes rendez-vous",
            "étape 1 sur 6"
        ]
    
    def detect_page_type(self, driver: WebDriver) -> Tuple[PageType, str]:
        """
        Detects the current page type
        
        Returns:
            Tuple[PageType, str]: Page type and description
        """
        try:
            # Get page HTML and title
            page_source = driver.page_source.lower()
            page_title = driver.title
            
            # FIRST: Check by title (more reliable)
            # Check if captcha page (página de "Constituez votre dossier")
            if "constituez votre dossier" in page_title.lower():
                logger.info(f"🔍 Page classified as CAPTCHA by title: '{page_title}'")
                return PageType.CAPTCHA, "Page with captcha - manual intervention required"
            
            # Also check for captcha in page content as backup
            if self._is_captcha(page_source, page_title.lower()):
                logger.info(f"🔍 Page classified as CAPTCHA by content indicators: '{page_title}'")
                return PageType.CAPTCHA, "Page with captcha - manual intervention required"
            
            # Check if appointment page (página de "Choisissez votre créneau")
            if "choisissez votre créneau" in page_title.lower():
                logger.info(f"🔍 Page classified as APPOINTMENT by title: '{page_title}'")
                return PageType.UNAVAILABLE, "Appointment page - monitoring for available slots"
            
            # Check if initial page (página inicial)
            if "accueil" in page_title.lower():
                logger.info(f"🔍 Page classified as INITIAL by title: '{page_title}'")
                return PageType.INITIAL, "Initial page - click on 'Prendre un rendez-vous'"
            
            # THEN: Check by content (less reliable)
            # Check if blocked (Cloudflare)
            if self._is_blocked(page_source, page_title.lower()):
                logger.info(f"🔍 Page classified as BLOCKED by content indicators")
                return PageType.BLOCKED, "Page blocked by Cloudflare"
            
            # Check if in maintenance
            if self._is_maintenance(page_source, page_title.lower()):
                logger.info(f"🔍 Page classified as MAINTENANCE by content indicators")
                return PageType.MAINTENANCE, "Page in maintenance"
            
            # Check if there's an error
            if self._is_error(page_source, page_title.lower()):
                logger.info(f"🔍 Page classified as ERROR by content indicators")
                return PageType.ERROR, "Error page"
            
            # Check if loading
            if self._is_loading(page_source, page_title.lower()):
                logger.info(f"🔍 Page classified as LOADING by content indicators")
                return PageType.LOADING, "Page loading"
            
            # Check if login required
            if self._is_login_required(page_source, page_title.lower()):
                logger.info(f"🔍 Page classified as LOGIN_REQUIRED by content indicators")
                return PageType.LOGIN_REQUIRED, "Login required"
            
            # Check if slots available
            if self._is_available(page_source, page_title.lower()):
                logger.info(f"🔍 Page classified as AVAILABLE by content indicators")
                return PageType.AVAILABLE, "Available slots detected"
            
            # If we got here, probably normal page without availability
            logger.info(f"🔍 Page classified as UNAVAILABLE (default) - title: '{page_title}'")
            return PageType.UNAVAILABLE, "Normal page - no available slots"
            
        except Exception as e:
            logger.error(f"❌ Error detecting page type: {e}")
            return PageType.UNKNOWN, f"Detection error: {e}"
    
    def _is_blocked(self, page_source: str, page_title: str) -> bool:
        """Checks if the page is blocked by Cloudflare"""
        for indicator in self.blocked_indicators:
            if indicator in page_source or indicator in page_title:
                logger.info(f"🔍 Found BLOCKED indicator: '{indicator}'")
                return True
        return False
    
    def _is_maintenance(self, page_source: str, page_title: str) -> bool:
        """Checks if the page is in maintenance"""
        for indicator in self.maintenance_indicators:
            if indicator in page_source or indicator in page_title:
                logger.info(f"🔍 Found MAINTENANCE indicator: '{indicator}'")
                return True
        return False
    
    def _is_error(self, page_source: str, page_title: str) -> bool:
        """Checks if it's an error page"""
        for indicator in self.error_indicators:
            if indicator in page_source or indicator in page_title:
                logger.info(f"🔍 Found ERROR indicator: '{indicator}'")
                return True
        return False
    
    def _is_loading(self, page_source: str, page_title: str) -> bool:
        """Checks if the page is loading"""
        for indicator in self.loading_indicators:
            if indicator in page_source or indicator in page_title:
                logger.info(f"🔍 Found LOADING indicator: '{indicator}'")
                return True
        return False
    
    def _is_login_required(self, page_source: str, page_title: str) -> bool:
        """Checks if login is required"""
        for indicator in self.login_indicators:
            if indicator in page_source or indicator in page_title:
                logger.info(f"🔍 Found LOGIN_REQUIRED indicator: '{indicator}'")
                return True
        return False
    
    def _is_captcha(self, page_source: str, page_title: str) -> bool:
        """Checks if it's a captcha page"""
        for indicator in self.captcha_indicators:
            if indicator in page_source or indicator in page_title:
                logger.info(f"🔍 Found CAPTCHA indicator: '{indicator}'")
                return True
        return False
    
    def _is_initial(self, page_source: str, page_title: str) -> bool:
        """Checks if it's an initial page"""
        for indicator in self.initial_indicators:
            if indicator in page_source or indicator in page_title:
                logger.info(f"🔍 Found INITIAL indicator: '{indicator}'")
                return True
        return False
    
    def _is_available(self, page_source: str, page_title: str) -> bool:
        """Checks if slots are available"""
        for indicator in self.availability_indicators:
            if indicator in page_source or indicator in page_title:
                logger.info(f"🔍 Found AVAILABLE indicator: '{indicator}'")
                return True
        return False
    
    def get_page_info(self, driver: WebDriver) -> dict:
        """
        Returns detailed information about the current page
        
        Returns:
            dict: Page information
        """
        try:
            page_type, description = self.detect_page_type(driver)
            
            info = {
                "type": page_type,
                "description": description,
                "title": driver.title,
                "url": driver.current_url,
                "status_code": self._get_status_code(driver)
            }
            
            # Adds specific information based on type
            if page_type == PageType.BLOCKED:
                info["blocked_reason"] = self._get_blocked_reason(driver)
            elif page_type == PageType.AVAILABLE:
                info["availability_details"] = self._get_availability_details(driver)
            
            return info
            
        except Exception as e:
            logger.error(f"❌ Error getting page information: {e}")
            return {
                "type": PageType.UNKNOWN,
                "description": f"Error: {e}",
                "title": "Error",
                "url": "Error",
                "status_code": None
            }
    
    def _get_status_code(self, driver: WebDriver) -> Optional[int]:
        """Attempts to get the HTTP status code"""
        try:
            # Selenium does not expose the status code directly, but we can try to detect
            page_source = driver.page_source.lower()
            
            if "404" in page_source:
                return 404
            elif "500" in page_source:
                return 500
            elif "503" in page_source:
                return 503
            else:
                return 200  # Assume 200 if no error is detected
                
        except Exception:
            return None
    
    def _get_blocked_reason(self, driver: WebDriver) -> str:
        """Extracts the blocking reason"""
        try:
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Searches for elements that indicate the blocking reason
            blocked_indicators = ["security solution", "triggered", "blocked", "protection"]
            for text in soup.stripped_strings:
                if any(indicator in text.lower() for indicator in blocked_indicators):
                    return text.strip()
            else:
                return "Reason unspecified"
                
        except Exception as e:
            return f"Error extracting reason: {e}"
    
    def _get_availability_details(self, driver: WebDriver) -> dict:
        """Extracts details about availability"""
        try:
            details = {
                "buttons": [],
                "links": [],
                "text_indicators": []
            }
            
            # Searches for appointment buttons
            buttons = driver.find_elements(By.TAG_NAME, "button")
            for button in buttons:
                button_text = button.text.lower()
                if any(indicator in button_text for indicator in self.availability_indicators):
                    details["buttons"].append(button.text)
            
            # Searches for appointment links
            links = driver.find_elements(By.TAG_NAME, "a")
            for link in links:
                link_text = link.text.lower()
                if any(indicator in link_text for indicator in self.availability_indicators):
                    details["links"].append(link.text)
            
            # Searches for indicators in the text
            page_text = driver.page_source.lower()
            for indicator in self.availability_indicators:
                if indicator in page_text:
                    details["text_indicators"].append(indicator)
            
            return details
            
        except Exception as e:
            return {"error": f"Error extracting details: {e}"}


# Global instance
page_detector = PageDetector() 