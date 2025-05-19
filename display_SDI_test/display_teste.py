# exemplo_display.py
import time
from machine import Pin
import st7789_simplified

# Pinos do seu display
SPI_SCL = 18      # D18 - SCL
SPI_SDA = 23      # D23 - SDA (MOSI) 
RST = 4           # D4 - RES
DC = 15           # D15 - DC
BLK = 22          # D22 - BLK (Backlight)

# Criar o objeto do display
display = st7789_simplified.ST7789(
    spi_sck=SPI_SCL,
    spi_mosi=SPI_SDA,
    rst=RST,
    dc=DC,
    bl=BLK
)

# Exemplo de uso
def run_demo():
    # Limpa o display
    display.fill(display.BLACK)
    time.sleep(0.5)
    
    # Mostra texto
    display.text("Teste do Display", 10, 10, display.WHITE, font_size=1)
    display.text("ST7789 - 240x240", 10, 60, display.YELLOW, font_size=1)
    time.sleep(2)
    
    # Desenha formas básicas
    display.fill(display.BLACK)
    
    # Retângulos
    display.fill_rect(20, 20, 80, 80, display.RED)
    display.fill_rect(140, 20, 80, 80, display.GREEN)
    display.fill_rect(20, 140, 80, 80, display.BLUE)
    display.fill_rect(140, 140, 80, 80, display.YELLOW)
    
    # Bordas
    display.rect(10, 10, 100, 100, display.WHITE)
    display.rect(130, 10, 100, 100, display.WHITE)
    display.rect(10, 130, 100, 100, display.WHITE)
    display.rect(130, 130, 100, 100, display.WHITE)
    time.sleep(2)
    
    # Texto centralizado
    display.fill(display.BLACK)
    display.text("Projeto ESP32", 15, 100, display.CYAN, font_size=2)
    display.text("Funcionando!", 30, 140, display.GREEN, font_size=2)

# Executar a demonstração
run_demo()