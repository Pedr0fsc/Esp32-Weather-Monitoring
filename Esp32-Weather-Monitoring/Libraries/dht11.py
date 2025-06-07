"""
Driver DHT11 para MicroPython em ESP32
Leitura de temperatura e umidade do sensor DHT11
"""
from machine import Pin
import utime

class DHT11:
    def __init__(self, pin):
        """
        Inicializa o sensor DHT11
       
        Args:
            pin: Número do pino GPIO conectado ao sensor DHT11
        """
        self.pin = Pin(pin, Pin.OUT)
        self._temperature = 0
        self._humidity = 0
        self.last_read = 0
        self._last_read_success = False
   
    def measure(self):
        """
        Realiza a leitura da temperatura e umidade.
        Retorna True se a leitura foi bem-sucedida, False caso contrário.
        """
        # Não realizar leituras com intervalos menores que 2 segundos
        current_time = utime.time()
        if current_time - self.last_read < 2 and self._last_read_success:
            return True
       
        self.last_read = current_time
       
        # Buffers de dados
        data = bytearray(5)
        
        # Reset todos os bytes para 0
        for i in range(5):
            data[i] = 0
       
        # Sinal inicial - pull down por 18ms
        self.pin.init(Pin.OUT)
        self.pin.value(1)
        utime.sleep_ms(50)
        self.pin.value(0)
        utime.sleep_ms(18)
       
        # Sinal para iniciar transmissão
        self.pin.value(1)
        utime.sleep_us(40)
        self.pin.init(Pin.IN, Pin.PULL_UP)  # Adicionado pull-up para melhor estabilidade
       
        # Esperar pela resposta do sensor (sinal baixo)
        timeout = 0
        while not self.pin.value():
            timeout += 1
            if timeout > 100:
                self._last_read_success = False
                return False
            utime.sleep_us(1)
       
        # Esperar sinal alto da resposta do sensor
        timeout = 0
        while self.pin.value():
            timeout += 1
            if timeout > 100:
                self._last_read_success = False
                return False
            utime.sleep_us(1)
       
        # Ler 40 bits (5 bytes) de dados
        for i in range(40):
            # Esperar pelo início do bit (sinal baixo)
            timeout = 0
            while not self.pin.value():
                timeout += 1
                if timeout > 100:
                    self._last_read_success = False
                    return False
                utime.sleep_us(1)
           
            # Medir duração do sinal alto para determinar bit 0 ou 1
            timeout = 0
            pulse_start = utime.ticks_us()
            while self.pin.value():
                timeout += 1
                if timeout > 100:
                    self._last_read_success = False
                    return False
                utime.sleep_us(1)
            
            pulse_duration = utime.ticks_diff(utime.ticks_us(), pulse_start)
           
            # Se o pulso alto for longo (>40us), é bit 1, caso contrário é bit 0
            data[i // 8] = (data[i // 8] << 1) | (1 if pulse_duration > 40 else 0)
       
        # Verificar checksum
        if ((data[0] + data[1] + data[2] + data[3]) & 0xFF) != data[4]:
            print("Erro de checksum:", data)
            self._last_read_success = False
            return False
       
        # Dados lidos com sucesso
        self._humidity = data[0]
        self._temperature = data[2]
        self._last_read_success = True
        return True
   
    def temperature(self):
        """
        Retorna a temperatura em graus Celsius.
        Retorna None em caso de falha na leitura.
        """
        if not self._last_read_success and not self.measure():
            return None
        return self._temperature
   
    def humidity(self):
        """
        Retorna a umidade relativa em porcentagem.
        Retorna None em caso de falha na leitura.
        """
        if not self._last_read_success and not self.measure():
            return None
        return self._humidity
   
    def read(self):
        """
        Realiza uma leitura e retorna tuple (temperatura, umidade).
        Retorna None, None em caso de falha na leitura.
        """
        if self.measure():
            return self._temperature, self._humidity
        return None, None