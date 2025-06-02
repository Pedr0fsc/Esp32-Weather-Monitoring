# main.py - Este arquivo roda automaticamente quando o ESP32 liga
import time
from machine import I2C, Pin, reset, freq, ADC
import st7789_simplified
from bmp280 import BMP280
import dht
import gc

print("=== ESP32 WEATHER STATION COMPLETA ===")
print("Iniciando sistema...")

# CONFIGURAÇÕES DE SENSORES (True = habilitado, False = desabilitado)
ENABLE_BMP280 = False      # Sensor de pressão e temperatura
ENABLE_DHT11 = True       # Sensor de temperatura e umidade
ENABLE_RAIN_SENSOR = True # Sensor de chuva

# Pinagem do display
SPI_SCK = 18
SPI_MOSI = 23
RST = 19
DC = 15
BLK = 5

# Pinagem dos sensores
BMP280_SCL_PIN = 22       # SCL do BMP280
BMP280_SDA_PIN = 21       # SDA do BMP280
DHT11_PIN = 4             # Pino digital do DHT11
RAIN_SENSOR_PIN = 34      # Pino analógico para sensor de chuva

# Configurações I2C e constantes
BMP280_I2C_FREQ = 50000
BMP280_ADDR = 0x76
SEA_LEVEL_PRESSURE = 101325

# Configurações do sensor de chuva
RAIN_THRESHOLD_DRY = 3000      # Valor acima = seco
RAIN_THRESHOLD_WET = 1500      # Valor abaixo = chuva forte
RAIN_SAMPLES = 5               # Número de amostras para média

# Variáveis globais
display = None
bmp = None
dht11 = None
rain_sensor = None
i2c = None
boot_count = 0

def startup_sequence():
    """Sequência de inicialização com indicadores visuais"""
    global boot_count
    
    print("Executando sequência de boot...")
    
    # Economia de energia - reduz CPU para 80MHz
    freq(80000000)
    print(f"CPU reduzida para: {freq()}Hz")
    
    # Configura LED do backlight como indicador
    status_led = Pin(BLK, Pin.OUT)
    
    # Pisca 3 vezes para indicar boot
    for i in range(3):
        status_led.on()
        time.sleep(0.2)
        status_led.off()
        time.sleep(0.2)
    
    boot_count += 1
    print(f"Boot #{boot_count} concluído")

def safe_display_init():
    """Inicialização segura do display com retry"""
    global display
    
    print("Inicializando display...")
    
    # Reset físico do display
    rst_pin = Pin(RST, Pin.OUT)
    rst_pin.off()
    time.sleep(0.1)
    rst_pin.on()
    time.sleep(0.2)
    
    # Liga backlight
    bl_pin = Pin(BLK, Pin.OUT)
    bl_pin.on()
    
    for attempt in range(5):
        try:
            print(f"Tentativa display {attempt + 1}/5")
            
            display = st7789_simplified.ST7789(
                spi_sck=SPI_SCK,
                spi_mosi=SPI_MOSI,
                rst=RST,
                dc=DC,
                bl=BLK
            )
            
            # Teste rápido
            display.fill(display.BLACK)
            display.text("BOOT OK", 50, 100, display.GREEN)
            time.sleep(1)
            
            print("✓ Display inicializado!")
            return True
            
        except Exception as e:
            print(f"✗ Tentativa {attempt + 1} falhou: {e}")
            time.sleep(0.5)
            gc.collect()
    
    print("✗ Display falhou - continuando sem display")
    return False

def safe_sensor_init():
    """Inicialização segura dos sensores"""
    global i2c, bmp, dht11, rain_sensor
    
    print("Inicializando sensores...")
    sensors_ok = 0
    
    # === BMP280 ===
    if ENABLE_BMP280:
        try:
            i2c = I2C(0, scl=Pin(BMP280_SCL_PIN), sda=Pin(BMP280_SDA_PIN), freq=BMP280_I2C_FREQ)
            devices = i2c.scan()
            
            if devices:
                print(f"I2C devices: {[hex(d) for d in devices]}")
                
                # Tenta endereços comuns do BMP280
                for addr in [0x76, 0x77]:
                    if addr in devices:
                        try:
                            bmp = BMP280(i2c, addr=addr)
                            print(f"✓ BMP280 OK no endereço {hex(addr)}")
                            sensors_ok += 1
                            break
                        except Exception as e:
                            print(f"✗ BMP280 falhou no {hex(addr)}: {e}")
                            continue
                else:
                    print("✗ BMP280 não inicializou em nenhum endereço")
                    bmp = None
            else:
                print("✗ Nenhum dispositivo I2C encontrado")
                bmp = None
                
        except Exception as e:
            print(f"✗ Erro I2C geral: {e}")
            i2c = None
            bmp = None
    else:
        print("- BMP280 desabilitado na configuração")
        bmp = None
    
    # === DHT11 ===
    if ENABLE_DHT11:
        try:
            dht11 = dht.DHT11(Pin(DHT11_PIN))
            print("✓ DHT11 configurado")
            sensors_ok += 1
        except Exception as e:
            print(f"✗ DHT11 erro: {e}")
            dht11 = None
    else:
        print("- DHT11 desabilitado na configuração")
        dht11 = None
    
    # === SENSOR DE CHUVA ===
    if ENABLE_RAIN_SENSOR:
        try:
            rain_sensor = ADC(Pin(RAIN_SENSOR_PIN))
            rain_sensor.atten(ADC.ATTN_11DB)  # Permite leitura de 0 - 3.3V
            
            # Teste de leitura
            test_value = rain_sensor.read()
            if 0 <= test_value <= 4095:  # Valores válidos para ADC de 12 bits
                print(f"✓ Sensor de chuva OK (valor teste: {test_value})")
                sensors_ok += 1
            else:
                print(f"✗ Sensor de chuva valor inválido: {test_value}")
                rain_sensor = None
                
        except Exception as e:
            print(f"✗ Sensor de chuva erro: {e}")
            rain_sensor = None
    else:
        print("- Sensor de chuva desabilitado na configuração")
        rain_sensor = None
    
    print(f"Sensores ativos: {sensors_ok}")
    return sensors_ok > 0

def read_rain_sensor():
    """Lê o sensor de chuva e retorna status interpretado"""
    if rain_sensor is None:
        return None, None
        
    try:
        # Coleta múltiplas amostras para maior precisão
        readings = []
        for _ in range(RAIN_SAMPLES):
            readings.append(rain_sensor.read())
            time.sleep(0.1)
        
        # Calcula média
        avg_value = sum(readings) / len(readings)
        
        # Interpreta o valor
        if avg_value > RAIN_THRESHOLD_DRY:
            status = "Seco"
        elif avg_value < RAIN_THRESHOLD_WET:
            status = "Chuva"
        else:
            status = "Umido"
        
        return int(avg_value), status
        
    except Exception as e:
        print(f"Erro lendo sensor de chuva: {e}")
        return None, "Erro"

def show_boot_info():
    """Mostra informações de boot no display"""
    if display is None:
        return
        
    try:
        display.fill(display.BLACK)
        display.text("Weather Station", 10, 10, display.CYAN)
        display.text("Versao Completa", 10, 30, display.WHITE)
        display.text(f"Boot #{boot_count}", 10, 60, display.GREEN)
        
        # Mostra status dos componentes
        y = 90
        
        if ENABLE_BMP280:
            if bmp is not None:
                display.text("BMP280: OK", 10, y, display.GREEN)
            else:
                display.text("BMP280: ERRO", 10, y, display.RED)
        else:
            display.text("BMP280: OFF", 10, y, display.YELLOW)
        
        y += 20
        if ENABLE_DHT11:
            if dht11 is not None:
                display.text("DHT11: OK", 10, y, display.GREEN)
            else:
                display.text("DHT11: ERRO", 10, y, display.RED)
        else:
            display.text("DHT11: OFF", 10, y, display.YELLOW)
            
        y += 20
        if ENABLE_RAIN_SENSOR:
            if rain_sensor is not None:
                display.text("CHUVA: OK", 10, y, display.GREEN)
            else:
                display.text("CHUVA: ERRO", 10, y, display.RED)
        else:
            display.text("CHUVA: OFF", 10, y, display.YELLOW)
            
        display.text("Iniciando...", 10, 200, display.YELLOW)
        time.sleep(4)
        
    except Exception as e:
        print(f"Erro show_boot_info: {e}")

def read_and_display_data():
    """Loop principal de leitura e exibição"""
    loop_count = 0
    error_count = 0
    last_good_data = {}
    
    print("Iniciando loop principal...")
    
    while True:
        try:
            print(f"\n--- Ciclo {loop_count} ---")
            current_data = {}
            
            # === Lê BMP280 ===
            if bmp is not None:
                try:
                    temp = bmp.temperature
                    pressure = bmp.pressure
                    altitude = 44330.0 * (1.0 - (pressure / SEA_LEVEL_PRESSURE) ** (1.0 / 5.255))
                    
                    current_data.update({
                        'bmp_temp': temp,
                        'bmp_pressure': pressure,
                        'bmp_altitude': altitude
                    })
                    
                    print(f"BMP280: {temp:.1f}°C, {pressure:.0f}hPa, {altitude:.0f}m")
                    
                except Exception as e:
                    print(f"Erro BMP280: {e}")
                    current_data['bmp_error'] = str(e)
            
            # === Lê DHT11 ===
            if dht11 is not None:
                try:
                    dht11.measure()
                    time.sleep(0.5)  # DHT11 precisa de tempo entre leituras
                    
                    temp = dht11.temperature()
                    humidity = dht11.humidity()
                    
                    if temp is not None and humidity is not None:
                        current_data.update({
                            'dht_temp': temp,
                            'dht_humidity': humidity
                        })
                        print(f"DHT11: {temp}°C, {humidity}%")
                    else:
                        print("DHT11: Dados inválidos")
                        current_data['dht_error'] = "Dados inválidos"
                    
                except Exception as e:
                    print(f"Erro DHT11: {e}")
                    current_data['dht_error'] = str(e)
            
            # === Lê Sensor de Chuva ===
            if rain_sensor is not None:
                try:
                    rain_value, rain_status = read_rain_sensor()
                    
                    if rain_value is not None:
                        current_data.update({
                            'rain_value': rain_value,
                            'rain_status': rain_status
                        })
                        print(f"Chuva: {rain_value} ({rain_status})")
                    else:
                        current_data['rain_error'] = "Leitura falhou"
                    
                except Exception as e:
                    print(f"Erro sensor chuva: {e}")
                    current_data['rain_error'] = str(e)
            
            # === Atualiza Display ===
            if display is not None:
                try:
                    update_display_data(current_data, loop_count, error_count)
                except Exception as e:
                    print(f"Erro display: {e}")
                    error_count += 1
            
            # Guarda últimos dados bons
            if any(k for k in current_data.keys() if not k.endswith('_error')):
                last_good_data = current_data.copy()
                error_count = 0
            else:
                error_count += 1
            
            loop_count += 1
            
            # Reinicia se muitos erros consecutivos
            if error_count > 15:
                print("Muitos erros consecutivos - reiniciando sistema...")
                time.sleep(3)
                reset()
            
            # Coleta lixo periodicamente
            if loop_count % 20 == 0:
                gc.collect()
                print(f"Memória livre: {gc.mem_free()} bytes")
            
            # Pausa entre leituras
            time.sleep(8)
            
        except KeyboardInterrupt:
            print("Sistema interrompido pelo usuário")
            break
        except Exception as e:
            print(f"Erro no loop principal: {e}")
            error_count += 1
            time.sleep(5)

def update_display_data(data, loop_count, error_count):
    """Atualiza dados no display"""
    if display is None:
        return
        
    display.fill(display.BLACK)
    y = 5
    
    # Cabeçalho
    display.text("Weather Station", 5, y, display.CYAN)
    y += 25
    
    # === BMP280 ===
    if 'bmp_temp' in data:
        display.text("BMP280:", 5, y, display.YELLOW)
        y += 18
        display.text(f"T: {data['bmp_temp']:.1f}C", 5, y, display.WHITE)
        y += 15
        display.text(f"P: {data['bmp_pressure']:.0f}hPa", 5, y, display.WHITE)
        y += 15
        display.text(f"A: {data['bmp_altitude']:.0f}m", 5, y, display.WHITE)
        y += 20
    elif 'bmp_error' in data:
        display.text("BMP280: ERRO", 5, y, display.RED)
        y += 25
    
    # === DHT11 ===
    if 'dht_temp' in data:
        display.text("DHT11:", 5, y, display.YELLOW)
        y += 18
        display.text(f"T: {data['dht_temp']}C", 5, y, display.WHITE)
        y += 15
        display.text(f"H: {data['dht_humidity']}%", 5, y, display.WHITE)
        y += 20
    elif 'dht_error' in data:
        display.text("DHT11: ERRO", 5, y, display.RED)
        y += 25
    
    # === Sensor de Chuva ===
    if 'rain_value' in data:
        display.text("CHUVA:", 5, y, display.YELLOW)
        y += 18
        display.text(f"Val: {data['rain_value']}", 5, y, display.WHITE)
        y += 15
        
        # Cor baseada no status
        status = data['rain_status']
        if status == "Seco":
            color = display.GREEN
        elif status == "Chuva":
            color = display.BLUE
        else:  # Úmido
            color = display.YELLOW
            
        display.text(f"St: {status}", 5, y, color)
        y += 20
    elif 'rain_error' in data:
        display.text("CHUVA: ERRO", 5, y, display.RED)
        y += 25
    
    # === Status do Sistema ===
    display.text(f"Ciclo: {loop_count}", 5, 200, display.GREEN)
    if error_count > 0:
        display.text(f"Erros: {error_count}", 5, 220, display.RED)

def main():
    """Função principal do sistema"""
    try:
        startup_sequence()
        
        display_ok = safe_display_init()
        sensors_ok = safe_sensor_init()
        
        if display_ok:
            show_boot_info()
        
        if not sensors_ok:
            print("AVISO: Nenhum sensor funcionando!")
            if display_ok:
                display.fill(display.BLACK)
                display.text("ERRO SENSORES", 10, 100, display.RED)
                display.text("Verifique conexoes", 10, 120, display.WHITE)
                time.sleep(5)
        
        # Mostra configuração ativa
        print(f"\nConfiguração ativa:")
        print(f"- BMP280: {'ON' if ENABLE_BMP280 else 'OFF'}")
        print(f"- DHT11: {'ON' if ENABLE_DHT11 else 'OFF'}")
        print(f"- Sensor Chuva: {'ON' if ENABLE_RAIN_SENSOR else 'OFF'}")
        
        # Inicia loop principal
        read_and_display_data()
        
    except Exception as e:
        print(f"Erro crítico: {e}")
        # Tenta mostrar erro no display
        if display is not None:
            try:
                display.fill(display.BLACK)
                display.text("ERRO CRITICO", 10, 100, display.RED)
                display.text("Reiniciando...", 10, 120, display.WHITE)
            except:
                pass
        
        time.sleep(5)
        reset()

# PONTO DE ENTRADA AUTOMÁTICO
if __name__ == "__main__":
    main()