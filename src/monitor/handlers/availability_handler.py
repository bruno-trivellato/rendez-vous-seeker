"""
Availability handler for the monitor
"""
from typing import Tuple
from selenium.webdriver.remote.webdriver import WebDriver

from ...utils import logger, notification_utils


class AvailabilityHandler:
    """Handles availability detection and notifications"""
    
    @staticmethod
    def check_availability(driver: WebDriver) -> Tuple[bool, str]:
        """Checks if there are available slots on the page"""
        try:
            if driver is None:
                return False, "Driver not available"
                
            page_text = driver.page_source.lower()
            
            # NOVA LÓGICA: Se encontrar "aucun créneau disponible", não há agenda
            if "aucun créneau disponible" in page_text:
                return False, "Aucun créneau disponible found - no slots available"
            
            # Se não encontrou "aucun créneau disponible", significa que há agenda disponível
            return True, "No 'Aucun créneau disponible' found - slots are available"
            
        except Exception as e:
            logger.error(f"❌ Error checking availability: {e}")
            return False, f"Error: {e}"
    
    @staticmethod
    def handle_availability_detected(timestamp: str, check_count: int, page_info: dict) -> None:
        """Handles when availability is detected"""
        logger.info(f"\n🎉 [{timestamp}] AVAILABLE SLOTS! (Check #{check_count})")
        logger.info(f"📝 Details: {page_info['description']}")
        
        # Sound and visual notification (3x for availability)
        notification_utils.play_sound(3, "availability")
        notification_utils.show_notification(
            "RDV Monitor - AVAILABLE SLOTS!", 
            "Open the browser to schedule!"
        )
        
        # Show availability details
        availability_details = page_info.get('availability_details', {})
        if availability_details.get('buttons'):
            logger.info(f"🔘 Buttons: {', '.join(availability_details['buttons'])}")
        if availability_details.get('links'):
            logger.info(f"🔗 Links: {', '.join(availability_details['links'])}")
        
        logger.info("🔗 Open the browser manually to schedule!")
        logger.info("🔊 Sound will continue playing every 30 seconds until you stop the monitor...")
    
    @staticmethod
    def handle_availability_reminder(timestamp: str, check_count: int) -> None:
        """Handles availability reminder (when slots are still available)"""
        logger.info(f"🔊 [{timestamp}] Reminder: Slots are still available! (Check #{check_count})")
        notification_utils.play_sound(3, "availability")
    
    @staticmethod
    def handle_availability_lost(timestamp: str) -> None:
        """Handles when availability is lost"""
        logger.info(f"📄 [{timestamp}] Slots are no longer available, resuming normal monitoring...")
    
    @staticmethod
    def handle_appointment_page_check(driver: WebDriver, timestamp: str, check_count: int) -> Tuple[bool, str]:
        """Handles checking appointment page for availability"""
        logger.info(f"📄 [{timestamp}] Appointment page detected - checking for available slots...")
        
        # Check for available slots
        is_available, details = AvailabilityHandler.check_availability(driver)
        if is_available:
            logger.info(f"🎉 [{timestamp}] AVAILABLE SLOTS FOUND! (Check #{check_count})")
            logger.info(f"📝 Details: {details}")
            
            # Sound and visual notification (3x for availability)
            notification_utils.play_sound(3, "availability")
            notification_utils.show_notification(
                "RDV Monitor - AVAILABLE SLOTS!", 
                "Open the browser to schedule!"
            )
            
            logger.info("🔗 Open the browser manually to schedule!")
            logger.info("🔊 Sound will continue playing every 30 seconds until you stop the monitor...")
        
        return is_available, details 