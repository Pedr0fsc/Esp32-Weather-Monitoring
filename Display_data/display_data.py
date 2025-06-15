<<<<<<< HEAD
import time # Vai ser responsável por importar um módulo de tempo
from machine import Pin, reset, freq, ADC, PWM # Importa classes e funções específicas da biblioteca machine para controle de hardware
import st7789_simplified # Importa biblioteca simplificada para controle do display ST7789 
import dht # Importa biblioteca para sensores DHT (temperatura e umidade)
import gc # Coletor de lixo, usado para evitar muitos dados desnecessários para não sobrecarregar o sistema
import network # Importa biblioteca para conectividade WiFi
import uasyncio as asyncio # Importa biblioteca para programação assíncrona
from umqtt.simple import MQTTClient # Importa cliente MQTT simples para comunicação com serviços cloud

# Imprime mensagem de inicialização do sistema
print("=== ESP32 WEATHER STATION ===") # Print para demonstrar que o sistema está sendo iniciado
=======

import time # Vai ser responsável por importar um módulo de tempo
from machine import Pin, reset, freq, ADC, PWM # Importa classes e funções específicas da biblioteca machine para controle de hardware
import st7789_simplified # Importa biblioteca simplificada para controle do display ST7789 
import dht # Importa biblioteca para sensores DHT (temperatura e umidade)
import gc # Coletor de lixo, usado para evitar muitos dados desnecessários para não sobrecarregar o sistema
import network # Importa biblioteca para conectividade WiFi
import uasyncio as asyncio # Importa biblioteca para programação assíncrona
from umqtt.simple import MQTTClient # Importa cliente MQTT simples para comunicação com serviços cloud

# Imprime mensagem de inicialização do sistema
print("=== ESP32 WEATHER STATION ===") # Print para desmontrar que o sistema está sendo iniciado
>>>>>>> 285c4da536864a3ae455a05f95d9c51fcf4eccb5

# ===============================================================
# CONFIGURAÇÕES
# ===============================================================
# Sensores
ENABLE_LDR = True # Inicializa o sensor LDR (Sensor de luminosidade, se está claro ou escuro)
ENABLE_DHT11 = True # Inicializa o sensor DHT11(Sensor de temperatura e umidade)
ENABLE_RAIN_SENSOR = True # Inicializa o sensor de Chuva
<<<<<<< HEAD
WIFI_SSID = "" # Define o nome da rede WiFi (SSID) - deixado em branco para ser preenchido
WIFI_PASSWORD = "" # Define a senha do WIFI
ADAFRUIT_AIO_USERNAME = "" # Usuário do ADAFRUIT
ADAFRUIT_AIO_KEY = "" # Define a chave de acesso do adafruit
MQTT_SERVER = "io.adafruit.com" # Link para inicializar o servidor adafruit

=======
WIFI_SSID = "" # Define o nome da rede WiFi (SSID) - deixado em branco para ser preenchido
WIFI_PASSWORD = "" # Define a senha do WIFI
ADAFRUIT_AIO_USERNAME = "" # Usuário do ADAFRUIT
ADAFRUIT_AIO_KEY = "" # Define a chave de acesso do adatruit
MQTT_SERVER = "io.adafruit.com" # Link para inicializar o servidor adafruit
>>>>>>> 285c4da536864a3ae455a05f95d9c51fcf4eccb5
# Pinos
# Define o pino GPIO 4 para o sensor DHT11
DHT11_PIN = 4 
# Define o pino GPIO 32 para o sensor LDR (analógico)
LDR_PIN = 32
# Define o pino GPIO 34 para o sensor de chuva (analógico)
RAIN_SENSOR_PIN = 34
<<<<<<< HEAD
=======
# Define o pino GPIO 2 para o LED de status
LED_PIN = 2
>>>>>>> 285c4da536864a3ae455a05f95d9c51fcf4eccb5
# Define o pino GPIO 14 para o buzzer
BUZZER_PIN = 14
# Define os pinos para comunicação SPI com o display: SCK, MOSI, RST, DC, BLK
SPI_SCK, SPI_MOSI, RST, DC, BLK = 18, 23, 19, 15, 5
<<<<<<< HEAD

# Pinos dos LEDs
LED_VERDE_PIN = 27         # LED Verde - Sistema OK
LED_VERMELHO_PIN = 12     # LED Vermelho - Alertas críticos
LED_AMARELO_PIN = 13         # LED Amarelo - Chuva/Umidade

# Limites de temperatura (°C)
TEMP_ALERTA_ALTA = 35
TEMP_ALERTA_BAIXA = 5
# Limites de umidade (%)
UMIDADE_ALERTA_ALTA = 85
UMIDADE_ALERTA_BAIXA = 20
# Limites do sensor LDR (luminosidade)
LDR_THRESHOLD_DARK = 500     # Abaixo = noite/escuro
LDR_THRESHOLD_BRIGHT = 2500  # Acima = dia ensolarado
# Limites do sensor de chuva
RAIN_THRESHOLD_DRY = 3000    # Acima = seco
RAIN_THRESHOLD_WET = 1500    # Abaixo = chuva forte

=======
# Define temperatura alta (35°C) e baixa (5°C) para alertas
TEMP_HIGH, TEMP_LOW = 35, 5
# Define umidade alta (85%) e baixa (20%) para alertas
HUMIDITY_HIGH, HUMIDITY_LOW = 85, 20
# Define valores de luminosidade para escuro (500) e claro (2500)
LDR_DARK, LDR_BRIGHT = 500, 2500
>>>>>>> 285c4da536864a3ae455a05f95d9c51fcf4eccb5
# ===============================================================
# CLASSES E VARIÁVEIS GLOBAIS
# ===============================================================

# Define a classe principal da estação meteorológica
class WeatherStation:
    def __init__(self):
        # Inicializa a variável do display como None
        self.display = None
        # Inicializa a variável do sensor DHT como None
        self.dht_sensor = None
        # Inicializa a variável do sensor LDR como None
        self.ldr_sensor = None
        # Inicializa a variável do sensor de chuva como None
        self.rain_sensor = None
<<<<<<< HEAD
        # Inicializa as variáveis dos LEDs como None
        self.led_verde = None
        self.led_vermelho = None
        self.led_amarelo = None
=======
        # Inicializa a variável do LED como None
        self.led = None
>>>>>>> 285c4da536864a3ae455a05f95d9c51fcf4eccb5
        # Inicializa a variável do buzzer como None
        self.buzzer = None
        # Inicializa a variável do cliente MQTT como None
        self.mqtt_client = None
        # Flag para controlar status da conexão WiFi
        self.wifi_connected = False
        # Contador de ciclos do loop principal
        self.loop_count = 0
        
    # Método para inicializar todos os componentes de hardware
    def init_hardware(self):
        """Inicializa todos os componentes de hardware"""
        # Define frequência do processador para 80MHz (economia de energia)
        freq(80000000)  # Reduz frequência para economia de energia
        
        # Display
        # Tenta inicializar o display ST7789
        try:
            # Cria instância do display com os pinos definidos
            self.display = st7789_simplified.ST7789(
                spi_sck=SPI_SCK, spi_mosi=SPI_MOSI, rst=RST, dc=DC, bl=BLK
            )
            # Preenche tela com cor preta
            self.display.fill(self.display.BLACK)
            
            # Exibe texto "WEATHER STATION" na posição (10, 100) com cor verde
            self.display.text("WEATHER STATION", 10, 100, self.display.GREEN)
            
            # Exibe texto "INICIALIZANDO..." na posição (10, 120) com cor branca
            self.display.text("INICIALIZANDO...", 10, 120, self.display.WHITE)
<<<<<<< HEAD
            
            # Imprime confirmação de sucesso na inicialização do display
            print("Display OK")
        # Captura qualquer exceção durante inicialização do display
        except Exception as display_nao_iniciado:
            # Imprime erro na inicialização do display
            print(f"Display erro: {display_nao_iniciado}")
            
        # LEDs de status
        # Tenta inicializar os LEDs
        try:
            # Configura os pinos dos LEDs como saída
            self.led_verde = Pin(LED_VERDE_PIN, Pin.OUT)
            self.led_vermelho = Pin(LED_VERMELHO_PIN, Pin.OUT)
            self.led_amarelo = Pin(LED_AMARELO_PIN, Pin.OUT)
            
            # Desliga todos os LEDs inicialmente
            self.led_verde.off()
            self.led_vermelho.off()
            self.led_amarelo.off()
            
            # Teste inicial dos LEDs (sequência rápida)
            self.led_verde.on()
            time.sleep(0.2)
            self.led_verde.off()
            
            self.led_amarelo.on()
            time.sleep(0.2)
            self.led_amarelo.off()
            
            self.led_vermelho.on()
            time.sleep(0.2)
            self.led_vermelho.off()
            
            # Liga LED verde indicando sistema inicializando
            self.led_verde.on()
            
            # Imprime confirmação de sucesso na inicialização dos LEDs
            print("LEDs OK")
        # Captura qualquer exceção durante inicialização dos LEDs
        except Exception as leds_nao_ligados:
            # Imprime erro na inicialização dos LEDs
            print(f"LEDs erro: {leds_nao_ligados}")
=======
            
            # Imprime confirmação de sucesso na inicialização do display
            print("✓ Display OK")
        # Captura qualquer exceção durante inicialização do display
        except Exception as display_nao_iniciado:
            # Imprime erro na inicialização do display
            print(f"✗ Display erro: {display_nao_iniciado}")
            
        # LED de status
        # Tenta inicializar o LED de status
        try:
            # Configura o pino do LED como saída
            self.led = Pin(LED_PIN, Pin.OUT)
            
            # Liga o LED inicialmente
            self.led.on()
            
            # Imprime confirmação de sucesso na inicialização do LED
            print("✓ LED OK")
        # Captura qualquer exceção durante inicialização do LED
        except Exception as led_nao_ligado:
            # Imprime erro na inicialização do LED
            print(f"✗ LED erro: {led_nao_ligado}")
>>>>>>> 285c4da536864a3ae455a05f95d9c51fcf4eccb5
            
        # Buzzer
        # Tenta inicializar o buzzer
        try:
            # Configura o buzzer como PWM (modulação por largura de pulso)
            self.buzzer = PWM(Pin(BUZZER_PIN))
            
            # Define duty cycle como 0 (buzzer desligado)
            self.buzzer.duty(0)
            
            # Emite um beep de teste (1000Hz por 100ms)
            self.beep(1000, 100)  # Teste
            
            # Imprime confirmação de sucesso na inicialização do buzzer
<<<<<<< HEAD
            print("Buzzer OK")
        # Captura qualquer exceção durante inicialização do buzzer
        except Exception as sem_som:
            # Imprime erro na inicialização do buzzer
            print(f"Buzzer erro: {sem_som}")
=======
            print("✓ Buzzer OK")
        # Captura qualquer exceção durante inicialização do buzzer
        except Exception as sem_som:
            # Imprime erro na inicialização do buzzer
            print(f"✗ Buzzer erro: {sem_som}")
>>>>>>> 285c4da536864a3ae455a05f95d9c51fcf4eccb5
            
        # Sensores
        # Verifica se o sensor DHT11 está habilitado
        if ENABLE_DHT11:
            # Tenta inicializar o sensor DHT11
            try:
                # Cria instância do sensor DHT11 no pino definido
                self.dht_sensor = dht.DHT11(Pin(DHT11_PIN))
<<<<<<< HEAD
                
                # Imprime confirmação de sucesso na inicialização do DHT11
                print("DHT11 OK")
            # Captura qualquer exceção durante inicialização do DHT11
            except Exception as dht_nao_iniciado:
                # Imprime erro na inicialização do DHT11
                print(f"DHT11 erro: {dht_nao_iniciado}")
                
=======
                
                # Imprime confirmação de sucesso na inicialização do DHT11
                print("✓ DHT11 OK")
            # Captura qualquer exceção durante inicialização do DHT11
            except Exception as dht_nao_iniciado:
                # Imprime erro na inicialização do DHT11
                print(f"✗ DHT11 erro: {dht_nao_iniciado}")
                
>>>>>>> 285c4da536864a3ae455a05f95d9c51fcf4eccb5
        # Verifica se o sensor LDR está habilitado
        if ENABLE_LDR:
            # Tenta inicializar o sensor LDR
            try:
                # Configura o pino do LDR como conversor analógico-digital
                self.ldr_sensor = ADC(Pin(LDR_PIN))
                
                # Define atenuação para 11dB (permite leitura de 0V a 3.3V)
                self.ldr_sensor.atten(ADC.ATTN_11DB)
<<<<<<< HEAD
                
                # Imprime confirmação de sucesso na inicialização do LDR
                print("LDR OK")
            # Captura qualquer exceção durante inicialização do LDR
            except Exception as ldr_nao_iniciado:
                # Imprime erro na inicialização do LDR
                print(f"LDR erro: {ldr_nao_iniciado}")
                
=======
                
                # Imprime confirmação de sucesso na inicialização do LDR
                print("✓ LDR OK")
            # Captura qualquer exceção durante inicialização do LDR
            except Exception as ldr_nao_iniciado:
                # Imprime erro na inicialização do LDR
                print(f"✗ LDR erro: {ldr_nao_iniciado}")
                
>>>>>>> 285c4da536864a3ae455a05f95d9c51fcf4eccb5
        # Verifica se o sensor de chuva está habilitado
        if ENABLE_RAIN_SENSOR:
            # Tenta inicializar o sensor de chuva
            try:
                # Configura o pino do sensor de chuva como conversor analógico-digital
                self.rain_sensor = ADC(Pin(RAIN_SENSOR_PIN))
                
                # Define atenuação para 11dB (permite leitura de 0V a 3.3V)
                self.rain_sensor.atten(ADC.ATTN_11DB)
<<<<<<< HEAD
                
                # Imprime confirmação de sucesso na inicialização do sensor de chuva
                print("Rain sensor OK")
            # Captura qualquer exceção durante inicialização do sensor de chuva
            except Exception as sensor_nao_iniciado:
                # Imprime erro na inicialização do sensor de chuva
                print(f"Rain sensor erro: {sensor_nao_iniciado}")
                
=======
                
                # Imprime confirmação de sucesso na inicialização do sensor de chuva
                print("✓ Rain sensor OK")
            # Captura qualquer exceção durante inicialização do sensor de chuva
            except Exception as sensor_nao_iniciado:
                # Imprime erro na inicialização do sensor de chuva
                print(f"✗ Rain sensor erro: {sensor_nao_iniciado}")
                
>>>>>>> 285c4da536864a3ae455a05f95d9c51fcf4eccb5
    # Método para emitir um beep com frequência e duração específicas
    def beep(self, freq_hz, duration_ms):
        """Emite um beep simples"""
        # Verifica se o buzzer foi inicializado
        if not self.buzzer:
            return
        # Tenta emitir o beep
        try:
            # Define a frequência do buzzer
            self.buzzer.freq(freq_hz)
            # Define duty cycle para 512 (50% - buzzer ligado)
            self.buzzer.duty(512)
            # Aguarda pela duração especificada (convertida para segundos)
            time.sleep(duration_ms / 1000)
            # Define duty cycle para 0 (buzzer desligado)
            self.buzzer.duty(0)
        # Ignora qualquer erro durante emissão do beep
        except:
<<<<<<< HEAD
            pass

    # Método para emitir sequência de beeps para alertas específicos
    def beep_sequence(self, sequence_type):
        """Emite sequências de beeps para diferentes tipos de alerta"""
        if not self.buzzer:
            return
            
        try:
            if sequence_type == "TEMP_ALTA":
                # Sequência rápida e aguda para temperatura alta
                for _ in range(3):
                    self.beep(1200, 150)
                    time.sleep(0.1)
                    
            elif sequence_type == "TEMP_BAIXA":
                # Sequência grave e lenta para temperatura baixa
                for _ in range(2):
                    self.beep(300, 400)
                    time.sleep(0.2)
                    
            elif sequence_type == "UMIDADE_ALTA":
                # Sequência média rápida para umidade alta
                for _ in range(4):
                    self.beep(800, 100)
                    time.sleep(0.05)
                    
            elif sequence_type == "UMIDADE_BAIXA":
                # Sequência média lenta para umidade baixa
                for _ in range(2):
                    self.beep(600, 200)
                    time.sleep(0.3)
                    
            elif sequence_type == "CHUVA":
                # Sequência intermitente para chuva
                for _ in range(5):
                    self.beep(700, 80)
                    time.sleep(0.1)
                    
            elif sequence_type == "SISTEMA_OK":
                # Beep duplo suave para sistema OK
                self.beep(900, 100)
                time.sleep(0.1)
                self.beep(1100, 100)
                
        except:
            pass
            
    # Método para controlar os LEDs baseado no status do sistema
    def control_leds(self, alerts, data):
        """Controla os LEDs baseado nos alertas e dados"""
        if not (self.led_verde and self.led_vermelho and self.led_amarelo):
            return
            
        # Desliga todos os LEDs primeiro
        self.led_verde.off()
        self.led_vermelho.off()
        self.led_amarelo.off()
        
        # Verifica alertas críticos (temperatura)
        temp_alerts = [alert for alert in alerts if "TEMP" in alert]
        umidade_alerts = [alert for alert in alerts if "UMID" in alert]
        chuva_alerts = [alert for alert in alerts if "CHUVA" in alert]
        
        # LED VERMELHO - Alertas críticos de temperatura
        if temp_alerts:
            self.led_vermelho.on()
            
        # LED AMARELO - Alertas de chuva ou umidade
        elif chuva_alerts or umidade_alerts:
            self.led_amarelo.on()
            
        # LED VERDE - Sistema OK
        else:
            self.led_verde.on()
            
=======
            pass        
>>>>>>> 285c4da536864a3ae455a05f95d9c51fcf4eccb5
    # Método para conectar à rede WiFi
    def connect_wifi(self):
        """Conecta ao WiFi"""
        # Imprime mensagem de tentativa de conexão
        print("Conectando WiFi...")
        # Cria interface WiFi em modo estação (cliente)
        sta_if = network.WLAN(network.STA_IF)
        # Ativa a interface WiFi
        sta_if.active(True)
        # Verifica se não está conectado
        if not sta_if.isconnected():
            # Inicia conexão com SSID e senha
            sta_if.connect(WIFI_SSID, WIFI_PASSWORD)
            # Define timeout de 15 segundos
            timeout = 15
            # Loop de espera pela conexão
            while not sta_if.isconnected() and timeout > 0:
                # Aguarda 1 segundo
                time.sleep(1)
                # Decrementa contador de timeout
                timeout -= 1
                
        # Verifica se conseguiu conectar
        if sta_if.isconnected():
            # Imprime confirmação com endereço IP
<<<<<<< HEAD
            print(f"WiFi: {sta_if.ifconfig()[0]}")
=======
            print(f"✓ WiFi: {sta_if.ifconfig()[0]}")
>>>>>>> 285c4da536864a3ae455a05f95d9c51fcf4eccb5
            # Atualiza flag de conexão WiFi
            self.wifi_connected = True
            # Retorna sucesso
            return True
        else:
            # Imprime falha na conexão
<<<<<<< HEAD
            print("WiFi falhou")
=======
            print("✗ WiFi falhou")
>>>>>>> 285c4da536864a3ae455a05f95d9c51fcf4eccb5
            # Atualiza flag de conexão WiFi
            self.wifi_connected = False
            # Retorna falha
            return False
<<<<<<< HEAD
        
=======
>>>>>>> 285c4da536864a3ae455a05f95d9c51fcf4eccb5
    # Método para conectar ao servidor MQTT
    def connect_mqtt(self):
        """Conecta ao MQTT"""
        # Verifica se WiFi está conectado
        if not self.wifi_connected:
            # Tenta conectar WiFi se não estiver conectado
            if not self.connect_wifi():
                return False
        # Tenta conectar ao MQTT
        try:
            # Gera ID único do cliente usando timestamp
            client_id = f"weather_{time.ticks_ms()}"
            # Cria cliente MQTT com configurações do Adafruit IO
            self.mqtt_client = MQTTClient(
                client_id=client_id,
                server=MQTT_SERVER,
                port=1883,
                user=ADAFRUIT_AIO_USERNAME,
                password=ADAFRUIT_AIO_KEY
            )
            # Conecta ao servidor MQTT
            self.mqtt_client.connect()
            # Imprime confirmação de sucesso
<<<<<<< HEAD
            print("MQTT conectado")
=======
            print("✓ MQTT conectado")
>>>>>>> 285c4da536864a3ae455a05f95d9c51fcf4eccb5
            # Retorna sucesso
            return True
        # Captura qualquer exceção durante conexão MQTT
        except Exception as erro_de_conexao_mqtt:
            # Imprime erro na conexão MQTT
<<<<<<< HEAD
            print(f"MQTT erro: {erro_de_conexao_mqtt}")
=======
            print(f"✗ MQTT erro: {erro_de_conexao_mqtt}")
>>>>>>> 285c4da536864a3ae455a05f95d9c51fcf4eccb5
            # Retorna falha
            return False
    # Método para publicar dados no Adafruit IO
    def publish_data(self, feed, value):
        """Publica dados para Adafruit IO"""
        # Verifica se cliente MQTT está disponível
        if not self.mqtt_client:
            return False
        # Tenta publicar dados
        try:
            # Monta o tópico MQTT no formato do Adafruit IO
            topic = f"{ADAFRUIT_AIO_USERNAME}/feeds/{feed}"
            # Publica o valor convertido para string
            self.mqtt_client.publish(topic, str(value))
            # Retorna sucesso
            return True
        # Captura qualquer exceção durante publicação
        except Exception as erro_de_publicacao:
            # Imprime erro de publicação
            print(f"Erro publicando {feed}: {erro_de_publicacao}")
            # Retorna falha
            return False
    # Método para ler todos os sensores e retornar os dados
    def read_sensors(self):
        """Lê todos os sensores e retorna dados"""
        # Inicializa dicionário para armazenar dados
        data = {}
        
        # DHT11 - Temperatura e Umidade
        # Verifica se sensor DHT11 está disponível
        if self.dht_sensor:
            # Tenta ler dados do DHT11
            try:
                # Inicia medição do sensor
                self.dht_sensor.measure()
                # Aguarda 500ms para estabilizar leitura
                time.sleep(0.5)
                # Lê temperatura e armazena nos dados
                data['temperature'] = self.dht_sensor.temperature()
                # Lê umidade e armazena nos dados
                data['humidity'] = self.dht_sensor.humidity()
            # Captura qualquer exceção durante leitura do DHT11
            except Exception as erro_na_leitura_dht11:
                # Imprime erro na leitura do DHT11
                print(f"DHT11 erro: {erro_na_leitura_dht11}")
                # Define valores como None em caso de erro
                data['temperature'] = None
                data['humidity'] = None
        else:
            # Define valores como None se sensor não estiver disponível
            data['temperature'] = None
            data['humidity'] = None   
        # LDR - Luminosidade
        # Verifica se sensor LDR está disponível
        if self.ldr_sensor:
            # Tenta ler dados do LDR
            try:
                # Lê valor bruto do sensor (0-4095)
                ldr_raw = self.ldr_sensor.read()
                # Armazena valor bruto
                data['light_raw'] = ldr_raw
                # Converte para porcentagem (0-100%) limitando a 100
                data['light_percent'] = min(100, int((ldr_raw / 4095) * 100))
                # Determina status baseado nos limites definidos
<<<<<<< HEAD
                if ldr_raw < LDR_THRESHOLD_DARK:
=======
                if ldr_raw < LDR_DARK:
>>>>>>> 285c4da536864a3ae455a05f95d9c51fcf4eccb5
                    data['light_status'] = "Noite"
                elif ldr_raw > LDR_THRESHOLD_BRIGHT:
                    data['light_status'] = "Ensolarado"
                else:
                    data['light_status'] = "Nublado"
            # Captura qualquer exceção durante leitura do LDR
            except Exception as e:
                # Imprime erro na leitura do LDR
                print(f"LDR erro: {e}")
                
                # Define valores como None em caso de erro
                data['light_raw'] = None
                data['light_percent'] = None
                data['light_status'] = "Erro"
        else:
            # Define valores padrão se sensor não estiver disponível
            data['light_raw'] = None
            data['light_percent'] = None
            data['light_status'] = "OFF"
            
        # Sensor de Chuva
        # Verifica se sensor de chuva está disponível
        if self.rain_sensor:
            # Tenta ler dados do sensor de chuva
            try:
                # Lê valor bruto do sensor (0-4095)
                rain_raw = self.rain_sensor.read()
                
                # Armazena valor bruto
                data['rain_raw'] = rain_raw
                
<<<<<<< HEAD
                # Determina status baseado nos valores definidos
                if rain_raw > RAIN_THRESHOLD_DRY:
                    data['rain_status'] = "Seco"
                elif rain_raw < RAIN_THRESHOLD_WET:
                    data['rain_status'] = "Chuva"
                else:
                    data['rain_status'] = "Úmido"
=======
                # Determina status baseado nos valores lidos
                # Valor alto = seco, valor baixo = úmido/chuva
                data['rain_status'] = "Seco" if rain_raw > 3000 else "Úmido" if rain_raw > 1500 else "Chuva"
>>>>>>> 285c4da536864a3ae455a05f95d9c51fcf4eccb5
            # Captura qualquer exceção durante leitura do sensor de chuva
            except Exception as e:
                # Imprime erro na leitura do sensor de chuva
                print(f"Rain sensor erro: {e}")
                
                # Define valores como None em caso de erro
                data['rain_raw'] = None
                data['rain_status'] = "Erro"
        else:
            # Define valores padrão se sensor não estiver disponível
            data['rain_raw'] = None
            data['rain_status'] = "OFF"
            
        # Retorna todos os dados coletados
        return data
        
    # Método para verificar condições que geram alertas
    def check_alerts(self, data):
        """Verifica condições de alerta"""
        # Lista para armazenar alertas encontrados
        alerts = []
        
        # Obtém valores dos dados
        temp = data.get('temperature')
        humidity = data.get('humidity')
        rain_status = data.get('rain_status')
        
        # Verifica alertas de temperatura
        if temp is not None:
            # Temperatura muito alta
<<<<<<< HEAD
            if temp >= TEMP_ALERTA_ALTA:
                alerts.append("TEMP_ALTA")
            # Temperatura muito baixa
            elif temp <= TEMP_ALERTA_BAIXA:
=======
            if temp >= TEMP_HIGH:
                alerts.append("TEMP_ALTA")
            # Temperatura muito baixa
            elif temp <= TEMP_LOW:
>>>>>>> 285c4da536864a3ae455a05f95d9c51fcf4eccb5
                alerts.append("TEMP_BAIXA")
                
        # Verifica alertas de umidade
        if humidity is not None:
            # Umidade muito alta
<<<<<<< HEAD
            if humidity >= UMIDADE_ALERTA_ALTA:
                alerts.append("UMID_ALTA")
            # Umidade muito baixa
            elif humidity <= UMIDADE_ALERTA_BAIXA:
=======
            if humidity >= HUMIDITY_HIGH:
                alerts.append("UMID_ALTA")
            # Umidade muito baixa
            elif humidity <= HUMIDITY_LOW:
>>>>>>> 285c4da536864a3ae455a05f95d9c51fcf4eccb5
                alerts.append("UMID_BAIXA")
                
        # Verifica alerta de chuva
        if rain_status == "Chuva":
            alerts.append("CHUVA")
            
        # Retorna lista de alertas
        return alerts
        
<<<<<<< HEAD
    # Método para processar alertas com LEDs e som
    def handle_alerts(self, alerts, data):
        """Processa alertas - LEDs e som"""
        # Controla os LEDs baseado nos alertas
        self.control_leds(alerts, data)
        
        # Se não há alertas
        if not alerts:
            # Sistema OK - beep suave ocasional (apenas a cada 20 ciclos)
            if self.loop_count % 20 == 0:
                self.beep_sequence("SISTEMA_OK")
            return
            
        # Emite sons específicos para cada tipo de alerta
        for alert in alerts:
            if alert == "TEMP_ALTA":
                self.beep_sequence("TEMP_ALTA")
                break  # Para evitar sobreposição de sons
            elif alert == "TEMP_BAIXA":
                self.beep_sequence("TEMP_BAIXA")
                break
            elif alert == "CHUVA":
                self.beep_sequence("CHUVA")
                break
            elif alert == "UMID_ALTA":
                self.beep_sequence("UMIDADE_ALTA")
                break
            elif alert == "UMID_BAIXA":
                self.beep_sequence("UMIDADE_BAIXA")
                break
=======
    # Método para processar alertas com LED e som
    def handle_alerts(self, alerts):
        """Processa alertas - LED e som"""
        # Se não há alertas
        if not alerts:
            # Liga LED indicando sistema OK
            if self.led:
                self.led.on()  # LED ligado = sistema OK
            return
            
        # Se há alertas, desliga LED (indicando problema)
        if self.led:
            self.led.off()
            
        # Emite sons diferentes para cada tipo de alerta
        if "TEMP_ALTA" in alerts:
            # Som agudo para temperatura alta
            self.beep(800, 200)
        elif "TEMP_BAIXA" in alerts:
            # Som grave para temperatura baixa
            self.beep(400, 300)
        elif "CHUVA" in alerts:
            # Som médio para chuva
            self.beep(600, 150)
        elif any("UMID" in alert for alert in alerts):
            # Som rápido para problemas de umidade
            self.beep(500, 100)
>>>>>>> 285c4da536864a3ae455a05f95d9c51fcf4eccb5
            
    # Método para atualizar informações no display
    def update_display(self, data, alerts):
        """Atualiza display com informações"""
        # Verifica se display está disponível
        if not self.display:
            return
            
        # Tenta atualizar display
        try:
            # Limpa tela com cor preta
            self.display.fill(self.display.BLACK)
            
            # Posição vertical inicial
            y = 10
            
            # Título
            # Exibe título do sistema
            self.display.text("WEATHER STATION", 5, y, self.display.CYAN)
            y += 25
            
            # Status
            # Se há alertas
            if alerts:
                # Exibe status de alerta em vermelho
                self.display.text("STATUS: ALERTA!", 5, y, self.display.RED)
                y += 20
                
                # Exibe até 2 primeiros alertas
                for alert in alerts[:2]:  # Máximo 2 alertas
                    self.display.text(f"- {alert}", 5, y, self.display.YELLOW)
                    y += 15
            else:
                # Exibe status OK em verde
                self.display.text("STATUS: OK", 5, y, self.display.GREEN)
                y += 20
                
            # Dados dos sensores
            # Obtém valores de temperatura e umidade
            temp = data.get('temperature')
            humidity = data.get('humidity')
            
            # Exibe temperatura se disponível
            if temp is not None:
                # Cor vermelha se temperatura fora dos limites, branca se normal
<<<<<<< HEAD
                color = self.display.RED if temp >= TEMP_ALERTA_ALTA or temp <= TEMP_ALERTA_BAIXA else self.display.WHITE
=======
                color = self.display.RED if temp >= TEMP_HIGH or temp <= TEMP_LOW else self.display.WHITE
>>>>>>> 285c4da536864a3ae455a05f95d9c51fcf4eccb5
                self.display.text(f"Temp: {temp}C", 5, y, color)
                y += 15
                
            # Exibe umidade se disponível
            if humidity is not None:
                # Cor amarela se umidade fora dos limites, branca se normal
<<<<<<< HEAD
                color = self.display.YELLOW if humidity >= UMIDADE_ALERTA_ALTA or humidity <= UMIDADE_ALERTA_BAIXA else self.display.WHITE
=======
                color = self.display.YELLOW if humidity >= HUMIDITY_HIGH or humidity <= HUMIDITY_LOW else self.display.WHITE
>>>>>>> 285c4da536864a3ae455a05f95d9c51fcf4eccb5
                self.display.text(f"Umid: {humidity}%", 5, y, color)
                y += 15
                
            # Exibe dados de luminosidade
            light_percent = data.get('light_percent')
            light_status = data.get('light_status')
            if light_percent is not None:
                # Exibe porcentagem de luz
                self.display.text(f"Luz: {light_percent}%", 5, y, self.display.WHITE)
                
                # Exibe status de luz na linha seguinte
                self.display.text(f"({light_status})", 5, y + 15, self.display.WHITE)
                y += 30
                
            # Sensor de chuva (se habilitado)
            if ENABLE_RAIN_SENSOR:
                rain_status = data.get('rain_status')
                rain_raw = data.get('rain_raw')
                
                # Exibe dados se sensor estiver funcionando
                if rain_status and rain_status not in ["OFF", "Erro"]:
                    # Cor azul se estiver chovendo, branca se não
                    rain_color = self.display.BLUE if rain_status == "Chuva" else self.display.WHITE
                    self.display.text(f"Chuva: {rain_status}", 5, y, rain_color)
                    
                    # Exibe valor bruto se disponível
                    if rain_raw is not None:
                        self.display.text(f"({rain_raw})", 5, y + 15, self.display.WHITE)
                    y += 30
                
            # Conectividade
            y += 10
            
            # Status WiFi - verde se conectado, vermelho se não
            wifi_color = self.display.GREEN if self.wifi_connected else self.display.RED
            self.display.text("WiFi: " + ("ON" if self.wifi_connected else "OFF"), 5, y, wifi_color)
            y += 15
            
            # Status MQTT/Cloud - verde se conectado, vermelho se não
            mqtt_color = self.display.GREEN if self.mqtt_client else self.display.RED
            self.display.text("Cloud: " + ("ON" if self.mqtt_client else "OFF"), 5, y, mqtt_color)
            y += 20
            
            # Rodapé
            # Exibe número do ciclo atual
            self.display.text(f"Ciclo: {self.loop_count}", 5, 220, self.display.GREEN)
            
            # Exibe memória livre em KB
            self.display.text(f"Mem: {gc.mem_free()//1024}KB", 120, 220, self.display.WHITE)
            
        # Captura qualquer exceção durante atualização do display
        except Exception as e:
            # Imprime erro na atualização do display
            print(f"Display erro: {e}")
            
    # Método assíncrono para o loop principal do sistema
    async def run(self):
        """Loop principal"""
        # Imprime mensagem de início do monitoramento
        print("Iniciando monitoramento...")
        
        # Controla tentativas de conexão MQTT
        last_mqtt_attempt = 0
        
        # Loop infinito principal
        while True:
            # Bloco try-catch para capturar erros no loop
            try:
                # Incrementa contador de ciclos
                self.loop_count += 1
                
                # Imprime separador e número do ciclo
                print(f"\n--- Ciclo {self.loop_count} ---")
                
                # Tenta conectar MQTT se necessário (a cada 30 segundos)
                if not self.mqtt_client and (time.time() - last_mqtt_attempt) > 30:
                    self.connect_mqtt()
                    last_mqtt_attempt = time.time()
                    
                # Lê todos os sensores
                data = self.read_sensors()
                
                # Mostra dados de temperatura e umidade no console
                temp, humidity = data.get('temperature'), data.get('humidity')
                if temp is not None and humidity is not None:
                    print(f"DHT11: {temp}°C, {humidity}%")
                    
                # Mostra dados de luminosidade no console
                light = data.get('light_percent')
                if light is not None:
                    print(f"Luz: {light}% ({data.get('light_status')})")
                    
                # Mostra dados do sensor de chuva no console
                if ENABLE_RAIN_SENSOR:
                    rain_status = data.get('rain_status')
                    rain_raw = data.get('rain_raw')
                    if rain_status and rain_status not in ["OFF", "Erro"]:
                        print(f"Chuva: {rain_status} ({rain_raw})")
                    
                # Verifica se há condições de alerta
                alerts = self.check_alerts(data)
                
                # Imprime alertas ou status OK
                if alerts:
                    print(f"ALERTAS: {', '.join(alerts)}")
                else:
                    print("Sistema OK")
                    
                # Processa alertas (LED e som)
<<<<<<< HEAD
                self.handle_alerts(alerts, data)
=======
                self.handle_alerts(alerts)
>>>>>>> 285c4da536864a3ae455a05f95d9c51fcf4eccb5
                
                # Atualiza informações no display
                self.update_display(data, alerts)
                
                # Publica dados no MQTT se conectado
                if self.mqtt_client:
                    try:
                        # Publica temperatura se disponível
                        if temp is not None:
                            self.publish_data("temperature", temp)
                            
                        # Publica umidade se disponível
                        if humidity is not None:
                            self.publish_data("humidity", humidity)
                            
                        # Publica luminosidade se disponível
                        if light is not None:
                            self.publish_data("luminosity", light)

                        # Publica status de luz
                        light_status = data.get('light_status')
                        if light_status and light_status not in ["OFF", "Erro"]:
                            self.publish_data("light_status", light_status)
                            print(f"Publicado status-luz: {light_status}")
                        
                        # Publica dados do sensor de chuva se habilitado
                        if ENABLE_RAIN_SENSOR:
                            rain_status = data.get('rain_status')
                            if rain_status and rain_status not in ["OFF", "Erro"]:
                                self.publish_data("climate_status", rain_status)
                                print(f"Publicado chuva: {rain_status}")
                                
                            rain_raw = data.get('rain_raw')
                            if rain_raw is not None:
                                self.publish_data("rain", rain_raw)
<<<<<<< HEAD
                                print(f"Publicado chuva-raw: {rain_raw}")
=======
                                print(f"✓ Publicado chuva-raw: {rain_raw}")
>>>>>>> 285c4da536864a3ae455a05f95d9c51fcf4eccb5
                    # Se houver erro na publicação, desconecta MQTT
                    except:
                        self.mqtt_client = None  
                # Limpeza de memória a cada 10 ciclos
                if self.loop_count % 10 == 0:
                    # Executa garbage collector para liberar memória
                    gc.collect()
            
                # Aguarda 10 segundos antes do próximo ciclo (assíncrono)
                await asyncio.sleep(10)
                
            # Captura interrupção do teclado (Ctrl+C)
            except KeyboardInterrupt:
                # Imprime mensagem de interrupção
                print("Sistema interrompido")
                
                # Sai do loop principal
                break
                
            # Captura qualquer outro erro no loop
            except Exception as e:
                # Imprime erro encontrado
                print(f"Erro no loop: {e}")
                
                # Aguarda 5 segundos antes de tentar novamente
                await asyncio.sleep(5)

# ===============================================================
# FUNÇÃO PRINCIPAL
# ===============================================================

# Função assíncrona principal do sistema
async def main():
    """Função principal"""
    # Bloco try-catch para capturar erros críticos
    try:
        # Imprime mensagem de inicialização
        print("Inicializando sistema...")
        
        # Cria uma instância da classe WeatherStation
        station = WeatherStation()
        
        # Inicializa todos os componentes de hardware
        station.init_hardware()
        
        # Emite som de inicialização (2 beeps)
        # Primeiro beep: 1000Hz por 100ms
        station.beep(1000, 100)
        
        # Pausa de 100ms entre os beeps
        time.sleep(0.1)
        
        # Segundo beep: 1200Hz por 100ms
        station.beep(1200, 100)
        
        # Imprime confirmação de inicialização bem-sucedida
        print("Sistema iniciado com sucesso!")
        
        # Inicia o loop principal assíncrono
        await station.run()
        
    # Captura qualquer erro crítico durante inicialização
    except Exception as e:
        # Imprime mensagem de erro crítico
        print(f"ERRO CRÍTICO: {e}")
        
        # Aguarda 5 segundos antes de reiniciar
        time.sleep(5)
        
        # Reinicia o sistema completamente
        reset()

# Verifica se este arquivo está sendo executado diretamente
if __name__ == "__main__":
    # Executa a função principal usando asyncio
    asyncio.run(main())