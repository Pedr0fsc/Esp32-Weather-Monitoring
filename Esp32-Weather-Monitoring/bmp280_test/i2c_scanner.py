"""
Scanner de dispositivos I2C para ESP32
Este script detecta todos os dispositivos conectados ao barramento I2C 
e tenta várias configurações para melhorar a confiabilidade
"""
from machine import I2C, Pin
import time

# Tenta diferentes configurações de pinos I2C
def scan_i2c_config():
    # Configurações comuns para ESP32
    configs = [
        {"scl": 22, "sda": 21, "freq": 100000},  # Sua configuração atual
        {"scl": 22, "sda": 21, "freq": 50000},   # Frequência menor
        {"scl": 22, "sda": 21, "freq": 10000},   # Frequência muito baixa
        {"scl": 22, "sda": 21, "freq": 400000},  # Frequência alta
        # Pinos alternativos (tente apenas se necessário)
        # {"scl": 18, "sda": 19, "freq": 100000},
        # {"scl": 5, "sda": 4, "freq": 100000}
    ]
    
    found_devices = False
    
    for i, config in enumerate(configs):
        print(f"\nTentativa {i+1}: SCL={config['scl']}, SDA={config['sda']}, Freq={config['freq']}Hz")
        try:
            i2c = I2C(0, scl=Pin(config['scl']), sda=Pin(config['sda']), freq=config['freq'])
            devices = i2c.scan()
            
            if devices:
                print(f"SUCESSO! Dispositivos encontrados: {[hex(d) for d in devices]}")
                found_devices = True
                print("Endereços comuns:")
                print("  - 0x76 ou 0x77: BMP280/BME280")
                print("  - 0x3C ou 0x3D: Display OLED SSD1306")
                print("  - 0x68: MPU6050 giroscópio/acelerômetro")
                
                # Verificar especificamente o BMP280
                if 0x76 in devices or 0x77 in devices:
                    print("\nBMP280 detectado!")
                    addr = 0x76 if 0x76 in devices else 0x77
                    print(f"  Endereço: {hex(addr)}")
                    print("  Configuração para usar no código:")
                    print(f"  i2c = I2C(0, scl=Pin({config['scl']}), sda=Pin({config['sda']}), freq={config['freq']})")
                    print(f"  bmp280 = BMP280(i2c, addr={hex(addr)})")
            else:
                print("Nenhum dispositivo encontrado nesta configuração.")
        except Exception as e:
            print(f"Erro na configuração: {e}")
    
    if not found_devices:
        print("\nNenhum dispositivo I2C encontrado em todas as configurações.")
        print("Verifique suas conexões:")
        print("1. O sensor está conectado corretamente (SCL, SDA, VCC e GND)?")
        print("2. O sensor está recebendo alimentação adequada (3.3V)?")
        print("3. Os resistores pull-up estão presentes (se necessário)?")
        print("4. O sensor não está danificado?")

# Executar o scanner
scan_i2c_config()

# Aguarde antes de encerrar
print("\nPressione Ctrl+C para encerrar...")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Scanner encerrado pelo usuário.")