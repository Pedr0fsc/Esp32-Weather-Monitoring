# st7789_simplified.py
import machine
import time

class ST7789:
    # Constantes de cores
    BLACK = 0x0000
    RED = 0xF800
    GREEN = 0x07E0
    BLUE = 0x001F
    WHITE = 0xFFFF
    YELLOW = 0xFFE0
    CYAN = 0x07FF
    MAGENTA = 0xF81F
    
    def __init__(self, spi_sck, spi_mosi, rst, dc, bl=None, cs=None, width=240, height=240):
        # Configurar pinos
        self.width = width
        self.height = height
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
        self.spi = machine.SPI(2, 
                              baudrate=40000000, 
                              polarity=1, 
                              phase=1,
                              sck=machine.Pin(spi_sck), 
                              mosi=machine.Pin(spi_mosi))
            
        # Inicializar display
        self._hard_reset()
        self._init_display()
        
        # Ligar backlight se disponível
        if self.bl:
            self.bl.value(1)
    
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
        
    def pixel(self, x, y, color):
        """Desenha um pixel na posição especificada"""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return
        self._set_window(x, y, x, y)
        self._write_data(bytes([color >> 8, color & 0xFF]))
        
    def fill_rect(self, x, y, w, h, color):
        """Preenche um retângulo com uma cor específica"""
        # Limitar às dimensões da tela
        x = min(max(x, 0), self.width - 1)
        y = min(max(y, 0), self.height - 1)
        w = min(w, self.width - x)
        h = min(h, self.height - y)
        
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
        self.fill_rect(0, 0, self.width, self.height, color)
        
    def hline(self, x, y, w, color):
        """Desenha uma linha horizontal"""
        self.fill_rect(x, y, w, 1, color)
        
    def vline(self, x, y, h, color):
        """Desenha uma linha vertical"""
        self.fill_rect(x, y, 1, h, color)
        
    def rect(self, x, y, w, h, color):
        """Desenha um retângulo (apenas bordas)"""
        self.hline(x, y, w, color)
        self.hline(x, y + h - 1, w, color)
        self.vline(x, y, h, color)
        self.vline(x + w - 1, y, h, color)
        
    def text(self, text, x, y, color, font_size=1, bg_color=None):
        """Método básico para desenhar texto (caracteres ASCII)"""
        # Caracteres básicos 8x8
        from micropython import const
        _FONT = (
            b'\x00\x00\x00\x00\x00\x00\x00\x00', # Space
            b'\x10\x10\x10\x10\x10\x00\x10\x00', # !
            b'\x28\x28\x00\x00\x00\x00\x00\x00', # "
            b'\x28\x28\x7c\x28\x7c\x28\x28\x00', # #
            b'\x10\x3c\x50\x38\x14\x78\x10\x00', # $
            b'\x60\x64\x08\x10\x20\x4c\x0c\x00', # %
            b'\x20\x50\x50\x20\x54\x48\x34\x00', # &
            b'\x10\x10\x00\x00\x00\x00\x00\x00', # '
            b'\x08\x10\x20\x20\x20\x10\x08\x00', # (
            b'\x20\x10\x08\x08\x08\x10\x20\x00', # )
            b'\x00\x28\x10\x7c\x10\x28\x00\x00', # *
            b'\x00\x10\x10\x7c\x10\x10\x00\x00', # +
            b'\x00\x00\x00\x00\x00\x10\x10\x20', # ,
            b'\x00\x00\x00\x7c\x00\x00\x00\x00', # -
            b'\x00\x00\x00\x00\x00\x30\x30\x00', # .
            b'\x00\x04\x08\x10\x20\x40\x00\x00', # /
            b'\x38\x44\x4c\x54\x64\x44\x38\x00', # 0
            b'\x10\x30\x10\x10\x10\x10\x38\x00', # 1
            b'\x38\x44\x04\x08\x10\x20\x7c\x00', # 2
            b'\x38\x44\x04\x18\x04\x44\x38\x00', # 3
            b'\x08\x18\x28\x48\x7c\x08\x08\x00', # 4
            b'\x7c\x40\x78\x04\x04\x44\x38\x00', # 5
            b'\x18\x20\x40\x78\x44\x44\x38\x00', # 6
            b'\x7c\x04\x08\x10\x20\x20\x20\x00', # 7
            b'\x38\x44\x44\x38\x44\x44\x38\x00', # 8
            b'\x38\x44\x44\x3c\x04\x08\x30\x00', # 9
            b'\x00\x30\x30\x00\x30\x30\x00\x00', # :
            b'\x00\x30\x30\x00\x30\x10\x20\x00', # ;
            b'\x08\x10\x20\x40\x20\x10\x08\x00', # 
            b'\x00\x00\x7c\x00\x7c\x00\x00\x00', # =
            b'\x20\x10\x08\x04\x08\x10\x20\x00', # >
            b'\x38\x44\x04\x08\x10\x00\x10\x00', # ?
            b'\x38\x44\x5c\x54\x5c\x40\x38\x00', # @
            b'\x38\x44\x44\x7c\x44\x44\x44\x00', # A
            b'\x78\x24\x24\x38\x24\x24\x78\x00', # B
            b'\x38\x44\x40\x40\x40\x44\x38\x00', # C
            b'\x78\x24\x24\x24\x24\x24\x78\x00', # D
            b'\x7c\x40\x40\x78\x40\x40\x7c\x00', # E
            b'\x7c\x40\x40\x78\x40\x40\x40\x00', # F
            b'\x38\x44\x40\x5c\x44\x44\x3c\x00', # G
            b'\x44\x44\x44\x7c\x44\x44\x44\x00', # H
            b'\x38\x10\x10\x10\x10\x10\x38\x00', # I
            b'\x04\x04\x04\x04\x04\x44\x38\x00', # J
            b'\x44\x48\x50\x60\x50\x48\x44\x00', # K
            b'\x40\x40\x40\x40\x40\x40\x7c\x00', # L
            b'\x44\x6c\x54\x54\x44\x44\x44\x00', # M
            b'\x44\x64\x64\x54\x4c\x4c\x44\x00', # N
            b'\x38\x44\x44\x44\x44\x44\x38\x00', # O
            b'\x78\x44\x44\x78\x40\x40\x40\x00', # P
            b'\x38\x44\x44\x44\x54\x48\x34\x00', # Q
            b'\x78\x44\x44\x78\x50\x48\x44\x00', # R
            b'\x38\x44\x40\x38\x04\x44\x38\x00', # S
            b'\x7c\x10\x10\x10\x10\x10\x10\x00', # T
            b'\x44\x44\x44\x44\x44\x44\x38\x00', # U
            b'\x44\x44\x44\x44\x44\x28\x10\x00', # V
            b'\x44\x44\x44\x54\x54\x54\x28\x00', # W
            b'\x44\x44\x28\x10\x28\x44\x44\x00', # X
            b'\x44\x44\x44\x28\x10\x10\x10\x00', # Y
            b'\x7c\x04\x08\x10\x20\x40\x7c\x00', # Z
            b'\x38\x20\x20\x20\x20\x20\x38\x00', # [
            b'\x00\x40\x20\x10\x08\x04\x00\x00', # \
            b'\x38\x08\x08\x08\x08\x08\x38\x00', # ]
            b'\x10\x28\x44\x00\x00\x00\x00\x00', # ^
            b'\x00\x00\x00\x00\x00\x00\x00\xfc', # _
            b'\x20\x10\x00\x00\x00\x00\x00\x00', # `
            b'\x00\x00\x38\x04\x3c\x44\x3c\x00', # a
            b'\x40\x40\x58\x64\x44\x44\x78\x00', # b
            b'\x00\x00\x38\x44\x40\x44\x38\x00', # c
            b'\x04\x04\x34\x4c\x44\x44\x3c\x00', # d
            b'\x00\x00\x38\x44\x7c\x40\x38\x00', # e
            b'\x18\x24\x20\x70\x20\x20\x20\x00', # f
            b'\x00\x00\x3c\x44\x44\x3c\x04\x38', # g
            b'\x40\x40\x58\x64\x44\x44\x44\x00', # h
            b'\x10\x00\x30\x10\x10\x10\x38\x00', # i
            b'\x08\x00\x18\x08\x08\x08\x48\x30', # j
            b'\x40\x40\x48\x50\x60\x50\x48\x00', # k
            b'\x30\x10\x10\x10\x10\x10\x38\x00', # l
            b'\x00\x00\x68\x54\x54\x44\x44\x00', # m
            b'\x00\x00\x58\x64\x44\x44\x44\x00', # n
            b'\x00\x00\x38\x44\x44\x44\x38\x00', # o
            b'\x00\x00\x78\x44\x44\x78\x40\x40', # p
            b'\x00\x00\x3c\x44\x44\x3c\x04\x04', # q
            b'\x00\x00\x58\x64\x40\x40\x40\x00', # r
            b'\x00\x00\x38\x40\x38\x04\x78\x00', # s
            b'\x20\x20\x70\x20\x20\x24\x18\x00', # t
            b'\x00\x00\x44\x44\x44\x4c\x34\x00', # u
            b'\x00\x00\x44\x44\x44\x28\x10\x00', # v
            b'\x00\x00\x44\x44\x54\x54\x28\x00', # w
            b'\x00\x00\x44\x28\x10\x28\x44\x00', # x
            b'\x00\x00\x44\x44\x44\x3c\x04\x38', # y
            b'\x00\x00\x7c\x08\x10\x20\x7c\x00', # z
            b'\x08\x10\x10\x20\x10\x10\x08\x00', # {
            b'\x10\x10\x10\x00\x10\x10\x10\x00', # |
            b'\x20\x10\x10\x08\x10\x10\x20\x00', # }
            b'\x00\x00\x24\x48\x00\x00\x00\x00', # ~
            b'\x00\x00\x00\x00\x00\x00\x00\x00',
        )
        
        x_orig = x
        for char in text:
            # Verifica caracteres ASCII imprimíveis
            if 32 <= ord(char) <= 126:
                char_idx = ord(char) - 32
                # Desenha cada bit do caractere
                char_bitmap = _FONT[char_idx]
                
                # Trata quebra de linha
                if char == '\n':
                    y += 8 * font_size
                    x = x_orig
                    continue
                
                # Desenha o caractere pixel a pixel
                for row in range(8):
                    for col in range(8):
                        if char_bitmap[row] & (1 << (7 - col)):
                            # Desenha pixels maiores de acordo com font_size
                            for fs_y in range(font_size):
                                for fs_x in range(font_size):
                                    self.pixel(x + col * font_size + fs_x, 
                                             y + row * font_size + fs_y, 
                                             color)
                        elif bg_color is not None:
                            # Desenha fundo se especificado
                            for fs_y in range(font_size):
                                for fs_x in range(font_size):
                                    self.pixel(x + col * font_size + fs_x, 
                                             y + row * font_size + fs_y, 
                                             bg_color)
                
                # Avança o cursor horizontal
                x += 8 * font_size
                
                # Verifica se precisa fazer quebra de linha
                if x + 8 * font_size > self.width:
                    y += 8 * font_size
                    x = x_orig