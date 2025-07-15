"""
Gerenciador do ChromeDriver com suporte a Mac ARM64 e anti-detecção
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
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

from .config import config
from .utils import logger, anti_detection


class DriverManager:
    """Gerenciador do ChromeDriver com configurações avançadas"""
    
    def __init__(self):
        self.driver: Optional[webdriver.Chrome] = None
        self.driver_path: Optional[str] = None
    
    def setup_driver(self) -> webdriver.Chrome:
        """Configura e retorna uma instância do ChromeDriver"""
        try:
            chrome_options = self._create_chrome_options()
            service = self._create_chrome_service()
            
            logger.info("🚀 Iniciando ChromeDriver...")
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Configura timeouts
            self.driver.set_page_load_timeout(config.monitoring.timeout)
            self.driver.implicitly_wait(10)
            
            logger.info("✅ ChromeDriver iniciado com sucesso")
            return self.driver
            
        except Exception as e:
            logger.error(f"❌ Erro ao configurar ChromeDriver: {e}")
            raise
    
    def _create_chrome_options(self) -> Options:
        """Cria opções do Chrome com configurações anti-detecção"""
        options = Options()
        
        # Configurações básicas
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument(f"--window-size={config.chrome.window_size}")
        
        # User agent rotativo
        user_agent = anti_detection.get_next_user_agent()
        options.add_argument(f"--user-agent={user_agent}")
        
        # Desabilitar imagens para carregar mais rápido
        if config.chrome.disable_images:
            prefs = {"profile.managed_default_content_settings.images": 2}
            options.add_experimental_option("prefs", prefs)
        
        # Configurações anti-detecção
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Headers adicionais
        for key, value in config.anti_detection.additional_headers.items():
            options.add_argument(f"--header={key}: {value}")
        
        # Configurações de rede
        options.add_argument("--disable-web-security")
        options.add_argument("--allow-running-insecure-content")
        
        return options
    
    def _create_chrome_service(self) -> Service:
        """Cria serviço do Chrome com suporte a Mac ARM64"""
        try:
            # Detecta se é Mac ARM
            if platform.system() == "Darwin" and platform.machine() == "arm64":
                logger.info("🍎 Detectado Mac ARM64 - Configurando ChromeDriver específico...")
                return self._setup_mac_arm_driver()
            else:
                logger.info("🖥️  Sistema detectado - Usando ChromeDriver padrão...")
                return self._setup_standard_driver()
                
        except Exception as e:
            logger.error(f"❌ Erro ao criar serviço do Chrome: {e}")
            raise
    
    def _setup_mac_arm_driver(self) -> Service:
        """Configura ChromeDriver específico para Mac ARM64"""
        try:
            # Limpa cache anterior se existir
            cache_path = os.path.expanduser("~/.wdm")
            if os.path.exists(cache_path):
                import shutil
                shutil.rmtree(cache_path)
                logger.info("🧹 Cache do webdriver-manager limpo")
            
            # Baixa o ChromeDriver
            driver_path = ChromeDriverManager().install()
            logger.info(f"✅ ChromeDriver baixado: {driver_path}")
            
            # Corrige o caminho se necessário
            if "THIRD_PARTY_NOTICES" in driver_path:
                correct_path = driver_path.replace("THIRD_PARTY_NOTICES.chromedriver", "chromedriver")
                logger.info(f"🔧 Corrigindo caminho para: {correct_path}")
                driver_path = correct_path
            
            # Corrige permissões
            self._fix_driver_permissions(driver_path)
            
            self.driver_path = driver_path
            return Service(driver_path)
            
        except Exception as e:
            logger.error(f"❌ Erro ao configurar driver Mac ARM: {e}")
            raise
    
    def _setup_standard_driver(self) -> Service:
        """Configura ChromeDriver padrão para outros sistemas"""
        try:
            driver_path = ChromeDriverManager().install()
            logger.info(f"✅ ChromeDriver baixado: {driver_path}")
            
            self.driver_path = driver_path
            return Service(driver_path)
            
        except Exception as e:
            logger.error(f"❌ Erro ao configurar driver padrão: {e}")
            raise
    
    def _fix_driver_permissions(self, driver_path: str):
        """Corrige permissões do ChromeDriver"""
        try:
            # Verifica se o arquivo existe
            if not os.path.exists(driver_path):
                logger.error(f"❌ Arquivo do driver não encontrado: {driver_path}")
                return
            
            # Verifica permissões atuais
            stat = os.stat(driver_path)
            if not (stat.st_mode & 0o111):  # Se não é executável
                logger.info(f"🔧 Corrigindo permissões para: {driver_path}")
                
                # Tenta com chmod normal
                try:
                    subprocess.run(["chmod", "+x", driver_path], check=True)
                    logger.info("✅ Permissões corrigidas")
                except subprocess.CalledProcessError:
                    # Se falhar, tenta com sudo
                    logger.warning("⚠️  Tentando corrigir permissões com sudo...")
                    subprocess.run(["sudo", "chmod", "+x", driver_path], check=True)
                    logger.info("✅ Permissões corrigidas com sudo")
            
        except Exception as e:
            logger.error(f"❌ Erro ao corrigir permissões: {e}")
    
    def rotate_session(self):
        """Rotaciona a sessão do driver (fecha e reabre)"""
        if self.driver:
            try:
                logger.info("🔄 Rotacionando sessão do ChromeDriver...")
                self.driver.quit()
                time.sleep(2)  # Aguarda fechamento
                
                # Reseta contadores anti-detecção
                anti_detection.reset_session()
                
                # Recria o driver
                self.setup_driver()
                logger.info("✅ Sessão rotacionada com sucesso")
                
            except Exception as e:
                logger.error(f"❌ Erro ao rotacionar sessão: {e}")
    
    def quit(self):
        """Fecha o driver"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("🛑 ChromeDriver fechado")
            except Exception as e:
                logger.error(f"❌ Erro ao fechar ChromeDriver: {e}")
    
    def get_driver(self) -> Optional[webdriver.Chrome]:
        """Retorna a instância atual do driver"""
        return self.driver
    
    def is_healthy(self) -> bool:
        """Verifica se o driver está funcionando"""
        if not self.driver:
            return False
        
        try:
            # Tenta executar um comando simples
            self.driver.current_url
            return True
        except Exception:
            return False 