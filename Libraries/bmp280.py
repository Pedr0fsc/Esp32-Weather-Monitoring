from micropython import const
import time

# Endereços I2C do BMP280 (0x76 ou 0x77)
BMP280_I2C_ADDR = const(0x76)  # Endereço padrão
BMP280_I2C_ADDR_ALT = const(0x77)  # Endereço alternativo

# Registradores
BMP280_REG_CALIBRATION = const(0x88)
BMP280_REG_CONFIG = const(0xF5)
BMP280_REG_CTRL_MEAS = const(0xF4)
BMP280_REG_STATUS = const(0xF3)
BMP280_REG_PRESS_MSB = const(0xF7)
BMP280_REG_TEMP_MSB = const(0xFA)
BMP280_REG_ID = const(0xD0)

# Constantes
BMP280_CHIP_ID = const(0x58)

class BMP280:
    def __init__(self, i2c, addr=BMP280_I2C_ADDR):
        self.i2c = i2c
        self.addr = addr
        
        # Verificar se o dispositivo está presente
        try:
            chip_id = self._read_reg(BMP280_REG_ID)
            if chip_id != BMP280_CHIP_ID:
                # Tente o endereço alternativo
                if addr == BMP280_I2C_ADDR:
                    self.addr = BMP280_I2C_ADDR_ALT
                    chip_id = self._read_reg(BMP280_REG_ID)
                    if chip_id != BMP280_CHIP_ID:
                        raise RuntimeError("BMP280 não encontrado em nenhum endereço I2C")
                else:
                    raise RuntimeError(f"ID do chip inválido: 0x{chip_id:02x}")
        except Exception as e:
            raise RuntimeError(f"Erro ao comunicar com BMP280: {e}")
        
        # Ler coeficientes de calibração
        self._read_calibration()
        
        # Configuração padrão: normal mode, pressão oversample 4x, temperatura oversample 1x
        self._write_reg(BMP280_REG_CONFIG, 0x0C)  # Standby 500ms, filtro 16
        self._write_reg(BMP280_REG_CTRL_MEAS, 0x27)  # Normal mode, pressão 4x, temperatura 1x
        
        # Aguardar inicialização
        time.sleep_ms(100)
        
        # Variáveis para armazenar os últimos valores lidos
        self.temperature = 0
        self.pressure = 0
    
    def _read_reg(self, reg, size=1):
        """Lê bytes de um registrador."""
        if size == 1:
            return self.i2c.readfrom_mem(self.addr, reg, 1)[0]
        else:
            result = 0
            data = self.i2c.readfrom_mem(self.addr, reg, size)
            for i, b in enumerate(data):
                result |= b << (8 * i)
            return result
    
    def _write_reg(self, reg, value):
        """Escreve um byte em um registrador."""
        self.i2c.writeto_mem(self.addr, reg, bytes([value]))
    
    def _read_calibration(self):
        """Lê os coeficientes de calibração do sensor."""
        self.dig_T1 = self._read_reg(BMP280_REG_CALIBRATION, 2)
        self.dig_T2 = self._signed16(self._read_reg(BMP280_REG_CALIBRATION + 2, 2))
        self.dig_T3 = self._signed16(self._read_reg(BMP280_REG_CALIBRATION + 4, 2))
        
        self.dig_P1 = self._read_reg(BMP280_REG_CALIBRATION + 6, 2)
        self.dig_P2 = self._signed16(self._read_reg(BMP280_REG_CALIBRATION + 8, 2))
        self.dig_P3 = self._signed16(self._read_reg(BMP280_REG_CALIBRATION + 10, 2))
        self.dig_P4 = self._signed16(self._read_reg(BMP280_REG_CALIBRATION + 12, 2))
        self.dig_P5 = self._signed16(self._read_reg(BMP280_REG_CALIBRATION + 14, 2))
        self.dig_P6 = self._signed16(self._read_reg(BMP280_REG_CALIBRATION + 16, 2))
        self.dig_P7 = self._signed16(self._read_reg(BMP280_REG_CALIBRATION + 18, 2))
        self.dig_P8 = self._signed16(self._read_reg(BMP280_REG_CALIBRATION + 20, 2))
        self.dig_P9 = self._signed16(self._read_reg(BMP280_REG_CALIBRATION + 22, 2))
    
    def _signed16(self, value):
        """Converte um valor de 16 bits para signed."""
        if value > 32767:
            return value - 65536
        return value
    
    def read(self):
        """Lê e calcula temperatura e pressão."""
        # Lê temperatura (0xFA, 0xFB, 0xFC)
        adc_T = (self._read_reg(BMP280_REG_TEMP_MSB) << 12) | (self._read_reg(BMP280_REG_TEMP_MSB + 1) << 4) | (self._read_reg(BMP280_REG_TEMP_MSB + 2) >> 4)
        
        # Cálculo de temperatura conforme datasheet
        var1 = ((((adc_T >> 3) - (self.dig_T1 << 1))) * self.dig_T2) >> 11
        var2 = (((((adc_T >> 4) - self.dig_T1) * ((adc_T >> 4) - self.dig_T1)) >> 12) * self.dig_T3) >> 14
        t_fine = var1 + var2
        self.temperature = ((t_fine * 5 + 128) >> 8) / 100  # Temperatura em °C
        
        # Lê pressão (0xF7, 0xF8, 0xF9)
        adc_P = (self._read_reg(BMP280_REG_PRESS_MSB) << 12) | (self._read_reg(BMP280_REG_PRESS_MSB + 1) << 4) | (self._read_reg(BMP280_REG_PRESS_MSB + 2) >> 4)
        
        # Cálculo de pressão conforme datasheet
        var1 = t_fine - 128000
        var2 = var1 * var1 * self.dig_P6
        var2 = var2 + ((var1 * self.dig_P5) << 17)
        var2 = var2 + (self.dig_P4 << 35)
        var1 = ((var1 * var1 * self.dig_P3) >> 8) + ((var1 * self.dig_P2) << 12)
        var1 = ((1 << 47) + var1) * self.dig_P1 >> 33
        
        if var1 == 0:
            # Evitar divisão por zero
            return self.temperature, 0
        
        p = 1048576 - adc_P
        p = (((p << 31) - var2) * 3125) // var1
        var1 = (self.dig_P9 * (p >> 13) * (p >> 13)) >> 25
        var2 = (self.dig_P8 * p) >> 19
        p = ((p + var1 + var2) >> 8) + (self.dig_P7 << 4)
        
        self.pressure = p / 256  # Pressão em Pa
        
        return self.temperature, self.pressure
    
    def get_temperature(self):
        """Retorna a temperatura em graus Celsius."""
        self.read()
        return self.temperature
    
    def get_pressure(self):
        """Retorna a pressão em Pascal."""
        self.read()
        return self.pressure
    
    def get_altitude(self, sea_level_pressure=101325):
        """Calcula a altitude aproximada em metros.
        
        Args:
            sea_level_pressure: Pressão ao nível do mar em Pascal (padrão: 101325 Pa)
        """
        self.read()
        if self.pressure == 0:
            return 0
        return 44330 * (1 - (self.pressure / sea_level_pressure) ** (1/5.255))
    
    def sleep(self):
        """Coloca o sensor em modo sleep para economizar energia."""
        current = self._read_reg(BMP280_REG_CTRL_MEAS)
        self._write_reg(BMP280_REG_CTRL_MEAS, current & 0xFC)  # Bits 0 e 1 = 00 (sleep mode)
    
    def wake(self):
        """Coloca o sensor em modo normal."""
        current = self._read_reg(BMP280_REG_CTRL_MEAS)
        self._write_reg(BMP280_REG_CTRL_MEAS, (current & 0xFC) | 0x03)  # Bits 0 e 1 = 11 (normal mode)