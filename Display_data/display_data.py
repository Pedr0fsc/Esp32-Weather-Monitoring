# ===============================================================
# ESP32 WEATHER STATION COM SISTEMA DE ALERTAS
# Estação meteorológica inteligente com sensores e atuadores
# ===============================================================

import time
from machine import Pin, reset, freq, ADC, PWM
import st7789_simplified
import dht
import gc

print("=== ESP32 WEATHER STATION ===")
print("Iniciando sistema...")

# ===============================================================
# CONFIGURAÇÃO DOS SENSORES
# ===============================================================

ENABLE_LDR = True         # Sensor de luminosidade
ENABLE_DHT11 = True       # Sensor de temperatura e umidade
ENABLE_RAIN_SENSOR = False # Sensor de chuva (desabilitado por padrão)

# ===============================================================
# CONFIGURAÇÃO DE PINOS
# ===============================================================

# Display ST7789
SPI_SCK = 18
SPI_MOSI = 23
RST = 19
DC = 15
BLK = 5

# Sensores
LDR_PIN = 32              # Sensor de luminosidade (analógico)
DHT11_PIN = 4             # Temperatura/umidade (digital)
RAIN_SENSOR_PIN = 34      # Sensor de chuva (analógico)

# Atuadores (LEDs e Buzzer)
LED_VERDE_PIN = 2         # LED Verde - Sistema OK
LED_VERMELHO_PIN = 12     # LED Vermelho - Alertas críticos
LED_AMARELO_PIN = 13         # LED Amarelo - Chuva/Umidade
BUZZER_PIN = 14           # Buzzer para alertas sonoros

# ===============================================================
# CONFIGURAÇÃO DE LIMITES E ALERTAS
# ===============================================================

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

# Configurações gerais
ENABLE_SOUND_ALERTS = True   # Ativar/desativar buzzer
LDR_SAMPLES = 5             # Amostras para média do LDR
RAIN_SAMPLES = 5            # Amostras para média da chuva

# ===============================================================
# PADRÕES DE SONS DO BUZZER
# ===============================================================

BEEP_PATTERNS = {
    'temp_alta': [(800, 200), (0, 100), (800, 200)],      # Bi-bip agudo
    'temp_baixa': [(400, 300), (0, 200), (400, 300)],     # Bi-bip grave
    'umidade_alta': [(600, 150), (0, 50), (600, 150)],    # Tri-bip
    'chuva': [(500, 100), (0, 50)] * 3,                   # Bips rápidos
    'sistema_ok': [(1000, 100)],                          # Bip único
    'erro': [(300, 500)],                                 # Bip longo grave
}

# ===============================================================
# VARIÁVEIS GLOBAIS
# ===============================================================

display = None
dht11 = None
rain_sensor = None
ldr_sensor = None
led_verde = None
led_vermelho = None
led_amarelo = None
buzzer = None
boot_count = 0

# ===============================================================
# FUNÇÕES DE INICIALIZAÇÃO
# ===============================================================

def startup_sequence():
    """Sequência de inicialização do sistema"""
    global boot_count
    
    print("Executando sequência de boot...")
    
    # Reduz frequência da CPU para economia de energia
    freq(80000000)
    print(f"CPU configurada para: {freq()}Hz")
    
    # Indica boot com LED do backlight
    status_led = Pin(BLK, Pin.OUT)
    for i in range(3):
        status_led.on()
        time.sleep(0.2)
        status_led.off()
        time.sleep(0.2)
    
    boot_count += 1
    print(f"Boot #{boot_count} concluído")

def init_display():
    """Inicializa o display ST7789"""
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
    
    try:
        display = st7789_simplified.ST7789(
            spi_sck=SPI_SCK,
            spi_mosi=SPI_MOSI,
            rst=RST,
            dc=DC,
            bl=BLK
        )
        
        # Teste inicial
        display.fill(display.BLACK)
        display.text("WEATHER STATION", 10, 100, display.GREEN)
        display.text("INICIALIZANDO...", 10, 120, display.WHITE)
        time.sleep(2)
        
        print("✓ Display inicializado com sucesso!")
        return True
        
    except Exception as e:
        print(f"✗ Erro no display: {e}")
        return False

def init_sensors():
    """Inicializa todos os sensores configurados"""
    global dht11, rain_sensor, ldr_sensor
    
    print("Inicializando sensores...")
    sensors_ok = 0
    
    # Sensor LDR (Luminosidade)
    if ENABLE_LDR:
        try:
            ldr_sensor = ADC(Pin(LDR_PIN))
            ldr_sensor.atten(ADC.ATTN_11DB)  # Range 0-3.3V
            
            # Teste de leitura
            test_value = ldr_sensor.read()
            if 0 <= test_value <= 4095:
                print(f"✓ Sensor LDR OK (teste: {test_value})")
                sensors_ok += 1
            else:
                print(f"✗ LDR valor inválido: {test_value}")
                ldr_sensor = None
                
        except Exception as e:
            print(f"✗ Erro no LDR: {e}")
            ldr_sensor = None
    
    # Sensor DHT11 (Temperatura e Umidade)
    if ENABLE_DHT11:
        try:
            dht11 = dht.DHT11(Pin(DHT11_PIN))
            print("✓ DHT11 configurado")
            sensors_ok += 1
        except Exception as e:
            print(f"✗ Erro no DHT11: {e}")
            dht11 = None
    
    # Sensor de Chuva
    if ENABLE_RAIN_SENSOR:
        try:
            rain_sensor = ADC(Pin(RAIN_SENSOR_PIN))
            rain_sensor.atten(ADC.ATTN_11DB)  # Range 0-3.3V
            
            # Teste de leitura
            test_value = rain_sensor.read()
            if 0 <= test_value <= 4095:
                print(f"✓ Sensor de chuva OK (teste: {test_value})")
                sensors_ok += 1
            else:
                print(f"✗ Sensor de chuva valor inválido: {test_value}")
                rain_sensor = None
                
        except Exception as e:
            print(f"✗ Erro no sensor de chuva: {e}")
            rain_sensor = None
    
    print(f"Sensores ativos: {sensors_ok}")
    return sensors_ok > 0

def init_actuators():
    """Inicializa LEDs e buzzer para sistema de alertas"""
    global led_verde, led_vermelho, led_amarelo, buzzer
    
    print("Inicializando sistema de alertas...")
    
    try:
        # Configura LEDs como saídas
        led_verde = Pin(LED_VERDE_PIN, Pin.OUT)
        led_vermelho = Pin(LED_VERMELHO_PIN, Pin.OUT)
        led_amarelo = Pin(LED_AMARELO_PIN, Pin.OUT)
        
        # Configura buzzer como PWM
        buzzer = PWM(Pin(BUZZER_PIN))
        buzzer.duty(0)  # Inicia desligado
        
        # Teste dos componentes
        test_actuators()
        
        print("✓ Sistema de alertas inicializado!")
        return True
        
    except Exception as e:
        print(f"✗ Erro nos atuadores: {e}")
        return False

def test_actuators():
    """Testa LEDs e buzzer em sequência"""
    print("Testando sistema de alertas...")
    
    # Teste dos LEDs
    leds = [(led_verde, "Verde"), (led_vermelho, "Vermelho"), (led_amarelo, "amarelo")]
    
    for led, cor in leds:
        if led:
            print(f"Testando LED {cor}")
            led.on()
            time.sleep(0.3)
            led.off()
            time.sleep(0.1)
    
    # Teste do buzzer
    if buzzer and ENABLE_SOUND_ALERTS:
        print("Testando buzzer")
        play_beep_pattern('sistema_ok')

# ===============================================================
# FUNÇÕES DE LEITURA DOS SENSORES
# ===============================================================

def read_ldr_sensor():
    """Lê sensor de luminosidade e interpreta condição"""
    if ldr_sensor is None:
        return None, "Sensor OFF", 0
        
    try:
        # Coleta múltiplas amostras para maior precisão
        readings = [ldr_sensor.read() for _ in range(LDR_SAMPLES)]
        avg_value = sum(readings) / len(readings)
        
        # Interpreta luminosidade
        if avg_value < LDR_THRESHOLD_DARK:
            light_status = "Noite"
        elif avg_value > LDR_THRESHOLD_BRIGHT:
            light_status = "Ensolarado"
        else:
            light_status = "Nublado"
        
        # Calcula percentual (0-100%)
        light_percent = min(100, int((avg_value / 4095) * 100))
        
        return int(avg_value), light_status, light_percent
        
    except Exception as e:
        print(f"Erro no LDR: {e}")
        return None, "Erro", 0

def read_rain_sensor():
    """Lê sensor de chuva e interpreta status"""
    if rain_sensor is None:
        return None, "Sensor OFF"
        
    try:
        # Coleta múltiplas amostras
        readings = [rain_sensor.read() for _ in range(RAIN_SAMPLES)]
        avg_value = sum(readings) / len(readings)
        
        # Interpreta umidade
        if avg_value > RAIN_THRESHOLD_DRY:
            status = "Seco"
        elif avg_value < RAIN_THRESHOLD_WET:
            status = "Chuva"
        else:
            status = "Úmido"
        
        return int(avg_value), status
        
    except Exception as e:
        print(f"Erro no sensor de chuva: {e}")
        return None, "Erro"

def read_dht11_sensor():
    """Lê sensor DHT11 (temperatura e umidade)"""
    if dht11 is None:
        return None, None
        
    try:
        dht11.measure()
        time.sleep(0.5)  # DHT11 precisa de pausa entre leituras
        
        temp = dht11.temperature()
        humidity = dht11.humidity()
        
        if temp is not None and humidity is not None:
            return temp, humidity
        else:
            print("DHT11: Dados inválidos")
            return None, None
            
    except Exception as e:
        print(f"Erro no DHT11: {e}")
        return None, None

# ===============================================================
# SISTEMA DE ALERTAS
# ===============================================================

def play_beep_pattern(pattern_name):
    """Toca padrão de beeps específico"""
    if not buzzer or not ENABLE_SOUND_ALERTS or pattern_name not in BEEP_PATTERNS:
        return
    
    pattern = BEEP_PATTERNS[pattern_name]
    
    try:
        for freq_hz, duration_ms in pattern:
            if freq_hz > 0:
                buzzer.freq(freq_hz)
                buzzer.duty(512)  # 50% duty cycle
            else:
                buzzer.duty(0)    # Silêncio
            
            time.sleep(duration_ms / 1000.0)
        
        buzzer.duty(0)  # Garante que termine desligado
        
    except Exception as e:
        print(f"Erro no buzzer: {e}")
        buzzer.duty(0)

def update_alert_system(temp, humidity, rain_status):
    """Atualiza sistema de alertas baseado nos dados dos sensores"""
    alerts = {
        'temp_alta': False,
        'temp_baixa': False,
        'umidade_alta': False,
        'umidade_baixa': False,
        'chuva': False,
        'sistema_ok': True
    }
    
    # Verifica alertas de temperatura
    if temp is not None:
        if temp >= TEMP_ALERTA_ALTA:
            alerts['temp_alta'] = True
            alerts['sistema_ok'] = False
        elif temp <= TEMP_ALERTA_BAIXA:
            alerts['temp_baixa'] = True
            alerts['sistema_ok'] = False
    
    # Verifica alertas de umidade
    if humidity is not None:
        if humidity >= UMIDADE_ALERTA_ALTA:
            alerts['umidade_alta'] = True
            alerts['sistema_ok'] = False
        elif humidity <= UMIDADE_ALERTA_BAIXA:
            alerts['umidade_baixa'] = True
            alerts['sistema_ok'] = False
    
    # Verifica alerta de chuva
    if rain_status == "Chuva":
        alerts['chuva'] = True
        alerts['sistema_ok'] = False
    
    # Atualiza LEDs e sons
    update_leds(alerts)
    play_alerts(alerts)
    
    return alerts

def update_leds(alerts):
    """Atualiza status dos LEDs baseado nos alertas"""
    if not all([led_verde, led_vermelho, led_amarelo]):
        return
    
    # LED VERDE - Sistema OK
    led_verde.value(1 if alerts['sistema_ok'] else 0)
    
    # LED VERMELHO - Alertas críticos (temperatura)
    led_vermelho.value(1 if (alerts['temp_alta'] or alerts['temp_baixa']) else 0)
    
    # LED AMARELO - Alertas de umidade/chuva
    led_amarelo.value(1 if (alerts['chuva'] or alerts['umidade_alta'] or alerts['umidade_baixa']) else 0)

def play_alerts(alerts):
    """Toca alertas sonoros por prioridade"""
    if not ENABLE_SOUND_ALERTS:
        return
    
    # Toca apenas o alerta de maior prioridade
    if alerts['temp_alta']:
        play_beep_pattern('temp_alta')
    elif alerts['temp_baixa']:
        play_beep_pattern('temp_baixa')
    elif alerts['chuva']:
        play_beep_pattern('chuva')
    elif alerts['umidade_alta'] or alerts['umidade_baixa']:
        play_beep_pattern('umidade_alta')

# ===============================================================
# INTERFACE DO DISPLAY
# ===============================================================

def update_display(temp, humidity, ldr_value, light_status, light_percent, rain_status, alerts, loop_count):
    """Atualiza informações no display"""
    if display is None:
        return
        
    try:
        display.fill(display.BLACK)
        y = 5
        
        # Cabeçalho
        display.text("WEATHER STATION", 5, y, display.CYAN)
        y += 20
        
        # Status geral do sistema
        if alerts['sistema_ok']:
            display.text("STATUS: OK", 5, y, display.GREEN)
        else:
            display.text("STATUS: ALERTA!", 5, y, display.RED)
        y += 25
        
        # Temperatura e Umidade
        if temp is not None and humidity is not None:
            temp_color = display.WHITE
            if temp >= TEMP_ALERTA_ALTA:
                temp_color = display.RED
            elif temp <= TEMP_ALERTA_BAIXA:
                temp_color = display.BLUE
            
            display.text(f"Temp: {temp}C", 5, y, temp_color)
            y += 15
            
            hum_color = display.WHITE
            if humidity >= UMIDADE_ALERTA_ALTA or humidity <= UMIDADE_ALERTA_BAIXA:
                hum_color = display.YELLOW
            
            display.text(f"Umid: {humidity}%", 5, y, hum_color)
            y += 20
        
        # Luminosidade
        if ldr_value is not None:
            light_color = display.YELLOW if light_status == "Ensolarado" else display.WHITE
            display.text(f"Luz: {light_percent}%", 5, y, light_color)
            display.text(f"({light_status})", 5, y + 15, light_color)
            y += 35
        
        # Chuva (se habilitado)
        if ENABLE_RAIN_SENSOR and rain_status:
            rain_color = display.BLUE if rain_status == "Chuva" else display.WHITE
            display.text(f"Chuva: {rain_status}", 5, y, rain_color)
            y += 20
        
        # Alertas ativos
        active_alerts = [k for k, v in alerts.items() if v and k != 'sistema_ok']
        if active_alerts:
            display.text("ALERTAS ATIVOS:", 5, y, display.RED)
            y += 15
            for alert in active_alerts[:3]:  # Máximo 3 alertas na tela
                alert_text = alert.replace('_', ' ').upper()
                display.text(f"- {alert_text}", 5, y, display.YELLOW)
                y += 12
        
        # Status do sistema (rodapé)
        display.text(f"Ciclo: {loop_count}", 5, 220, display.GREEN)
        
        # Indicadores dos LEDs
        led_status = "LEDs: "
        if led_verde and led_verde.value():
            led_status += "Verde"
        if led_vermelho and led_vermelho.value():
            led_status += "Vermelho"
        if led_amarelo and led_amarelo.value():
            led_status += "Amarelo"
        if len(led_status) == 6:
            led_status += "OFF"
        
        display.text(led_status, 120, 220, display.WHITE)
        
    except Exception as e:
        print(f"Erro no display: {e}")

# ===============================================================
# LOOP PRINCIPAL
# ===============================================================

def main_loop():
    """Loop principal de leitura e exibição dos dados"""
    loop_count = 0
    error_count = 0
    
    print("Iniciando loop principal de monitoramento...")
    
    while True:
        try:
            print(f"\n--- Ciclo {loop_count + 1} ---")
            
            # Lê todos os sensores
            temp, humidity = read_dht11_sensor()
            ldr_value, light_status, light_percent = read_ldr_sensor()
            rain_value, rain_status = read_rain_sensor()
            
            # Exibe dados no console
            if temp is not None and humidity is not None:
                print(f"DHT11: {temp}°C, {humidity}%")
            
            if ldr_value is not None:
                print(f"LDR: {ldr_value} ({light_percent}%) - {light_status}")
            
            if ENABLE_RAIN_SENSOR and rain_value is not None:
                print(f"Chuva: {rain_value} ({rain_status})")
            
            # Atualiza sistema de alertas
            alerts = update_alert_system(temp, humidity, rain_status)
            
            # Mostra alertas no console
            active_alerts = [k for k, v in alerts.items() if v and k != 'sistema_ok']
            if active_alerts:
                print(f"ALERTAS: {', '.join(active_alerts)}")
            else:
                print("Sistema OK")
            
            # Atualiza display
            update_display(temp, humidity, ldr_value, light_status, light_percent, 
                         rain_status, alerts, loop_count + 1)
            
            loop_count += 1
            error_count = 0
            
            # Som de confirmação ocasional (a cada 20 ciclos sem alertas)
            if loop_count % 20 == 0 and alerts['sistema_ok']:
                play_beep_pattern('sistema_ok')
            
            # Limpeza de memória periódica
            if loop_count % 10 == 0:
                gc.collect()
                print(f"Memória livre: {gc.mem_free()} bytes")
            
            # Pausa entre leituras
            time.sleep(5)
            
        except KeyboardInterrupt:
            print("Sistema interrompido pelo usuário")
            break
            
        except Exception as e:
            print(f"Erro no loop principal: {e}")
            error_count += 1
            
            if error_count > 10:
                print("Muitos erros consecutivos - reiniciando...")
                play_beep_pattern('erro')
                time.sleep(3)
                reset()
            
            time.sleep(2)

# ===============================================================
# FUNÇÃO PRINCIPAL
# ===============================================================

def main():
    """Função principal do sistema"""
    try:
        print("=== INICIALIZAÇÃO DO SISTEMA ===")
        
        # Sequência de inicialização
        startup_sequence()
        
        # Inicializa componentes
        display_ok = init_display()
        sensors_ok = init_sensors()
        actuators_ok = init_actuators()
        
        # Mostra configuração no console
        print(f"\n=== CONFIGURAÇÃO ATIVA ===")
        print(f"Sensores:")
        print(f"- LDR (Luminosidade): {'ON' if ENABLE_LDR else 'OFF'}")
        print(f"- DHT11 (Temp/Umidade): {'ON' if ENABLE_DHT11 else 'OFF'}")
        print(f"- Sensor de Chuva: {'ON' if ENABLE_RAIN_SENSOR else 'OFF'}")
        print(f"\nLimites de Alerta:")
        print(f"- Temperatura: <{TEMP_ALERTA_BAIXA}°C ou >{TEMP_ALERTA_ALTA}°C")
        print(f"- Umidade: <{UMIDADE_ALERTA_BAIXA}% ou >{UMIDADE_ALERTA_ALTA}%")
        print(f"- Alertas Sonoros: {'ON' if ENABLE_SOUND_ALERTS else 'OFF'}")
        
        # Verifica se há sensores funcionando
        if not sensors_ok:
            print("⚠️ AVISO: Nenhum sensor funcionando!")
            if actuators_ok:
                play_beep_pattern('erro')
        
        # Som de inicialização bem-sucedida
        if actuators_ok:
            time.sleep(1)
            play_beep_pattern('sistema_ok')
        
        print("\n=== SISTEMA INICIADO ===")
        
        # Inicia monitoramento contínuo
        main_loop()
        
    except Exception as e:
        print(f"ERRO CRÍTICO: {e}")
        
        # Alerta de erro crítico
        if buzzer and ENABLE_SOUND_ALERTS:
            play_beep_pattern('erro')
        
        if led_vermelho:
            # Pisca LED vermelho para indicar erro crítico
            for _ in range(10):
                led_vermelho.on()
                time.sleep(0.1)
                led_vermelho.off()
                time.sleep(0.1)
        
        time.sleep(5)
        reset()

# ===============================================================
# PONTO DE ENTRADA
# ===============================================================
if __name__ == "__main__":
    main()