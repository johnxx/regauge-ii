import machine
import lcd_bus
from micropython import const
from collections import deque

from i2c import I2C
# i2c_bus = I2C.Bus(0, scl=10, sda=11, freq=100_000)
# io_exp_i2c = I2C.Device(i2c_bus, 0x20)
# import io_expander_framework
# import tca9554
# tca9554._INPUT_PORT_REG = const(0x00)
# tca9554._OUTPUT_PORT_REG = const(0x01)
# tca9554._POLARITY_INVERSION_REG = const(0x02)
# tca9554._CONFIGURATION_REG = const(0x03)

# io_expander_framework.Pin.set_device(io_exp_i2c)
# ex2 = tca9554.Pin(tca9554.EXIO2, mode=io_expander_framework.Pin.OUT, pull=io_expander_framework.Pin.PULL_DOWN, value=1)
# ex2.value(0)
# time.sleep_ms(10)
# ex2.value(1)
# time.sleep_ms(50)

# LCD parameters
_WIDTH = const(360)
_HEIGHT = const(360)
_DEPTH = const(16)

# LCD SPI Bus
# Using 
_HOST = const(1)
_FREQ = const(50 * 1000 * 1000)
_SCK = const(40)
_CS = const(21)
_DC = const(0)
_SDA0 = const(46)
_SDA1 = const(45)
_SDA2 = const(42)
_SDA3 = const(41)

# LCD GPIO Pins
_BACKLIGHT = const(5)
_RESET = const(0)
_TEAR = const(24)

def setup_hardware(config):
    lcd_spi_bus = machine.SPI.Bus(
        host=_HOST,
        mosi=_SDA0,
        miso=_SDA1,
        sck=_SCK,
        quad_pins=(_SDA2, _SDA3), # type: ignore
    )

    display_bus = lcd_bus.SPIBus(
        spi_bus=lcd_spi_bus,
        freq=_FREQ,
        cs=_CS,
        dc=_DC,
        quad=True,
    )

    import st77916
    import lvgl as lv

    display = st77916.ST77916(
        data_bus=display_bus,
        display_width=_WIDTH,
        display_height=_HEIGHT,
        backlight_pin=_BACKLIGHT,
        reset_pin=_RESET,
        color_space=lv.COLOR_FORMAT.RGB565,
        color_byte_order=st77916.BYTE_ORDER_BGR,
        rgb565_byte_swap=True,
    )

    display.set_power(False)
    display.init()
    display.set_backlight(100)

    return {
        'display': display,
    }