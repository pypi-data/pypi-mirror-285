"""
Descripción: Esta libreria funciona para la lectura de carateruisticas del la tarjeta de carga, comado como referencia
{Andre Peeters 2017/10/31}<https://github.com/andrethemac/max17043.py/tree/master>
Fecha de creación: 25 de Marzo de 2024
Fecha de modificación:
Versión: 1.0
Dependencias: binascii, machine
modified by: @Cesar
"""
from machine import Pin, I2C
import binascii

class max1704x:
    REGISTER_VCELL = const(0X02)
    REGISTER_SOC = const(0X04)
    REGISTER_MODE = const(0X06)
    REGISTER_VERSION = const(0X08)
    REGISTER_CONFIG = const(0X0C)
    REGISTER_COMMAND = const(0XFE)

    def __init__(self, _id=0, sda_pin=12, scl_pin=13):
        """
        Inicializa el módulo y establece los pines usados para I2C.
        Escanea la dirección I2C (devuelve el primer resultado encontrado).
        """
        self._id = _id
   
        self.sda_pin = sda_pin
        self.scl_pin = scl_pin
        self.i2c = I2C(self._id, sda=Pin(self.sda_pin), scl=Pin(self.scl_pin))
        self.max1704xAddress = self.i2c.scan()[0]

    def __str__(self):
        """
        Representación en forma de cadena de los valores.
        """
        rs  = "La dirección I2C es {}\n".format(self.max1704xAddress)
        rs += "Los pines I2C son SDA: {} y SCL: {}\n".format(self.sda_pin, self.scl_pin)
        rs += "La versión es {}\n".format(self.getVersion())
        rs += "VCell es {} V\n".format(self.getVCell())
        rs += "Compensatevalue es {}\n".format(self.getCompensateValue())
        rs += "El umbral de alerta es {} %\n".format(self.getAlertThreshold())
        rs += "¿Está en alerta? {}\n".format(self.inAlert())
        return rs

    def address(self):
        """
        Devuelve la dirección I2C.
        """
        return self.max1704xAddress

    def reset(self):
        """
        Reinicia el sensor.
        """
        self.__writeRegister(REGISTER_COMMAND, binascii.unhexlify('0054'))

    def getVCell(self):
        """
        Obtiene los voltios restantes en la celda.
        """
        buf = self.__readRegister(REGISTER_VCELL)
        return (buf[0] << 4 | buf[1] >> 4) / 1000.0

    def getSoc(self):
        """
        Obtiene el estado de carga.
        """
        buf = self.__readRegister(REGISTER_SOC)
        return (buf[0] + (buf[1] / 256.0))

    def getVersion(self):
        """
        Obtiene la versión del módulo max17043.
        """
        buf = self.__readRegister(REGISTER_VERSION)
        return (buf[0] << 8) | (buf[1])

    def getCompensateValue(self):
        """
        Obtiene el valor de compensación.
        """
        return self.__readConfigRegister()[0]

    def getAlertThreshold(self):
        """
        Obtiene el nivel de alerta.
        """
        return (32 - (self.__readConfigRegister()[1] & 0x1f))

    def setAlertThreshold(self, threshold):
        """
        Establece el nivel de alerta.
        """
        self.threshold = 32 - threshold if threshold < 32 else 32
        buf = self.__readConfigRegister()
        buf[1] = (buf[1] & 0xE0) | self.threshold
        self.__writeConfigRegister(buf)

    def inAlert(self):
        """
        Comprueba si el módulo max17043 está en alerta.
        """
        return (self.__readConfigRegister())[1] & 0x20

    def clearAlert(self):
        """
        Borra la alerta.
        """
        self.__readConfigRegister()

    def quickStart(self):
        """
        Realiza un reinicio rápido.
        """
        self.__writeRegister(REGISTER_MODE, binascii.unhexlify('4000'))

    def __readRegister(self, address):
        """
        Lee el registro en la dirección especificada, siempre devuelve un bytearray de 2 bytes.
        """
        return self.i2c.readfrom_mem(self.max1704xAddress, address, 2)

    def __readConfigRegister(self):
        """
        Lee el registro de configuración, siempre devuelve un bytearray de 2 bytes.
        """
        return self.__readRegister(REGISTER_CONFIG)

    def __writeRegister(self, address, buf):
        """
        Escribe el buf en la dirección del registro.
        """
        self.i2c.writeto_mem(self.max1704xAddress, address, buf)

    def __writeConfigRegister(self, buf):
        """
        Escribe el buf en el registro de configuración.
        """
        self.__writeRegister(REGISTER_CONFIG, buf)

    def deinit(self):
        """
        Apaga el periférico.
        """
        self.i2c.deinit()

