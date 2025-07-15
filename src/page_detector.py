"""
Detector de páginas do sistema de Rendez-vous
Identifica em qual estado/página estamos no sistema da prefeitura
"""
from enum import Enum
from typing import Optional, Tuple
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

from .utils import logger


class PageType(Enum):
    """Tipos de páginas possíveis no sistema"""
    UNKNOWN = "unknown"
    BLOCKED = "blocked"  # Página de bloqueio Cloudflare
    MAINTENANCE = "maintenance"  # Página de manutenção
    ERROR = "error"  # Página de erro genérica
    LOADING = "loading"  # Página carregando
    AVAILABLE = "available"  # Página com horários disponíveis
    UNAVAILABLE = "unavailable"  # Página sem horários
    LOGIN_REQUIRED = "login_required"  # Página pedindo login
    CAPTCHA = "captcha"  # Página com captcha
    INITIAL = "initial"  # Página inicial


class PageDetector:
    """Detector de páginas do sistema"""
    
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
        Detecta o tipo da página atual
        
        Returns:
            Tuple[PageType, str]: Tipo da página e descrição
        """
        try:
            # Pega o HTML da página
            page_source = driver.page_source.lower()
            page_title = driver.title.lower()
            
            # Verifica se está bloqueado (Cloudflare)
            if self._is_blocked(page_source, page_title):
                return PageType.BLOCKED, "Página bloqueada pelo Cloudflare"
            
            # Verifica se está em manutenção
            if self._is_maintenance(page_source, page_title):
                return PageType.MAINTENANCE, "Página em manutenção"
            
            # Verifica se há erro
            if self._is_error(page_source, page_title):
                return PageType.ERROR, "Página de erro"
            
            # Verifica se está carregando
            if self._is_loading(page_source, page_title):
                return PageType.LOADING, "Página carregando"
            
            # Verifica se precisa de login
            if self._is_login_required(page_source, page_title):
                return PageType.LOGIN_REQUIRED, "Login necessário"
            
            # Verifica se é página de captcha
            if self._is_captcha(page_source, page_title):
                return PageType.CAPTCHA, "Página com captcha - intervenção manual necessária"
            
            # Verifica se é página inicial
            if self._is_initial(page_source, page_title):
                return PageType.INITIAL, "Página inicial - clique em 'Prendre un rendez-vous'"
            
            # Verifica se há horários disponíveis
            if self._is_available(page_source, page_title):
                return PageType.AVAILABLE, "Horários disponíveis detectados"
            
            # Se chegou até aqui, provavelmente é a página normal sem disponibilidade
            return PageType.UNAVAILABLE, "Página normal - sem horários disponíveis"
            
        except Exception as e:
            logger.error(f"❌ Erro ao detectar tipo da página: {e}")
            return PageType.UNKNOWN, f"Erro na detecção: {e}"
    
    def _is_blocked(self, page_source: str, page_title: str) -> bool:
        """Verifica se a página está bloqueada pelo Cloudflare"""
        for indicator in self.blocked_indicators:
            if indicator in page_source or indicator in page_title:
                return True
        return False
    
    def _is_maintenance(self, page_source: str, page_title: str) -> bool:
        """Verifica se a página está em manutenção"""
        for indicator in self.maintenance_indicators:
            if indicator in page_source or indicator in page_title:
                return True
        return False
    
    def _is_error(self, page_source: str, page_title: str) -> bool:
        """Verifica se é uma página de erro"""
        for indicator in self.error_indicators:
            if indicator in page_source or indicator in page_title:
                return True
        return False
    
    def _is_loading(self, page_source: str, page_title: str) -> bool:
        """Verifica se a página está carregando"""
        for indicator in self.loading_indicators:
            if indicator in page_source or indicator in page_title:
                return True
        return False
    
    def _is_login_required(self, page_source: str, page_title: str) -> bool:
        """Verifica se precisa de login"""
        for indicator in self.login_indicators:
            if indicator in page_source or indicator in page_title:
                return True
        return False
    
    def _is_captcha(self, page_source: str, page_title: str) -> bool:
        """Verifica se é página de captcha"""
        for indicator in self.captcha_indicators:
            if indicator in page_source or indicator in page_title:
                return True
        return False
    
    def _is_initial(self, page_source: str, page_title: str) -> bool:
        """Verifica se é página inicial"""
        for indicator in self.initial_indicators:
            if indicator in page_source or indicator in page_title:
                return True
        return False
    
    def _is_available(self, page_source: str, page_title: str) -> bool:
        """Verifica se há horários disponíveis"""
        for indicator in self.availability_indicators:
            if indicator in page_source or indicator in page_title:
                return True
        return False
    
    def get_page_info(self, driver: WebDriver) -> dict:
        """
        Retorna informações detalhadas sobre a página atual
        
        Returns:
            dict: Informações da página
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
            
            # Adiciona informações específicas baseadas no tipo
            if page_type == PageType.BLOCKED:
                info["blocked_reason"] = self._get_blocked_reason(driver)
            elif page_type == PageType.AVAILABLE:
                info["availability_details"] = self._get_availability_details(driver)
            
            return info
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter informações da página: {e}")
            return {
                "type": PageType.UNKNOWN,
                "description": f"Erro: {e}",
                "title": "Erro",
                "url": "Erro",
                "status_code": None
            }
    
    def _get_status_code(self, driver: WebDriver) -> Optional[int]:
        """Tenta obter o código de status HTTP"""
        try:
            # Selenium não expõe diretamente o status code, mas podemos tentar detectar
            page_source = driver.page_source.lower()
            
            if "404" in page_source:
                return 404
            elif "500" in page_source:
                return 500
            elif "503" in page_source:
                return 503
            else:
                return 200  # Assumimos 200 se não detectamos erro
                
        except Exception:
            return None
    
    def _get_blocked_reason(self, driver: WebDriver) -> str:
        """Extrai a razão do bloqueio"""
        try:
            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Procura por elementos que indicam a razão do bloqueio
            blocked_indicators = ["security solution", "triggered", "blocked", "protection"]
            for text in soup.stripped_strings:
                if any(indicator in text.lower() for indicator in blocked_indicators):
                    return text.strip()
            else:
                return "Razão não especificada"
                
        except Exception as e:
            return f"Erro ao extrair razão: {e}"
    
    def _get_availability_details(self, driver: WebDriver) -> dict:
        """Extrai detalhes sobre a disponibilidade"""
        try:
            details = {
                "buttons": [],
                "links": [],
                "text_indicators": []
            }
            
            # Procura por botões de agendamento
            buttons = driver.find_elements(By.TAG_NAME, "button")
            for button in buttons:
                button_text = button.text.lower()
                if any(indicator in button_text for indicator in self.availability_indicators):
                    details["buttons"].append(button.text)
            
            # Procura por links de agendamento
            links = driver.find_elements(By.TAG_NAME, "a")
            for link in links:
                link_text = link.text.lower()
                if any(indicator in link_text for indicator in self.availability_indicators):
                    details["links"].append(link.text)
            
            # Procura por indicadores no texto
            page_text = driver.page_source.lower()
            for indicator in self.availability_indicators:
                if indicator in page_text:
                    details["text_indicators"].append(indicator)
            
            return details
            
        except Exception as e:
            return {"error": f"Erro ao extrair detalhes: {e}"}


# Instância global
page_detector = PageDetector() 