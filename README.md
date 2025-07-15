# 🎯 Monitor de Rendez-vous - Boulogne-Billancourt

Sistema automatizado para monitorar a disponibilidade de horários na prefeitura de Boulogne-Billancourt para agendamento de **Titre de Séjour**.

## 🚀 Como Funciona

O sistema monitora a página de agendamento da prefeitura e detecta automaticamente quando novos horários ficam disponíveis, usando técnicas anti-detecção avançadas:

- **Refresh inteligente** com delays aleatórios (10-15 segundos)
- **Rotação de User-Agents** para parecer mais humano
- **Rotação de sessões** para evitar bloqueios
- **Headers realistas** simulando navegador real
- **Detecção de mudanças** no DOM da página

## 📋 Pré-requisitos

- **macOS** (testado no MacBook Pro M4)
- **Python 3.8+**
- **Chrome** instalado
- **pip3** para instalar dependências

## ⚙️ Instalação

1. **Clone ou baixe os arquivos** para uma pasta
2. **Execute o script de configuração**:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

O script vai:
- Verificar se Python 3 está instalado
- Instalar todas as dependências necessárias
- Configurar o ambiente

## 🎮 Como Usar

### Executar o Monitor
```bash
python3 main.py
```

### Parar o Monitor
Pressione **Ctrl+C** a qualquer momento para parar graciosamente.

## 🔧 Funcionalidades

### ✅ Monitoramento Inteligente
- **Refresh inteligente** com delays aleatórios (10-15 segundos)
- **Detecção de mudanças** no DOM da página
- **Análise de disponibilidade** baseada em palavras-chave francesas
- **Hash da página** para detectar mudanças reais
- **Rotação automática** de sessões e User-Agents

### 🎯 Detecção de Disponibilidade
O sistema procura por:
- Botões com texto: "disponible", "réserver", "choisir", "creneau"
- Links de agendamento
- Mensagens de disponibilidade
- Elementos que indicam horários livres

### 🛑 Controle Fácil
- **Ctrl+C** para parar instantaneamente
- **Logs detalhados** com timestamp
- **Contador de verificações**
- **Notificações claras** quando detecta mudanças

## 📊 Exemplo de Saída

```
🎯 MONITOR DE RENDEZ-VOUS - BOULOGNE-BILLANCOURT
============================================================
🚀 Iniciando monitor de Rendez-vous...
📍 URL: https://www.rdv-prefecture.interieur.gouv.fr/rdvpref/reservation/demarche/3720/creneau/
⏱️  Intervalo de verificação: 5 segundos
🛑 Pressione Ctrl+C para parar

✅ Página carregada inicialmente
[14:30:15] Verificação #1 - Sem mudanças
[14:30:20] Verificação #2 - Sem mudanças
[14:30:25] Verificação #3 - Sem mudanças

🔄 [14:30:30] MUDANÇA DETECTADA! (Verificação #4)
🎉 HORÁRIOS DISPONÍVEIS ENCONTRADOS!
📝 Detalhes: Botão encontrado: Réserver
🔗 Abra o navegador manualmente para agendar!
```

## ⚡ Configurações Avançadas

### Alterar Intervalo de Verificação
Edite o arquivo `rdv_monitor.py` e mude a linha:
```python
refresh_interval = 5  # segundos
```

### Personalizar Indicadores de Disponibilidade
Edite a lista `availability_indicators` no método `check_for_availability()`.

## 🔍 Troubleshooting

### Erro: "ChromeDriver not found"
- O sistema baixa automaticamente o ChromeDriver
- Se falhar, instale manualmente: `brew install chromedriver`

### Erro: "Permission denied"
- Execute: `chmod +x rdv_monitor.py`

### Página não carrega
- Verifique sua conexão com a internet
- A URL pode ter mudado - verifique no site oficial

## 🎯 Dicas de Uso

1. **Execute em segundo plano** enquanto trabalha
2. **Mantenha o terminal visível** para ver as notificações
3. **Tenha o site oficial aberto** em outra aba para agendar rapidamente
4. **Use em horários de pico** (manhãs, início de semana)

## 📝 Logs

O sistema mantém logs detalhados:
- Timestamp de cada verificação
- Número da verificação
- Mudanças detectadas
- Erros (se houver)

## 🔒 Segurança

- **Não armazena dados pessoais**
- **Não faz login automático**
- **Apenas monitora a página pública**
- **Para imediatamente com Ctrl+C**

## 🆘 Suporte

Se encontrar problemas:
1. Verifique se todas as dependências estão instaladas
2. Confirme que o Chrome está atualizado
3. Teste a URL manualmente no navegador
4. Verifique se a URL não mudou no site oficial

---

**Boa sorte com seu agendamento! 🍀** 