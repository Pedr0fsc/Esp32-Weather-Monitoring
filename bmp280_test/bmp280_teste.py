"""
Estação Meteorológica ESP32 com BMP280 e DHT11
Versão melhorada com maior tolerância a falhas
"""
from machine import I2C, Pin
import time
import gc

# Importações de sensores
# Presumindo que você tenha os arquivos bmp280.py e dht11.py na placa
from bmp280 import BMP280
from dht11 import DHT11

# Configurações
BMP280_SCL_PIN = 22      # GPIO para SCL do BMP280
BMP280_SDA_PIN = 21      # GPIO para SDA do BMP280
DHT11_PIN = 4            # GPIO para o pino de dados do DHT11
BMP280_I2C_FREQ = 50000  # Frequência I2C mais baixa para maior estabilidade
BMP280_ADDR = 0x76       # Endereço padrão do BMP280 (use 0x77 se necessário)

SEA_LEVEL_PRESSURE = 101325  # 1013.25 hPa (padrão)
MAX_INIT_RETRIES = 3     # Número máximo de tentativas de inicialização

def setup_sensors():
    """Configura e inicializa ambos os sensores com mais tentativas"""
    sensors = {}
    errors = []
    
    # Inicializar BMP280 com várias tentativas
    for attempt in range(MAX_INIT_RETRIES):
        try:
            print(f"Tentativa {attempt+1}/{MAX_INIT_RETRIES} de inicializar BMP280...")
            i2c = I2C(0, scl=Pin(BMP280_SCL_PIN), sda=Pin(BMP280_SDA_PIN), freq=BMP280_I2C_FREQ)
            
            # Dar um tempo para o barramento I2C estabilizar
            time.sleep(0.1)
            
            devices = i2c.scan()
            if devices:
                print(f"Dispositivos I2C encontrados: {[hex(d) for d in devices]}")
                
                # Tentar ambos os endereços possíveis do BMP280 se não for especificado
                if 0x76 in devices:
                    sensors['bmp280'] = BMP280(i2c, addr=0x76)
                    print("BMP280 inicializado com sucesso no endereço 0x76!")
                    break
                elif 0x77 in devices:
                    sensors['bmp280'] = BMP280(i2c, addr=0x77)
                    print("BMP280 inicializado com sucesso no endereço 0x77!")
                    break
                else:
                    print(f"BMP280 não encontrado nos endereços esperados. Dispositivos disponíveis: {[hex(d) for d in devices]}")
                    if attempt == MAX_INIT_RETRIES - 1:
                        errors.append("BMP280 não encontrado nos endereços esperados")
            else:
                print("Nenhum dispositivo I2C encontrado nesta tentativa.")
                if attempt == MAX_INIT_RETRIES - 1:
                    errors.append("Nenhum dispositivo I2C encontrado após múltiplas tentativas")
            
            # Aguarde antes da próxima tentativa
            if attempt < MAX_INIT_RETRIES - 1:
                print("Aguardando antes da próxima tentativa...")
                time.sleep(1)
                
        except Exception as e:
            print(f"Erro ao configurar I2C/BMP280 (tentativa {attempt+1}): {e}")
            if attempt == MAX_INIT_RETRIES - 1:
                errors.append(f"Erro ao inicializar BMP280: {e}")
            time.sleep(1)
    
    # Inicializar DHT11 com várias tentativas
    for attempt in range(MAX_INIT_RETRIES):
        try:
            print(f"Tentativa {attempt+1}/{MAX_INIT_RETRIES} de inicializar DHT11...")
            dht11 = DHT11(DHT11_PIN)
            
            # Tentar fazer uma leitura inicial para verificar se funciona
            print("Testando DHT11 com leitura inicial...")
            temp, hum = dht11.read()
            
            if temp is not None or hum is not None:
                sensors['dht11'] = dht11
                print(f"DHT11 inicializado com sucesso! Leitura inicial: Temp={temp}°C, Umidade={hum}%")
                break
            else:
                print("DHT11 inicializado, mas a leitura inicial falhou.")
                # Mesmo que a leitura inicial falhe, armazenamos o sensor
                if attempt == MAX_INIT_RETRIES - 1:
                    sensors['dht11'] = dht11
                    print("DHT11 inicializado sem leitura confirmada.")
                
        except Exception as e:
            print(f"Erro ao inicializar DHT11 (tentativa {attempt+1}): {e}")
            if attempt == MAX_INIT_RETRIES - 1:
                errors.append(f"Erro ao inicializar DHT11: {e}")
            time.sleep(1)
    
    if errors:
        print("\nALERTA: Alguns erros ocorreram:")
        for err in errors:
            print(f"- {err}")
    
    print(f"\nSensores inicializados: {', '.join(sensors.keys())}" if sensors else "Nenhum sensor inicializado!")
    return sensors

def format_reading(value, precision=2):
    """Formata um valor para exibição, tratando None"""
    if value is None:
        return "N/A"
    return f"{value:.{precision}f}"

def read_sensors(sensors):
    """Lê os dados de todos os sensores disponíveis com tratamento de erro melhorado"""
    readings = {
        'timestamp': time.time(),
        'temp_bmp': None,
        'pressure': None,
        'altitude': None,
        'temp_dht': None,
        'humidity': None
    }
    
    # Liberar memória antes das leituras
    gc.collect()
    
    # Ler BMP280
    if 'bmp280' in sensors:
        try:
            # Leitura do BMP280
            readings['temp_bmp'] = sensors['bmp280'].get_temperature()
            readings['pressure'] = sensors['bmp280'].get_pressure()
            readings['altitude'] = sensors['bmp280'].get_altitude(SEA_LEVEL_PRESSURE)
        except Exception as e:
            print(f"Erro ao ler BMP280: {e}")
    
    # Ler DHT11 com até 3 tentativas
    if 'dht11' in sensors:
        success = False
        for attempt in range(3):
            try:
                # Leitura do DHT11
                temp, hum = sensors['dht11'].read()
                if temp is not None and hum is not None:
                    readings['temp_dht'] = temp
                    readings['humidity'] = hum
                    success = True
                    break
                else:
                    print(f"Tentativa {attempt+1}: Leitura do DHT11 retornou valores nulos")
            except Exception as e:
                print(f"Erro ao ler DHT11 (tentativa {attempt+1}): {e}")
            
            # Se não for a última tentativa, espere um pouco antes de tentar novamente
            if attempt < 2:
                time.sleep(1)
        
        if not success:
            print("Falha em todas as tentativas de leitura do DHT11")
    
    return readings

def display_readings(readings):
    """Exibe os dados dos sensores no terminal"""
    print("\n-----------------------------------------")
    print("| Sensor     | Leitura                  |")
    print("-----------------------------------------")
    
    # BMP280
    temp_bmp = format_reading(readings['temp_bmp'])
    print(f"| BMP280     | Temperatura: {temp_bmp} °C      |")
    
    pressure = readings['pressure']
    if pressure is not None:
        pressure_hpa = pressure / 100  # Converter Pa para hPa
        print(f"|            | Pressão: {pressure_hpa:.2f} hPa        |")
    else:
        print("|            | Pressão: N/A               |")
    
    altitude = format_reading(readings['altitude'])
    print(f"|            | Altitude: {altitude} m         |")
    
    # DHT11
    temp_dht = format_reading(readings['temp_dht'])
    print(f"| DHT11      | Temperatura: {temp_dht} °C      |")
    
    humidity = format_reading(readings['humidity'])
    print(f"|            | Umidade: {humidity} %          |")
    
    print("-----------------------------------------")

def calculate_heat_index(temperature, humidity):
    """
    Calcula o índice de calor (sensação térmica) com base na temperatura e umidade
    Temperature em Celsius, umidade em porcentagem
    """
    if temperature is None or humidity is None:
        return None
    
    # Converter para Fahrenheit para o cálculo
    tempF = temperature * 9/5 + 32
    
    # Fórmula simplificada do índice de calor
    hi = 0.5 * (tempF + 61.0 + ((tempF - 68.0) * 1.2) + (humidity * 0.094))
    
    # Se estiver realmente quente, use a fórmula completa
    if hi > 80:
        hi = -42.379 + 2.04901523 * tempF + 10.14333127 * humidity
        hi = hi - 0.22475541 * tempF * humidity - 6.83783e-3 * tempF**2
        hi = hi - 5.481717e-2 * humidity**2 + 1.22874e-3 * tempF**2 * humidity
        hi = hi + 8.5282e-4 * tempF * humidity**2 - 1.99e-6 * tempF**2 * humidity**2
    
    # Converter de volta para Celsius
    return (hi - 32) * 5/9

def display_environmental_analysis(readings):
    """Exibe uma análise ambiental com base nas leituras"""
    temp_bmp = readings['temp_bmp']
    temp_dht = readings['temp_dht']
    humidity = readings['humidity']
    pressure = readings['pressure']
    
    # Use a temperatura mais confiável (geralmente o BMP280)
    temp = temp_bmp if temp_bmp is not None else temp_dht
    
    print("\n=== Análise Ambiental ===")
    
    # Calcular sensação térmica se possível
    if temp_dht is not None and humidity is not None:
        heat_index = calculate_heat_index(temp_dht, humidity)
        print(f"Sensação térmica: {format_reading(heat_index)} °C")
    
    # Análise de conforto
    if humidity is not None and temp is not None:
        if 40 <= humidity <= 60:
            if 20 <= temp <= 26:
                print("Condição: Confortável")
            elif temp < 20:
                print("Condição: Um pouco fria")
            else:
                print("Condição: Um pouco quente")
        elif humidity < 40:
            print("Condição: Ar seco")
        else:
            print("Condição: Úmido")
    
    # Tendência de clima baseada na pressão
    if pressure is not None:
        pressure_hpa = pressure / 100
        if pressure_hpa < 1000:
            print("Pressão: Baixa - Possibilidade de chuva")
        elif pressure_hpa > 1020:
            print("Pressão: Alta - Tempo provavelmente estável")
        else:
            print("Pressão: Normal")

def run_weather_station(duration=60, interval=5):
    """
    Executa a estação meteorológica por um período determinado
    
    Args:
        duration: Duração total em segundos (padrão: 60s)
        interval: Intervalo entre leituras em segundos (padrão: 5s)
    """
    print("\n===== Estação Meteorológica ESP32 =====")
    print(f"Executando por {duration} segundos, intervalo de {interval} segundos")
    
    # Configurar sensores
    print("\nInicializando sensores...")
    sensors = setup_sensors()
    
    if not sensors:
        print("Nenhum sensor disponível. Encerrando.")
        return
    
    # Aguardar estabilização dos sensores
    print("\nAguardando 2 segundos para estabilização dos sensores...")
    time.sleep(2)
    
    # Calcular número de leituras
    num_readings = duration // interval
    
    # Loop principal
    for i in range(num_readings):
        print(f"\nLeitura {i+1}/{num_readings}")
        
        # Ler dados
        readings = read_sensors(sensors)
        
        # Exibir resultados
        display_readings(readings)
        
        # Análise ambiental a cada 3 leituras
        if (i % 3) == 2:
            display_environmental_analysis(readings)
        
        # Aguardar até a próxima leitura (se não for a última)
        if i < num_readings - 1:
            print(f"\nAguardando {interval} segundos até a próxima leitura...")
            time.sleep(interval)
    
    print("\n===== Estação Meteorológica Encerrada =====")

if __name__ == "__main__":
    try:
        # Executar a estação meteorológica por 60 segundos, com leituras a cada 5 segundos
        run_weather_station(duration=60, interval=5)
    except KeyboardInterrupt:
        print("\nPrograma interrompido pelo usuário.")
    except Exception as e:
        print(f"\nErro inesperado: {e}")
        import sys
        sys.print_exception(e)