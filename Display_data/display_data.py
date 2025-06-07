import time
from machine import Pin, reset, freq, ADC, PWM
import st7789_simplified
import dht
import gc
import network
import uasyncio as asyncio
from umqtt.simple import MQTTClient

print("=== ESP32 WEATHER STATION ===")

# ===============================================================
# CONFIGURAÇÕES
# ===============================================================

# Sensores
ENABLE_LDR = True
ENABLE_DHT11 = True
ENABLE_RAIN_SENSOR = True

# WiFi e MQTT
WIFI_SSID = ""
WIFI_PASSWORD = ""
ADAFRUIT_AIO_USERNAME = ""
ADAFRUIT_AIO_KEY = ""
MQTT_SERVER = "io.adafruit.com"

# Pinos
DHT11_PIN = 4
LDR_PIN = 32
RAIN_SENSOR_PIN = 34
LED_PIN = 2
BUZZER_PIN = 14

# Display ST7789
SPI_SCK, SPI_MOSI, RST, DC, BLK = 18, 23, 19, 15, 5

# Limites de alerta
TEMP_HIGH, TEMP_LOW = 35, 5
HUMIDITY_HIGH, HUMIDITY_LOW = 85, 20
LDR_DARK, LDR_BRIGHT = 500, 2500

# ===============================================================
# CLASSES E VARIÁVEIS GLOBAIS
# ===============================================================

class WeatherStation:
    def __init__(self):
        self.display = None
        self.dht_sensor = None
        self.ldr_sensor = None
        self.rain_sensor = None
        self.led = None
        self.buzzer = None
        self.mqtt_client = None
        self.wifi_connected = False
        self.loop_count = 0
        
    def init_hardware(self):
        """Inicializa todos os componentes de hardware"""
        freq(80000000)  # Reduz frequência para economia
        
        # Display
        try:
            self.display = st7789_simplified.ST7789(
                spi_sck=SPI_SCK, spi_mosi=SPI_MOSI, rst=RST, dc=DC, bl=BLK
            )
            self.display.fill(self.display.BLACK)
            self.display.text("WEATHER STATION", 10, 100, self.display.GREEN)
            self.display.text("INICIALIZANDO...", 10, 120, self.display.WHITE)
            print("✓ Display OK")
        except Exception as e:
            print(f"✗ Display erro: {e}")
            
        # LED de status
        try:
            self.led = Pin(LED_PIN, Pin.OUT)
            self.led.on()
            print("✓ LED OK")
        except Exception as e:
            print(f"✗ LED erro: {e}")
            
        # Buzzer
        try:
            self.buzzer = PWM(Pin(BUZZER_PIN))
            self.buzzer.duty(0)
            self.beep(1000, 100)  # Teste
            print("✓ Buzzer OK")
        except Exception as e:
            print(f"✗ Buzzer erro: {e}")
            
        # Sensores
        if ENABLE_DHT11:
            try:
                self.dht_sensor = dht.DHT11(Pin(DHT11_PIN))
                print("✓ DHT11 OK")
            except Exception as e:
                print(f"✗ DHT11 erro: {e}")
                
        if ENABLE_LDR:
            try:
                self.ldr_sensor = ADC(Pin(LDR_PIN))
                self.ldr_sensor.atten(ADC.ATTN_11DB)
                print("✓ LDR OK")
            except Exception as e:
                print(f"✗ LDR erro: {e}")
                
        if ENABLE_RAIN_SENSOR:
            try:
                self.rain_sensor = ADC(Pin(RAIN_SENSOR_PIN))
                self.rain_sensor.atten(ADC.ATTN_11DB)
                print("✓ Rain sensor OK")
            except Exception as e:
                print(f"✗ Rain sensor erro: {e}")
                
    def beep(self, freq_hz, duration_ms):
        """Emite um beep simples"""
        if not self.buzzer:
            return
        try:
            self.buzzer.freq(freq_hz)
            self.buzzer.duty(512)
            time.sleep(duration_ms / 1000)
            self.buzzer.duty(0)
        except:
            pass
            
    def connect_wifi(self):
        """Conecta ao WiFi"""
        print("Conectando WiFi...")
        sta_if = network.WLAN(network.STA_IF)
        sta_if.active(True)
        
        if not sta_if.isconnected():
            sta_if.connect(WIFI_SSID, WIFI_PASSWORD)
            
            timeout = 15
            while not sta_if.isconnected() and timeout > 0:
                time.sleep(1)
                timeout -= 1
                
        if sta_if.isconnected():
            print(f"✓ WiFi: {sta_if.ifconfig()[0]}")
            self.wifi_connected = True
            return True
        else:
            print("✗ WiFi falhou")
            self.wifi_connected = False
            return False
            
    def connect_mqtt(self):
        """Conecta ao MQTT"""
        if not self.wifi_connected:
            if not self.connect_wifi():
                return False
                
        try:
            client_id = f"weather_{time.ticks_ms()}"
            self.mqtt_client = MQTTClient(
                client_id=client_id,
                server=MQTT_SERVER,
                port=1883,
                user=ADAFRUIT_AIO_USERNAME,
                password=ADAFRUIT_AIO_KEY
            )
            self.mqtt_client.connect()
            print("✓ MQTT conectado")
            return True
        except Exception as e:
            print(f"✗ MQTT erro: {e}")
            return False
            
    def publish_data(self, feed, value):
        """Publica dados para Adafruit IO"""
        if not self.mqtt_client:
            return False
            
        try:
            topic = f"{ADAFRUIT_AIO_USERNAME}/feeds/{feed}"
            self.mqtt_client.publish(topic, str(value))
            return True
        except Exception as e:
            print(f"Erro publicando {feed}: {e}")
            return False
            
    def read_sensors(self):
        """Lê todos os sensores e retorna dados"""
        data = {}
        
        # DHT11 - Temperatura e Umidade
        if self.dht_sensor:
            try:
                self.dht_sensor.measure()
                time.sleep(0.5)
                data['temperature'] = self.dht_sensor.temperature()
                data['humidity'] = self.dht_sensor.humidity()
            except Exception as e:
                print(f"DHT11 erro: {e}")
                data['temperature'] = None
                data['humidity'] = None
        else:
            data['temperature'] = None
            data['humidity'] = None
            
        # LDR - Luminosidade
        if self.ldr_sensor:
            try:
                ldr_raw = self.ldr_sensor.read()
                data['light_raw'] = ldr_raw
                data['light_percent'] = min(100, int((ldr_raw / 4095) * 100))
                
                if ldr_raw < LDR_DARK:
                    data['light_status'] = "Noite"
                elif ldr_raw > LDR_BRIGHT:
                    data['light_status'] = "Ensolarado"
                else:
                    data['light_status'] = "Nublado"
            except Exception as e:
                print(f"LDR erro: {e}")
                data['light_raw'] = None
                data['light_percent'] = None
                data['light_status'] = "Erro"
        else:
            data['light_raw'] = None
            data['light_percent'] = None
            data['light_status'] = "OFF"
            
        # Sensor de Chuva
        if self.rain_sensor:
            try:
                rain_raw = self.rain_sensor.read()
                data['rain_raw'] = rain_raw
                data['rain_status'] = "Seco" if rain_raw > 3000 else "Úmido" if rain_raw > 1500 else "Chuva"
            except Exception as e:
                print(f"Rain sensor erro: {e}")
                data['rain_raw'] = None
                data['rain_status'] = "Erro"
        else:
            data['rain_raw'] = None
            data['rain_status'] = "OFF"
            
        return data
        
    def check_alerts(self, data):
        """Verifica condições de alerta"""
        alerts = []
        
        temp = data.get('temperature')
        humidity = data.get('humidity')
        rain_status = data.get('rain_status')
        
        if temp is not None:
            if temp >= TEMP_HIGH:
                alerts.append("TEMP_ALTA")
            elif temp <= TEMP_LOW:
                alerts.append("TEMP_BAIXA")
                
        if humidity is not None:
            if humidity >= HUMIDITY_HIGH:
                alerts.append("UMID_ALTA")
            elif humidity <= HUMIDITY_LOW:
                alerts.append("UMID_BAIXA")
                
        if rain_status == "Chuva":
            alerts.append("CHUVA")
            
        return alerts
        
    def handle_alerts(self, alerts):
        """Processa alertas - LED e som"""
        if not alerts:
            if self.led:
                self.led.on()  # LED ligado = sistema OK
            return
            
        # LED piscando para alertas
        if self.led:
            self.led.off()
            
        # Som de alerta
        if "TEMP_ALTA" in alerts:
            self.beep(800, 200)
        elif "TEMP_BAIXA" in alerts:
            self.beep(400, 300)
        elif "CHUVA" in alerts:
            self.beep(600, 150)
        elif any("UMID" in alert for alert in alerts):
            self.beep(500, 100)
            
    def update_display(self, data, alerts):
        """Atualiza display com informações"""
        if not self.display:
            return
            
        try:
            self.display.fill(self.display.BLACK)
            y = 10
            
            # Título
            self.display.text("WEATHER STATION", 5, y, self.display.CYAN)
            y += 25
            
            # Status
            if alerts:
                self.display.text("STATUS: ALERTA!", 5, y, self.display.RED)
                y += 20
                for alert in alerts[:2]:  # Máximo 2 alertas
                    self.display.text(f"- {alert}", 5, y, self.display.YELLOW)
                    y += 15
            else:
                self.display.text("STATUS: OK", 5, y, self.display.GREEN)
                y += 20
                
            # Dados dos sensores
            temp = data.get('temperature')
            humidity = data.get('humidity')
            
            if temp is not None:
                color = self.display.RED if temp >= TEMP_HIGH or temp <= TEMP_LOW else self.display.WHITE
                self.display.text(f"Temp: {temp}C", 5, y, color)
                y += 15
                
            if humidity is not None:
                color = self.display.YELLOW if humidity >= HUMIDITY_HIGH or humidity <= HUMIDITY_LOW else self.display.WHITE
                self.display.text(f"Umid: {humidity}%", 5, y, color)
                y += 15
                
            light_percent = data.get('light_percent')
            light_status = data.get('light_status')
            if light_percent is not None:
                self.display.text(f"Luz: {light_percent}%", 5, y, self.display.WHITE)
                self.display.text(f"({light_status})", 5, y + 15, self.display.WHITE)
                y += 30
                
            # Sensor de chuva (se habilitado)
            if ENABLE_RAIN_SENSOR:
                rain_status = data.get('rain_status')
                rain_raw = data.get('rain_raw')
                if rain_status and rain_status not in ["OFF", "Erro"]:
                    rain_color = self.display.BLUE if rain_status == "Chuva" else self.display.WHITE
                    self.display.text(f"Chuva: {rain_status}", 5, y, rain_color)
                    if rain_raw is not None:
                        self.display.text(f"({rain_raw})", 5, y + 15, self.display.WHITE)
                    y += 30
                
            # Conectividade
            y += 10
            wifi_color = self.display.GREEN if self.wifi_connected else self.display.RED
            self.display.text("WiFi: " + ("ON" if self.wifi_connected else "OFF"), 5, y, wifi_color)
            y += 15
            
            mqtt_color = self.display.GREEN if self.mqtt_client else self.display.RED
            self.display.text("Cloud: " + ("ON" if self.mqtt_client else "OFF"), 5, y, mqtt_color)
            y += 20
            
            # Rodapé
            self.display.text(f"Ciclo: {self.loop_count}", 5, 220, self.display.GREEN)
            self.display.text(f"Mem: {gc.mem_free()//1024}KB", 120, 220, self.display.WHITE)
            
        except Exception as e:
            print(f"Display erro: {e}")
            
    async def run(self):
        """Loop principal"""
        print("Iniciando monitoramento...")
        last_mqtt_attempt = 0
        
        while True:
            try:
                self.loop_count += 1
                print(f"\n--- Ciclo {self.loop_count} ---")
                
                # Tenta conectar MQTT se necessário
                if not self.mqtt_client and (time.time() - last_mqtt_attempt) > 30:
                    self.connect_mqtt()
                    last_mqtt_attempt = time.time()
                    
                # Lê sensores
                data = self.read_sensors()
                
                # Mostra dados no console
                temp, humidity = data.get('temperature'), data.get('humidity')
                if temp is not None and humidity is not None:
                    print(f"DHT11: {temp}°C, {humidity}%")
                    
                light = data.get('light_percent')
                if light is not None:
                    print(f"Luz: {light}% ({data.get('light_status')})")
                    
                # Mostra dados do sensor de chuva
                if ENABLE_RAIN_SENSOR:
                    rain_status = data.get('rain_status')
                    rain_raw = data.get('rain_raw')
                    if rain_status and rain_status not in ["OFF", "Erro"]:
                        print(f"Chuva: {rain_status} ({rain_raw})")
                    
                # Verifica alertas
                alerts = self.check_alerts(data)
                if alerts:
                    print(f"ALERTAS: {', '.join(alerts)}")
                else:
                    print("Sistema OK")
                    
                # Processa alertas
                self.handle_alerts(alerts)
                
                # Atualiza display
                self.update_display(data, alerts)
                
                # Publica dados
                if self.mqtt_client:
                    try:
                        if temp is not None:
                            self.publish_data("temperature", temp)
                        if humidity is not None:
                            self.publish_data("humidity", humidity)
                        if light is not None:
                            self.publish_data("luminosity", light)

                        # Publica status de luz
                        light_status = data.get('light_status')
                        if light_status and light_status not in ["OFF", "Erro"]:
                            self.publish_data("light_status", light_status)
                            print(f"✓ Publicado status-luz: {light_status}")
                        
                        # Publica dados do sensor de chuva
                        if ENABLE_RAIN_SENSOR:
                            rain_status = data.get('rain_status')
                            if rain_status and rain_status not in ["OFF", "Erro"]:
                                self.publish_data("climate_status", rain_status)
                                print(f"✓ Publicado chuva: {rain_status}")
                                
                            rain_raw = data.get('rain_raw')
                            if rain_raw is not None:
                                self.publish_data("rain", rain_raw)
                                print(f"✓ Publicado chuva-raw: {rain_raw}")
                    except:
                        self.mqtt_client = None
                        
                # Limpeza de memória
                if self.loop_count % 10 == 0:
                    gc.collect()
                    
                await asyncio.sleep(10)
                
            except KeyboardInterrupt:
                print("Sistema interrompido")
                break
            except Exception as e:
                print(f"Erro no loop: {e}")
                await asyncio.sleep(5)

# ===============================================================
# FUNÇÃO PRINCIPAL
# ===============================================================

async def main():
    """Função principal"""
    try:
        print("Inicializando sistema...")
        
        # Cria instância da estação
        station = WeatherStation()
        
        # Inicializa hardware
        station.init_hardware()
        
        # Som de inicialização
        station.beep(1000, 100)
        time.sleep(0.1)
        station.beep(1200, 100)
        
        print("Sistema iniciado com sucesso!")
        
        # Inicia loop principal
        await station.run()
        
    except Exception as e:
        print(f"ERRO CRÍTICO: {e}")
        time.sleep(5)
        reset()

if __name__ == "__main__":
    asyncio.run(main())