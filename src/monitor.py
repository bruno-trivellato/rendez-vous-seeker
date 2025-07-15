"""
Monitor principal do sistema de Rendez-vous
"""
import time
import signal
import sys
import hashlib
from typing import Tuple, Optional
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

from .config import config
from .utils import logger, anti_detection, time_utils, hash_utils, notification_utils
from .driver_manager import DriverManager
from .page_detector import page_detector, PageType


class RDVMonitor:
    """Monitor principal para detectar disponibilidade de horários"""
    
    def __init__(self):
        self.driver_manager = DriverManager()
        self.running = True
        self.last_page_hash: Optional[str] = None
        self.check_count = 0
        self.start_time = time.time()
        
        # Configurar signal handler para parar graciosamente
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handler para Ctrl+C e SIGTERM"""
        logger.info("\n🛑 Parando o monitor...")
        self.running = False
        self.driver_manager.quit()
        sys.exit(0)
    
    def start(self):
        """Inicia o monitoramento"""
        try:
            logger.info("🚀 Iniciando monitor de Rendez-vous...")
            logger.info(f"📍 URL: {config.monitoring.url}")
            logger.info(f"⏱️  Intervalo base: {config.monitoring.base_interval} segundos")
            logger.info(f"🎯 Anti-detecção: {'Ativado' if config.anti_detection.enable_random_delays else 'Desativado'}")
            logger.info("🛑 Pressione Ctrl+C para parar\n")
            
            # Inicializa o driver
            self.driver_manager.setup_driver()
            driver = self.driver_manager.get_driver()
            
            if driver is None:
                logger.error("❌ Falha ao inicializar o driver")
                return
            
            # Carrega a página inicial
            driver.get(config.monitoring.url)
            time.sleep(3)  # Aguarda carregamento inicial
            
            # Primeira verificação
            self.last_page_hash = self._get_page_hash(driver)
            logger.info("✅ Página carregada inicialmente")
            
            # Loop principal de monitoramento
            self._monitoring_loop(driver)
            
        except Exception as e:
            logger.error(f"❌ Erro fatal: {e}")
        finally:
            self.driver_manager.quit()
    
    def _monitoring_loop(self, driver):
        """Loop principal de monitoramento"""
        while self.running:
            try:
                # Verifica se deve rotacionar a sessão
                if anti_detection.should_rotate_session():
                    logger.info("🔄 Rotacionando sessão por segurança...")
                    self.driver_manager.rotate_session()
                    driver = self.driver_manager.get_driver()
                    if driver is None:
                        logger.error("❌ Falha ao obter driver após rotação")
                        continue
                    driver.get(config.monitoring.url)
                
                # Refresh da página
                if driver is not None:
                    driver.refresh()
                    time.sleep(2)  # Aguarda carregar
                
                # Detecta o tipo da página atual
                if driver is not None:
                    page_info = page_detector.get_page_info(driver)
                    page_type = page_info["type"]
                    
                    # Gera hash da nova página
                    current_hash = self._get_page_hash(driver)
                    self.check_count += 1
                    
                    timestamp = time_utils.get_timestamp()
                    
                    # Log baseado no tipo da página
                    if page_type == PageType.BLOCKED:
                        logger.warning(f"🚫 [{timestamp}] BLOQUEADO! {page_info['description']}")
                        logger.warning(f"📋 Razão: {page_info.get('blocked_reason', 'Não especificada')}")
                        logger.info("⏳ Aguardando antes da próxima tentativa...")
                        time.sleep(30)  # Espera mais tempo se bloqueado
                        continue
                        
                    elif page_type == PageType.MAINTENANCE:
                        logger.warning(f"🔧 [{timestamp}] MANUTENÇÃO! {page_info['description']}")
                        logger.info("⏳ Aguardando antes da próxima tentativa...")
                        time.sleep(60)  # Espera mais tempo se em manutenção
                        continue
                        
                    elif page_type == PageType.ERROR:
                        logger.error(f"❌ [{timestamp}] ERRO! {page_info['description']}")
                        logger.info("⏳ Aguardando antes da próxima tentativa...")
                        time.sleep(45)  # Espera mais tempo se erro
                        continue
                        
                    elif page_type == PageType.LOADING:
                        logger.info(f"⏳ [{timestamp}] Carregando... {page_info['description']}")
                        time.sleep(5)  # Espera um pouco mais se carregando
                        continue
                        
                    elif page_type == PageType.CAPTCHA:
                        logger.warning(f"\n🔐 [{timestamp}] CAPTCHA DETECTADO! (Verificação #{self.check_count})")
                        logger.warning(f"📝 {page_info['description']}")
                        
                        # Notificação sonora e visual
                        notification_utils.play_sound()
                        notification_utils.show_notification(
                            "RDV Monitor - CAPTCHA", 
                            "Intervenção manual necessária! Digite o captcha."
                        )
                        
                        logger.info("🔐 Digite o captcha manualmente e pressione Enter para continuar...")
                        input("Pressione Enter quando terminar o captcha...")
                        continue
                        
                    elif page_type == PageType.INITIAL:
                        logger.info(f"\n🏠 [{timestamp}] PÁGINA INICIAL DETECTADA! (Verificação #{self.check_count})")
                        logger.info(f"📝 {page_info['description']}")
                        
                        # Tenta clicar no botão "Prendre un rendez-vous"
                        try:
                            from selenium.webdriver.common.by import By
                            buttons = driver.find_elements(By.TAG_NAME, "a")
                            for button in buttons:
                                if "prendre un rendez-vous" in button.text.lower():
                                    logger.info("🔘 Clicando em 'Prendre un rendez-vous'...")
                                    button.click()
                                    time.sleep(3)  # Aguarda carregar
                                    break
                            else:
                                logger.warning("⚠️  Botão 'Prendre un rendez-vous' não encontrado")
                        except Exception as e:
                            logger.error(f"❌ Erro ao clicar no botão: {e}")
                        
                        continue
                        
                    elif page_type == PageType.AVAILABLE:
                        logger.info(f"\n🎉 [{timestamp}] HORÁRIOS DISPONÍVEIS! (Verificação #{self.check_count})")
                        logger.info(f"📝 Detalhes: {page_info['description']}")
                        
                        # Notificação sonora e visual
                        notification_utils.play_sound()
                        notification_utils.show_notification(
                            "RDV Monitor - HORÁRIOS DISPONÍVEIS!", 
                            "Abra o navegador para agendar!"
                        )
                        
                        # Mostra detalhes da disponibilidade
                        availability_details = page_info.get('availability_details', {})
                        if availability_details.get('buttons'):
                            logger.info(f"🔘 Botões: {', '.join(availability_details['buttons'])}")
                        if availability_details.get('links'):
                            logger.info(f"🔗 Links: {', '.join(availability_details['links'])}")
                        
                        logger.info("🔗 Abra o navegador manualmente para agendar!")
                        
                        # Mantém a página aberta para o usuário
                        input("\nPressione Enter para continuar monitorando ou Ctrl+C para parar...")
                        
                    elif page_type == PageType.UNAVAILABLE:
                        if current_hash != self.last_page_hash:
                            logger.info(f"\n🔄 [{timestamp}] MUDANÇA DETECTADA! (Verificação #{self.check_count})")
                            logger.info(f"ℹ️  {page_info['description']}")
                            self.last_page_hash = current_hash
                        else:
                            if config.logging.show_check_count:
                                logger.info(f"[{timestamp}] Verificação #{self.check_count} - {page_info['description']}")
                            else:
                                logger.info(f"[{timestamp}] {page_info['description']}")
                                
                    else:  # UNKNOWN ou outros
                        logger.warning(f"❓ [{timestamp}] Página desconhecida: {page_info['description']}")
                        logger.info(f"📄 Título: {page_info['title']}")
                        logger.info(f"🔗 URL: {page_info['url']}")
                
                # Delay antes da próxima verificação
                self._smart_delay()
                
            except Exception as e:
                logger.error(f"❌ Erro durante monitoramento: {e}")
                self._smart_delay()
    
    def _get_page_hash(self, driver) -> Optional[str]:
        """Gera um hash do conteúdo da página para detectar mudanças"""
        try:
            if driver is None:
                return None
                
            # Aguarda a página carregar
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Pega o HTML da página
            page_source = driver.page_source
            
            # Normaliza o conteúdo
            normalized_content = hash_utils.normalize_content(page_source)
            
            # Remove scripts e elementos dinâmicos
            soup = BeautifulSoup(normalized_content, 'html.parser')
            
            # Remove scripts e styles
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Remove atributos que mudam frequentemente
            for tag in soup.find_all(True):
                for attr in ['data-reactid', 'data-testid', 'id']:
                    if tag.has_attr(attr):
                        del tag[attr]
            
            # Gera hash do conteúdo limpo
            content = str(soup)
            return hashlib.md5(content.encode()).hexdigest()
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar hash da página: {e}")
            return None
    
    def _check_availability(self, driver) -> Tuple[bool, str]:
        """Verifica se há horários disponíveis na página"""
        try:
            if driver is None:
                return False, "Driver não disponível"
                
            page_text = driver.page_source.lower()
            
            # Verifica se há botões de agendamento
            buttons = driver.find_elements(By.TAG_NAME, "button")
            for button in buttons:
                button_text = button.text.lower()
                if config.detection.availability_indicators and any(indicator in button_text for indicator in config.detection.availability_indicators):
                    return True, f"Botão encontrado: {button.text}"
            
            # Verifica se há links de agendamento
            links = driver.find_elements(By.TAG_NAME, "a")
            for link in links:
                link_text = link.text.lower()
                if config.detection.availability_indicators and any(indicator in link_text for indicator in config.detection.availability_indicators):
                    return True, f"Link encontrado: {link.text}"
            
            # Verifica se há mensagens de disponibilidade no texto
            if config.detection.availability_indicators:
                for indicator in config.detection.availability_indicators:
                    if indicator in page_text:
                        return True, f"Indicador encontrado: {indicator}"
            
            return False, "Nenhum horário disponível detectado"
            
        except Exception as e:
            logger.error(f"❌ Erro ao verificar disponibilidade: {e}")
            return False, f"Erro: {e}"
    
    def _smart_delay(self):
        """Implementa delay inteligente com anti-detecção"""
        if config.anti_detection.enable_random_delays:
            delay = anti_detection.get_random_delay()
            logger.debug(f"⏳ Delay aleatório: {delay:.1f}s")
            time.sleep(delay)
        else:
            time.sleep(config.monitoring.base_interval)
    
    def get_stats(self) -> dict:
        """Retorna estatísticas do monitoramento"""
        uptime = time.time() - self.start_time
        return {
            "check_count": self.check_count,
            "uptime": time_utils.format_duration(uptime),
            "checks_per_minute": self.check_count / (uptime / 60) if uptime > 0 else 0
        } 