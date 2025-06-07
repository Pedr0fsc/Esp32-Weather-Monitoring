# main.py - Este arquivo roda automaticamente quando o ESP32 liga
import time
from machine import Pin, reset, freq, ADC
import st7789_simplified
import dht
import gc

print("=== ESP32 WEATHER STATION COM SENSOR DE LUMINOSIDADE ===")
print("Iniciando sistema...")

# CONFIGURAÇÕES DE SENSORES (True = habilitado, False = desabilitado)
ENABLE_LDR = True         # Sensor de luminosidade (substitui BMP280)
ENABLE_DHT11 = True       # Sensor de temperatura e umidade
ENABLE_RAIN_SENSOR = False # Sensor de chuva

# Pinagem do display
SPI_SCK = 18
SPI_MOSI = 23
RST = 19
DC = 15
BLK = 5

# Pinagem dos sensores
LDR_PIN = 32              # Pino analógico para o LDR (substitui BMP280)
DHT11_PIN = 4             # Pino digital do DHT11
RAIN_SENSOR_PIN = 34      # Pino analógico para sensor de chuva

# Configurações do sensor de chuva
RAIN_THRESHOLD_DRY = 3000      # Valor acima = seco
RAIN_THRESHOLD_WET = 1500      # Valor abaixo = chuva forte
RAIN_SAMPLES = 5               # Número de amostras para média

# Configurações do sensor LDR (Luminosidade)
LDR_SAMPLES = 10               # Número de amostras para média
LDR_THRESHOLD_DARK = 500       # Valor abaixo = noite/escuro
LDR_THRESHOLD_BRIGHT = 2500    # Valor acima = dia ensolarado
# Entre os dois valores = nublado/ambiente interno

# Variáveis globais
display = None
dht11 = None
rain_sensor = None
ldr_sensor = None
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
    global dht11, rain_sensor, ldr_sensor
    
    print("Inicializando sensores...")
    sensors_ok = 0
    
    # === SENSOR LDR (LUMINOSIDADE) ===
    if ENABLE_LDR:
        try:
            ldr_sensor = ADC(Pin(LDR_PIN))
            ldr_sensor.atten(ADC.ATTN_11DB)  # Permite leitura de 0 - 3.3V
            
            # Teste de leitura
            test_value = ldr_sensor.read()
            if 0 <= test_value <= 4095:  # Valores válidos para ADC de 12 bits
                print(f"✓ Sensor LDR OK (valor teste: {test_value})")
                sensors_ok += 1
            else:
                print(f"✗ Sensor LDR valor inválido: {test_value}")
                ldr_sensor = None
                
        except Exception as e:
            print(f"✗ Sensor LDR erro: {e}")
            ldr_sensor = None
    else:
        print("- Sensor LDR desabilitado na configuração")
        ldr_sensor = None
    
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

def read_ldr_sensor():
    """Lê o sensor LDR e retorna valor e condição climática interpretada"""
    if ldr_sensor is None:
        return None, None, None
        
    try:
        # Coleta múltiplas amostras para maior precisão
        readings = []
        for _ in range(LDR_SAMPLES):
            readings.append(ldr_sensor.read())
            time.sleep(0.05)
        
        # Calcula média
        avg_value = sum(readings) / len(readings)
        
        # Interpreta o valor de luminosidade
        if avg_value < LDR_THRESHOLD_DARK:
            light_status = "Noite"
            weather_condition = "Noite/Escuro"
        elif avg_value > LDR_THRESHOLD_BRIGHT:
            light_status = "Sol"
            weather_condition = "Dia Ensolarado"
        else:
            light_status = "Nublado"
            weather_condition = "Nublado/Ambiente"
        
        # Calcula percentual de luminosidade (0-100%)
        light_percent = min(100, int((avg_value / 4095) * 100))
        
        return int(avg_value), light_status, weather_condition, light_percent
        
    except Exception as e:
        print(f"Erro lendo sensor LDR: {e}")
        return None, "Erro", "Erro", 0

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

def get_weather_summary(light_status, rain_status):
    """Combina dados de luminosidade e chuva para dar um resumo do tempo"""
    if light_status == "Erro" or rain_status == "Erro":
        return "Erro nos Sensores"
    
    # Combinações possíveis
    if rain_status == "Chuva":
        if light_status == "Noite":
            return "Chuva Noturna"
        else:
            return "Chuva Diurna"
    elif rain_status == "Umido":
        if light_status == "Nublado":
            return "Tempo Umido/Nublado"
        elif light_status == "Noite":
            return "Noite Umida"
        else:
            return "Pos-Chuva"
    else:  # Seco
        if light_status == "Sol":
            return "Tempo Bom/Ensolarado"
        elif light_status == "Nublado":
            return "Nublado Seco"
        else:
            return "Noite Clara"

def show_boot_info():
    """Mostra informações de boot no display"""
    if display is None:
        return
        
    try:
        display.fill(display.BLACK)
        display.text("Weather Station", 10, 10, display.CYAN)
        display.text("Com Sensor LDR", 10, 30, display.WHITE)
        display.text(f"Boot #{boot_count}", 10, 60, display.GREEN)
        
        # Mostra status dos componentes
        y = 90
        
        if ENABLE_LDR:
            if ldr_sensor is not None:
                display.text("LDR: OK", 10, y, display.GREEN)
            else:
                display.text("LDR: ERRO", 10, y, display.RED)
        else:
            display.text("LDR: OFF", 10, y, display.YELLOW)
        
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
            
            # === Lê Sensor LDR ===
            if ldr_sensor is not None:
                try:
                    ldr_value, light_status, weather_condition, light_percent = read_ldr_sensor()
                    
                    if ldr_value is not None:
                        current_data.update({
                            'ldr_value': ldr_value,
                            'light_status': light_status,
                            'weather_condition': weather_condition,
                            'light_percent': light_percent
                        })
                        print(f"LDR: {ldr_value} ({light_percent}%) - {light_status} - {weather_condition}")
                    else:
                        current_data['ldr_error'] = "Leitura falhou"
                        
                except Exception as e:
                    print(f"Erro LDR: {e}")
                    current_data['ldr_error'] = str(e)
            
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
            
            # === Gera Resumo do Tempo ===
            if 'light_status' in current_data and 'rain_status' in current_data:
                weather_summary = get_weather_summary(
                    current_data['light_status'], 
                    current_data['rain_status']
                )
                current_data['weather_summary'] = weather_summary
                print(f"Resumo do Tempo: {weather_summary}")
            
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
    y += 20
    
    # === RESUMO DO TEMPO (DESTAQUE) ===
    if 'weather_summary' in data:
        # Escolhe cor baseada no resumo
        summary = data['weather_summary']
        if "Ensolarado" in summary or "Tempo Bom" in summary:
            summary_color = display.YELLOW
        elif "Chuva" in summary:
            summary_color = display.BLUE
        elif "Noite" in summary:
            summary_color = display.CYAN
        elif "Nublado" in summary:
            summary_color = display.WHITE
        else:
            summary_color = display.GREEN
            
        display.text("CONDICAO:", 5, y, display.WHITE)
        y += 15
        # Divide texto longo em duas linhas se necessário
        if len(summary) > 16:
            words = summary.split()
            line1 = " ".join(words[:2])
            line2 = " ".join(words[2:])
            display.text(line1, 5, y, summary_color)
            y += 15
            display.text(line2, 5, y, summary_color)
        else:
            display.text(summary, 5, y, summary_color)
        y += 25
    
    # === SENSOR LDR ===
    if 'ldr_value' in data:
        display.text("LUMINOSIDADE:", 5, y, display.YELLOW)
        y += 15
        display.text(f"Valor: {data['ldr_value']}", 5, y, display.WHITE)
        y += 15
        display.text(f"Luz: {data['light_percent']}%", 5, y, display.WHITE)
        y += 15
        
        # Cor baseada no status de luz
        status = data['light_status']
        if status == "Sol":
            color = display.YELLOW
        elif status == "Noite":
            color = display.BLUE
        else:  # Nublado
            color = display.WHITE
            
        display.text(f"Status: {status}", 5, y, color)
        y += 20
    elif 'ldr_error' in data:
        display.text("LDR: ERRO", 5, y, display.RED)
        y += 20
    
    # === DHT11 ===
    if 'dht_temp' in data:
        display.text("TEMPERATURA/UMIDADE:", 5, y, display.GREEN)
        y += 15
        display.text(f"Temp: {data['dht_temp']}C", 5, y, display.WHITE)
        y += 15
        display.text(f"Umid: {data['dht_humidity']}%", 5, y, display.WHITE)
        y += 20
    elif 'dht_error' in data:
        display.text("DHT11: ERRO", 5, y, display.RED)
        y += 20
    
    # === Sensor de Chuva ===
    if 'rain_value' in data:
        display.text("CHUVA:", 5, y, display.CYAN)
        y += 15
        display.text(f"Sensor: {data['rain_value']}", 5, y, display.WHITE)
        y += 15
        
        # Cor baseada no status
        status = data['rain_status']
        if status == "Seco":
            color = display.GREEN
        elif status == "Chuva":
            color = display.BLUE
        else:  # Úmido
            color = display.YELLOW
            
        display.text(f"Status: {status}", 5, y, color)
        y += 20
    elif 'rain_error' in data:
        display.text("CHUVA: ERRO", 5, y, display.RED)
        y += 20
    
    # === Status do Sistema ===
    display.text(f"Ciclo: {loop_count}", 5, 200, display.GREEN)
    if error_count > 0:
        display.text(f"Erros: {error_count}", 120, 200, display.RED)

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
        print(f"- Sensor LDR: {'ON' if ENABLE_LDR else 'OFF'} (Pino {LDR_PIN})")
        print(f"- DHT11: {'ON' if ENABLE_DHT11 else 'OFF'} (Pino {DHT11_PIN})")
        print(f"- Sensor Chuva: {'ON' if ENABLE_RAIN_SENSOR else 'OFF'} (Pino {RAIN_SENSOR_PIN})")
        
        print(f"\nLimites LDR:")
        print(f"- Noite/Escuro: < {LDR_THRESHOLD_DARK}")
        print(f"- Nublado: {LDR_THRESHOLD_DARK} - {LDR_THRESHOLD_BRIGHT}")
        print(f"- Ensolarado: > {LDR_THRESHOLD_BRIGHT}")
        
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