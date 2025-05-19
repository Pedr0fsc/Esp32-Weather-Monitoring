# Código de diagnóstico para o display ST7789 com diferentes configurações
import machine
import time
import gc

# Liberar memória
gc.collect()

# Pinagem fornecida
SPI_SCL = 18      # D18 - SCL
SPI_SDA = 23      # D23 - SDA (MOSI)
RST = 4           # D4 - RES
DC = 15           # D15 - DC
BLK = 22          # D22 - BLK (Backlight)

# Constantes de cores
BLACK = 0x0000
RED = 0xF800
GREEN = 0x07E0
BLUE = 0x001F
WHITE = 0xFFFF

class ST7789Display:
    def __init__(self, spi_sck, spi_mosi, rst, dc, bl=None, cs=None):
        print("Inicializando display...")
        
        # Pinos
        self.rst = machine.Pin(rst, machine.Pin.OUT)
        self.dc = machine.Pin(dc, machine.Pin.OUT)
        
        if cs is not None:
            self.cs = machine.Pin(cs, machine.Pin.OUT)
        else:
            self.cs = None
            
        if bl is not None:
            self.bl = machine.Pin(bl, machine.Pin.OUT)
        else:
            self.bl = None
        
        # Configurar SPI
        print("Configurando SPI...")
        try:
            self.spi = machine.SPI(2, 
                                  baudrate=40000000, 
                                  polarity=1, 
                                  phase=1,
                                  sck=machine.Pin(spi_sck), 
                                  mosi=machine.Pin(spi_mosi))
            print("SPI inicializado com sucesso")
        except Exception as e:
            print(f"Erro ao inicializar SPI: {e}")
            return
            
        # Hard reset
        print("Executando hard reset...")
        self._hard_reset()
        
        # Inicializar display
        print("Inicializando sequência...")
        self._init_display()
        
        print("Display configurado!")
    
    def _hard_reset(self):
        """Execute hard reset do display"""
        # Reset
        if self.cs:
            self.cs.value(1)
        self.dc.value(0)
        
        if self.bl:
            self.bl.value(0)  # Desliga backlight durante reset
            
        # Sequência de reset
        self.rst.value(1)
        time.sleep_ms(50)
        self.rst.value(0)
        time.sleep_ms(50)
        self.rst.value(1)
        time.sleep_ms(150)
        
        if self.bl:
            self.bl.value(1)  # Liga backlight
            print("Backlight LIGADO")
    
    def _write_cmd(self, cmd):
        """Envia comando para o display"""
        if self.cs:
            self.cs.value(0)
        self.dc.value(0)  # Comando
        self.spi.write(bytes([cmd]))
        if self.cs:
            self.cs.value(1)
    
    def _write_data(self, data):
        """Envia dados para o display"""
        if self.cs:
            self.cs.value(0)
        self.dc.value(1)  # Dados
        self.spi.write(data if isinstance(data, bytes) else bytes([data]))
        if self.cs:
            self.cs.value(1)
            
    def _init_display(self):
        """Inicializa o display com os comandos corretos"""
        # Comandos de inicialização do ST7789
        self._write_cmd(0x01)    # Software Reset
        time.sleep_ms(150)
        
        self._write_cmd(0x11)    # Sleep Out
        time.sleep_ms(120)
        
        self._write_cmd(0x36)    # Memory Data Access Control
        self._write_data(0x00)   # Normal orientation
        
        self._write_cmd(0x3A)    # Interface Pixel Format
        self._write_data(0x05)   # 16 bits por pixel
        
        self._write_cmd(0xB2)    # Porch Setting
        self._write_data(bytes([0x0C, 0x0C, 0x00, 0x33, 0x33]))
        
        self._write_cmd(0xB7)    # Gate Control
        self._write_data(0x35)
        
        self._write_cmd(0xBB)    # VCOM Setting
        self._write_data(0x19)
        
        self._write_cmd(0xC0)    # LCM Control
        self._write_data(0x2C)
        
        self._write_cmd(0xC2)    # VDV and VRH Command Enable
        self._write_data(0x01)
        
        self._write_cmd(0xC3)    # VRH Set
        self._write_data(0x12)
        
        self._write_cmd(0xC4)    # VDV Set
        self._write_data(0x20)
        
        self._write_cmd(0xC6)    # Frame Rate Control
        self._write_data(0x0F)
        
        self._write_cmd(0xD0)    # Power Control 1
        self._write_data(bytes([0xA4, 0xA1]))
        
        self._write_cmd(0xE0)    # Positive Voltage Gamma Control
        self._write_data(bytes([0xD0, 0x04, 0x0D, 0x11, 0x13, 0x2B, 0x3F, 0x54, 0x4C, 0x18, 0x0D, 0x0B, 0x1F, 0x23]))
        
        self._write_cmd(0xE1)    # Negative Voltage Gamma Control
        self._write_data(bytes([0xD0, 0x04, 0x0C, 0x11, 0x13, 0x2C, 0x3F, 0x44, 0x51, 0x2F, 0x1F, 0x1F, 0x20, 0x23]))
        
        self._write_cmd(0x21)    # Display Inversion On
        
        self._write_cmd(0x29)    # Display On
        time.sleep_ms(120)
        
    def _set_window(self, x0, y0, x1, y1):
        """Define a área ativa do display"""
        # Definir coluna
        self._write_cmd(0x2A)
        self._write_data(bytes([x0 >> 8, x0 & 0xFF, x1 >> 8, x1 & 0xFF]))
        
        # Definir linha
        self._write_cmd(0x2B)
        self._write_data(bytes([y0 >> 8, y0 & 0xFF, y1 >> 8, y1 & 0xFF]))
        
        # Escrever na memória
        self._write_cmd(0x2C)
        
    def fill_rect(self, x, y, w, h, color):
        """Preenche um retângulo com uma cor específica"""
        # Limitar às dimensões da tela
        x = min(max(x, 0), 239)
        y = min(max(y, 0), 239)
        w = min(w, 240 - x)
        h = min(h, 240 - y)
        
        if w <= 0 or h <= 0:
            return
            
        # Definir janela
        self._set_window(x, y, x + w - 1, y + h - 1)
        
        # Preparar buffer de cor (dois bytes por pixel)
        color_bytes = bytes([color >> 8, color & 0xFF])
        
        # Escrever cores - usando buffer pequeno para não estourar memória
        buffer_size = min(w * h, 256) # 512 bytes (256 pixels)
        buffer = color_bytes * buffer_size
        
        pixels_to_write = w * h
        while pixels_to_write > 0:
            chunk = min(pixels_to_write, buffer_size)
            self._write_data(buffer[:chunk*2])
            pixels_to_write -= chunk
            
    def fill(self, color):
        """Preenche toda a tela com uma cor"""
        self.fill_rect(0, 0, 240, 240, color)
        
    def test_display(self):
        """Teste básico do display com cores e padrões"""
        print("Teste: tela vermelha")
        self.fill(RED)
        time.sleep(1)
        
        print("Teste: tela verde")
        self.fill(GREEN)
        time.sleep(1)
        
        print("Teste: tela azul")
        self.fill(BLUE)
        time.sleep(1)
        
        print("Teste: tela branca")
        self.fill(WHITE)
        time.sleep(1)
        
        print("Teste: tela preta")
        self.fill(BLACK)
        time.sleep(1)
        
        # Teste de padrão quadriculado
        print("Teste: padrão quadriculado")
        self.fill(BLACK)
        for i in range(0, 240, 40):
            for j in range(0, 240, 40):
                if (i // 40 + j // 40) % 2 == 0:
                    self.fill_rect(i, j, 40, 40, RED)
                else:
                    self.fill_rect(i, j, 40, 40, BLUE)

# Criar e testar o display
try:
    print("Criando objeto do display")
    display = ST7789Display(
        spi_sck=SPI_SCL,
        spi_mosi=SPI_SDA,
        rst=RST,
        dc=DC,
        bl=BLK,
        cs=None  # Sem chip select
    )
    
    print("Iniciando teste de diagnóstico")
    display.test_display()
    print("Teste concluído com sucesso!")
    
except Exception as e:
    print(f"Erro durante a execução: {e}")