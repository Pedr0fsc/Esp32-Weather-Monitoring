# Este é o arquivo st7789.py que você precisa salvar no seu computador
# e depois transferir para o ESP32

# Driver for ST7789 based displays.
# Source: https://github.com/russhughes/st7789_mpy

import time
from micropython import const
import ustruct as struct

# commands
ST7789_NOP = const(0x00)
ST7789_SWRESET = const(0x01)
ST7789_RDDID = const(0x04)
ST7789_RDDST = const(0x09)

ST7789_SLPIN = const(0x10)
ST7789_SLPOUT = const(0x11)
ST7789_PTLON = const(0x12)
ST7789_NORON = const(0x13)

ST7789_INVOFF = const(0x20)
ST7789_INVON = const(0x21)
ST7789_DISPOFF = const(0x28)
ST7789_DISPON = const(0x29)
ST7789_CASET = const(0x2A)
ST7789_RASET = const(0x2B)
ST7789_RAMWR = const(0x2C)
ST7789_RAMRD = const(0x2E)

ST7789_PTLAR = const(0x30)
ST7789_COLMOD = const(0x3A)
ST7789_MADCTL = const(0x36)

ST7789_FRMCTR1 = const(0xB1)
ST7789_FRMCTR2 = const(0xB2)
ST7789_FRMCTR3 = const(0xB3)
ST7789_INVCTR = const(0xB4)
ST7789_DISSET5 = const(0xB6)

ST7789_PVGAMCTRL = const(0xE0)
ST7789_NVGAMCTRL = const(0xE1)
ST7789_DGMLUTR = const(0xE2)
ST7789_DGMLUTB = const(0xE3)
ST7789_GATECTRL = const(0xE4)
ST7789_SPI2EN = const(0xE7)
ST7789_PWCTRL1 = const(0xD0)
ST7789_PWCTRL2 = const(0xD1)
ST7789_VMCTRL1 = const(0xD2)
ST7789_VMCTRL2 = const(0xD3)
ST7789_PWRCTRL6 = const(0xFC)

ST7789_GMCTRP1 = const(0xE0)
ST7789_GMCTRN1 = const(0xE1)

# Rotation-specific values
MADCTL_MY = const(0x80)  # Page Address Order
MADCTL_MX = const(0x40)  # Column Address Order
MADCTL_MV = const(0x20)  # Page/Column Order
MADCTL_ML = const(0x10)  # Line Address Order
MADCTL_RGB = const(0x00)  # RGB Order
MADCTL_BGR = const(0x08)  # BGR Order

# Color definitions
BLACK = const(0x0000)
BLUE = const(0x001F)
RED = const(0xF800)
GREEN = const(0x07E0)
CYAN = const(0x07FF)
MAGENTA = const(0xF81F)
YELLOW = const(0xFFE0)
WHITE = const(0xFFFF)

_ENCODE_PIXEL = const(">H")
_ENCODE_POS = const(">HH")
_DECODE_PIXEL = const(">BBB")

_BUFFER_SIZE = const(256)


def delay_ms(ms):
    time.sleep_ms(ms)


def color565(r, g, b):
    """Convert red, green and blue values (0-255) into a 16-bit 565 encoding."""
    return (r & 0xF8) << 8 | (g & 0xFC) << 3 | b >> 3


class ST7789:
    """Serial interface for ST7789 display controller."""

    def __init__(
        self,
        spi,
        width,
        height,
        reset,
        dc,
        cs=None,
        backlight=None,
        rotation=0,
        xstart=0,
        ystart=0,
    ):
        """Initialize the display. The reset pin is required and must be a valid Pin object,
        as must the dc pin. The cs pin is optional and can be a Pin object,
        or None if the CS pin is not used. Backlight is optional and can be a Pin object,
        or None if the backlight is not used."""
        self.width = width
        self.height = height
        self.spi = spi
        self.reset = reset
        self.dc = dc
        self.cs = cs
        self.backlight = backlight
        self._xstart = xstart
        self._ystart = ystart
        self.rotation = rotation
        self.buffer = bytearray(_BUFFER_SIZE * 2)
        self.init()

    def init(self):
        """Initialize the display."""
        if self.cs:
            self.cs.init(self.cs.OUT, value=1)
        self.dc.init(self.dc.OUT, value=0)
        if self.reset:
            self.reset.init(self.reset.OUT, value=0)
            delay_ms(5)
            self.reset.value(1)
        if self.backlight:
            self.backlight.init(self.backlight.OUT, value=1)

        delay_ms(150)  # 150ms delay after reset
        self._write(ST7789_SWRESET)
        delay_ms(150)

        # Initialize display
        self._write(ST7789_SLPOUT)  # Wake from sleep
        delay_ms(10)

        self._write(ST7789_COLMOD, b"\x55")  # Set color mode: 16-bit color
        delay_ms(10)

        self._write(ST7789_MADCTL, bytes([0x00]))  # Set memory data access control

        # Rotation
        self.set_rotation(self.rotation)

        self._write(ST7789_INVON)  # Inversion on
        delay_ms(10)

        self._write(ST7789_NORON)  # Normal display on
        delay_ms(10)

        self._write(ST7789_DISPON)  # Display on
        delay_ms(10)

    def set_rotation(self, rotation):
        """Set the display rotation."""
        rotation = rotation % 4
        self.rotation = rotation
        madctl = 0
        
        if rotation == 0:  # Portrait
            self.width = 240
            self.height = 240
            madctl = 0
        elif rotation == 1:  # Landscape
            self.width = 240
            self.height = 240
            madctl = MADCTL_MX | MADCTL_MV
        elif rotation == 2:  # Inverted Portrait
            self.width = 240
            self.height = 240
            madctl = MADCTL_MX | MADCTL_MY
        elif rotation == 3:  # Inverted Landscape
            self.width = 240
            self.height = 240
            madctl = MADCTL_MY | MADCTL_MV

        self._write(ST7789_MADCTL, bytes([madctl | MADCTL_BGR]))

    def _write(self, command=None, data=None):
        """Write a command and/or data to the display."""
        if command is not None:
            if self.cs:
                self.cs.value(0)
            self.dc.value(0)
            self.spi.write(bytes([command]))
            if self.cs:
                self.cs.value(1)
        if data is not None:
            if self.cs:
                self.cs.value(0)
            self.dc.value(1)
            self.spi.write(data)
            if self.cs:
                self.cs.value(1)

    def _set_window(self, x0, y0, x1, y1):
        """Set the active display area."""
        if x0 == x1 or y0 == y1:
            return
        
        x0 += self._xstart
        x1 += self._xstart
        y0 += self._ystart
        y1 += self._ystart
        
        self._write(ST7789_CASET, struct.pack(_ENCODE_POS, x0, x1))
        self._write(ST7789_RASET, struct.pack(_ENCODE_POS, y0, y1))
        self._write(ST7789_RAMWR)

    def pixel(self, x, y, color):
        """Draw a pixel at the given position."""
        if not 0 <= x < self.width or not 0 <= y < self.height:
            return
        self._set_window(x, y, x + 1, y + 1)
        self._write(None, struct.pack(_ENCODE_PIXEL, color))

    def text(self, text, x, y, color, background=BLACK):
        """Draw text at the given position."""
        import framebuf
        if not 0 <= x < self.width or not 0 <= y < self.height:
            return
        
        buffer = bytearray(8)
        
        framebuf_obj = framebuf.FrameBuffer(buffer, 8, 8, framebuf.MONO_VLSB)
        
        for char in text:
            framebuf_obj.fill(0)
            framebuf_obj.text(char, 0, 0, 1)
            
            self._set_window(x, y, x + 8, y + 8)
            
            for i in range(8):
                line = buffer[i]
                for j in range(8):
                    if line & (1 << j):
                        self._write(None, struct.pack(_ENCODE_PIXEL, color))
                    else:
                        self._write(None, struct.pack(_ENCODE_PIXEL, background))
            
            x += 8
            if x + 8 > self.width:
                x = 0
                y += 8
                if y + 8 > self.height:
                    break

    def fill_rect(self, x, y, width, height, color):
        """Draw a filled rectangle."""
        if not 0 <= x < self.width or not 0 <= y < self.height:
            return
        if x + width > self.width:
            width = self.width - x
        if y + height > self.height:
            height = self.height - y
        
        self._set_window(x, y, x + width, y + height)
        
        chunks, remainder = divmod(width * height, _BUFFER_SIZE)
        
        if chunks:
            pixel_buffer = struct.pack(_ENCODE_PIXEL, color) * _BUFFER_SIZE
            for _ in range(chunks):
                self._write(None, pixel_buffer)
        
        if remainder:
            self._write(None, struct.pack(_ENCODE_PIXEL, color) * remainder)

    def fill(self, color):
        """Fill the entire display with a color."""
        self.fill_rect(0, 0, self.width, self.height, color)

    def hline(self, x, y, length, color):
        """Draw a horizontal line."""
        self.fill_rect(x, y, length, 1, color)

    def vline(self, x, y, length, color):
        """Draw a vertical line."""
        self.fill_rect(x, y, 1, length, color)

    def rect(self, x, y, width, height, color):
        """Draw a rectangle."""
        self.hline(x, y, width, color)
        self.hline(x, y + height - 1, width, color)
        self.vline(x, y, height, color)
        self.vline(x + width - 1, y, height, color)