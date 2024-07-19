# pins_lib/shield.py
from machine import Pin, PWM, ADC
import time

class Shield:
    def __init__(self, pin_red=3, pin_green=17, pin_blue=19, pin_buzzer=11, pin_led1=16, pin_led2=18, pin_button1=4, pin_button2=5, pin_analog= 26):
        self.led_red = Pin(pin_red, Pin.OUT)
        self.led_green = Pin(pin_green, Pin.OUT)
        self.led_blue = Pin(pin_blue, Pin.OUT)
        self.buzzer = PWM(Pin(pin_buzzer))
        self.led1 = Pin(pin_led1, Pin.OUT)
        self.led2 = Pin(pin_led2, Pin.OUT)
        self.button1 = Pin(pin_button1, Pin.IN, Pin.PULL_UP)
        self.button2 = Pin(pin_button2, Pin.IN, Pin.PULL_UP)
        self.analog_sensor = ADC(Pin(pin_analog))

    def set_led(self, color):
        colors = {
            'red': (1, 0, 0),
            'green': (0, 1, 0),
            'blue': (0, 0, 1),
            'yellow': (1, 1, 0),
            'cyan': (0, 1, 1),
            'magenta': (1, 0, 1),
            'white': (1, 1, 1),
            'off': (0, 0, 0)
        }
        if color in colors:
            self.led_red.value(colors[color][0])
            self.led_green.value(colors[color][1])
            self.led_blue.value(colors[color][2])
        else:
            raise ValueError("Color not supported")

    def play_tone(self, frequency, duration):
        self.buzzer.freq(frequency)
        self.buzzer.duty_u16(32768)  # Configura el duty cycle al 50%
        time.sleep(duration)
        self.buzzer.duty_u16(0)  # Apaga el buzzer

    def read_button1(self):
        return self.button1.value()

    def read_button2(self):
        return self.button2.value()

    def set_led1(self, state):
        self.led1.value(state)

    def set_led2(self, state):
        self.led2.value(state)

    def read_analog(self):
        return self.analog_sensor.read_u16()

    def deinit(self):
        self.led_red.value(0)
        self.led_green.value(0)
        self.led_blue.value(0)
        self.buzzer.deinit()
        self.led1.value(0)
        self.led2.value(0)
