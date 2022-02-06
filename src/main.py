from machine import Pin, Timer, SoftI2C, ADC
import machine
import time
import network
import urequests as requests
import ujson
import random
import time
from machine import Pin
from neopixel import NeoPixel

def get_raw_values():
    i2c.start()
    a = i2c.readfrom_mem(104, 0x3B, 14)
    print(a)
    i2c.stop()
    return a

def get_ints():
    b = get_raw_values()
    c = []
    for i in b:
        print(i)
        c.append(i)
    return c

def bytes_toint(firstbyte, secondbyte):
    if not firstbyte & 0x80:
        return firstbyte << 8 | secondbyte
    return - (((firstbyte ^ 255) << 8) | (secondbyte ^ 255) + 1)

def get_values():
    raw_ints = get_raw_values()
    vals = {}
    vals["AcX"] = bytes_toint(raw_ints[0], raw_ints[1])
    vals["AcY"] = bytes_toint(raw_ints[2], raw_ints[3])
    vals["AcZ"] = bytes_toint(raw_ints[4], raw_ints[5])
    vals["Tmp"] = bytes_toint(raw_ints[6], raw_ints[7]) / 340.00 + 36.53
    vals["GyX"] = bytes_toint(raw_ints[8], raw_ints[9])
    vals["GyY"] = bytes_toint(raw_ints[10], raw_ints[11])
    vals["GyZ"] = bytes_toint(raw_ints[12], raw_ints[13])
    return vals  # returned in range of Int16

pA0 = Pin(25, Pin.OUT)
pA1 = Pin(26, Pin.OUT)
pA2 = Pin(27, Pin.OUT)

pRESET = Pin(33, Pin.OUT)
pRESET.value(1)



pin = Pin(5, Pin.OUT)   # set GPIO5 to output to drive NeoPixels
np = NeoPixel(pin, 36)   # create NeoPixel driver on GPIO0 for 8 pixels

def clearFace(face):
    np[0 + face*6] = (0, 0, 0)
    np[1 + face*6] = (0, 0, 0)
    np[2 + face*6] = (0, 0, 0)
    np[3 + face*6] = (0, 0, 0)
    np[4 + face*6] = (0, 0, 0)
    np[5 + face*6] = (0, 0, 0)

def lightRed(face):
    np[0 + face*6] = (120, 0, 0)
    np[1 + face*6] = (120, 0, 0)
    np[2 + face*6] = (120, 0, 0)
    np[3 + face*6] = (120, 0, 0)
    np[4 + face*6] = (120, 0, 0)
    np[5 + face*6] = (120, 0, 0)

def lightBlue(face):
    np[0 + face*6] = (0, 0, 120)
    np[1 + face*6] = (0, 0, 120)
    np[2 + face*6] = (0, 0, 120)
    np[3 + face*6] = (0, 0, 120)
    np[4 + face*6] = (0, 0, 120)
    np[5 + face*6] = (0, 0, 120)

def lightGreen(face):
    np[0 + face*6] = (0, 120, 0)
    np[1 + face*6] = (0, 120, 0)
    np[2 + face*6] = (0, 120, 0)
    np[3 + face*6] = (0, 120, 0)
    np[4 + face*6] = (0, 120, 0)
    np[5 + face*6] = (0, 120, 0)

activeFace = 0
lastActiveFace = -1
while True:
    if lastActiveFace > -1:
        clearFace(lastActiveFace)
    lightRed(activeFace)
    lastActiveFace = activeFace
    activeFace+=1
    if activeFace == 6:
        activeFace = 0

    np.write()
    time.sleep(1)

#START I2C
addr=0x70
SCL = Pin(22, Pin.OUT)
SDA = Pin(21, Pin.OUT)
i2c = SoftI2C(SCL, SDA)
#direct multiplex
pA0.value(0)
pA1.value(0)
pA2.value(0)
#activate line 0x70
i2c.start()
i2c.writeto(0x70, bytearray([0x01])) 
i2c.stop()
print(i2c.scan())



# list of commands in hex for MS5837
c_reset = const(0x1E) # reset command
r_c1 = const(0xA2) # read PROM C1 command
r_c2 = const(0xA4) # read PROM C2 command
r_c3 = const(0xA6) # read PROM C3 command
r_c4 = const(0xA8) # read PROM C4 command
r_c5 = const(0xAA) # read PROM C5 command
r_c6 = const(0xAC) # read PROM C6 command
r_adc = const(0x00) # read ADC command
r_d1 = const(0x43) # convert D1 (OSR=1024)
r_d2 = const(0x54) # convert D2 (OSR=1024)
slave_addr = 0x76  
# reset device to make sure PROM loaded
data = bytearray([c_reset])
i2c.writeto(slave_addr, data)


def read_c1(): #read PROM value C1
  data = bytearray([r_c1])
  i2c.writeto(slave_addr, data)
  raw_c = i2c.readfrom(slave_addr, 2) #raw C is 2 bytes
  value = int.from_bytes(raw_c, "big") # use builtin to convert to integer
  return value

def read_c2(): #read PROM value C2
  data = bytearray([r_c2])
  i2c.writeto(slave_addr, data)
  raw_c = i2c.readfrom(slave_addr, 2) #raw C is 2 bytes
  value = int.from_bytes(raw_c, "big") # use builtin to convert to unsigned integer
  return value

def read_c3(): #read PROM value C3
  data = bytearray([r_c3])
  i2c.writeto(slave_addr, data)
  raw_c = i2c.readfrom(slave_addr, 2) #raw C is 2 bytes
  value = int.from_bytes(raw_c, "big") # use builtin to convert to unsigned integer
  return value

def read_c4(): #read PROM value C4
  data = bytearray([r_c4])
  i2c.writeto(slave_addr, data)
  raw_c = i2c.readfrom(slave_addr, 2) #raw C is 2 bytes
  value = int.from_bytes(raw_c, "big") # use builtin to convert to unsigned integer
  return value

def read_c5(): #read PROM value C5
  data = bytearray([r_c5])
  i2c.writeto(slave_addr, data)
  raw_c = i2c.readfrom(slave_addr, 2) #raw C is 2 bytes
  value = int.from_bytes(raw_c, "big") # use builtin to convert to unsigned integer
  return value

def read_c6(): #read PROM value C6
  data = bytearray([r_c6])
  i2c.writeto(slave_addr, data)
  raw_c = i2c.readfrom(slave_addr, 2) #raw C is 2 bytes
  value = int.from_bytes(raw_c, "big") # use builtin to convert to unsigned integer
  return value
  
# read PROM calibration data  
C1 = read_c1()
C2 = read_c2()
C3 = read_c3()
C4 = read_c4()
C5 = read_c5()
C6 = read_c6()

print ('PROM C1 = ', C1)
print ('PROM C2 = ', C2)
print ('PROM C3 = ', C3)
print ('PROM C4 = ', C4)
print ('PROM C5 = ', C5)
print ('PROM C6 = ', C6)

# start D1 conversion - pressure (24 bit unsigned)
def start_d1():
  #print ('start D1 ')
  data = bytearray([r_d1])
  i2c.writeto(slave_addr, data)

# start D2 conversion - temperature (24 bit unsigned)  
def start_d2():
  #print ('start D2 ')
  data = bytearray([r_d2])
  i2c.writeto(slave_addr, data) 

#read ADC
def read_adc(): #read ADC 24 bits unsigned
  data = bytearray([r_adc])
  i2c.writeto(slave_addr, data)
  adc = i2c.readfrom(slave_addr, 3) #ADC is 3 bytes
  value = int.from_bytes(adc, "big") # use builtin to convert to integer
  return value

# while True:
#     # read ms5837
#     slave_addr = 0x76
#     start_d1() # start D1 conversion
#     time.sleep(0.01) # short delay during conversion
#     raw_d1 = read_adc()
#     start_d2() # start D2 conversion
#     time.sleep(0.01)
#     raw_d2 = read_adc()
#     dT = raw_d2 - (C5 * 256) # difference between actual and ref temp
#     Temp = 2000 + (dT * (C6/8388608)) #actual temperature is /100
#     OFF = (C2*131072) + (C4*dT/64) # offset at actual temperature
#     SENS = (C1*65536) + (C3*dT/128) # pressure offset at actual temperature
#     # need to add second order temp compensation if <20C
#     if Temp < 2000: # add 2nd order correction when temp < 20C
#         Ti = 11*dT**2/34359738368
#         OFFi = (31*(Temp - 2000)**2)/8
#         SENSi = (63*(Temp - 2000)**2)/32
#     else:
#         Ti = 0
#         OFFi = 0
#         SENSi = 0
#     #print ('Ti = ', Ti)
#     SENS = SENS - SENSi
#     OFF = OFF - OFFi
#     Pres = (raw_d1*SENS/2097152 - OFF)/3276800 # barometric pressure
#     # 

#     Temp = Temp/100
#     fTemp = (Temp*9/5) + 32
#     #print ('Temp = ', '%.1fC' % Temp)
#     #print ('Temp = ', '%.1fF' % fTemp)
#     print ('Pressure = ', '%.1f ' % Pres)
# i2c.start()
# a = i2c.readfrom_mem(118, 0xA6, 2)
# print(a)
# i2c.stop()
# print(bytes_toint(a[0], a[1]))

# while True:
#     i2c.start()
#     i2c.writeto(118, bytearray([0x48]))
#     i2c.stop()
#     time.sleep(0.1)
#     b = i2c.readfrom_mem(118, 0x40, 2)
#     print(int.from_bytes(b, "big"))
#     time.sleep(0.1)
    


# #ACTIVATE POWER ON IMU
# ##working
# i2c.start()
# i2c.writeto_mem(0x68, 0x6B, bytes([0]))
# i2c.stop()
# while True:
#     get_values()
#     print(get_values())
#     time.sleep(0.1)
# ##working




#while True:
    # pA0.value(0)
    # pA1.value(0)
    # pA2.value(0)
    # print("0 0 0")
    # print(i2c.scan())
    # time.sleep(0.1)
    # pA0.value(0)
    # pA1.value(0)
    # pA2.value(1)
    # print("0 0 1")
    # print(i2c.scan())
    # time.sleep(0.1)
    # pA0.value(0)
    # pA1.value(1)
    # pA2.value(0)
    # print("0 1 0")
    # print(i2c.scan())
    # time.sleep(0.1)
    # pA0.value(0)
    # pA1.value(1)
    # pA2.value(1)
    # print("0 1 1")
    # print(i2c.scan())
    # time.sleep(0.1)
    # pA0.value(1)
    # pA1.value(0)
    # pA2.value(0)
    # print("1 0 0")
    # print(i2c.scan())
    # time.sleep(0.1)
    # pA0.value(1)
    # pA1.value(0)
    # pA2.value(1)
    # print("1 0 1")
    # print(i2c.scan())
    # time.sleep(0.1)
    # pA0.value(1)
    # pA1.value(1)
    # pA2.value(0)
    # print("1 1 0")
    # print(i2c.scan())
    # time.sleep(0.1)
    # pA0.value(1)
    # pA1.value(1)
    # pA2.value(1)
    # print("1 1 1")
    # print(i2c.scan())
    # time.sleep(0.1)
    # np[0] = (120, 0, 0) # set the first pixel to white
    # np[1] = (120, 0, 0) # set the first pixel to white
    # np[2] = (120, 0, 0) # set the first pixel to white
    # np[3] = (120, 0, 0) # set the first pixel to white
    # np[4] = (120, 0, 0) # set the first pixel to white
    # np[5] = (120, 0, 0) # set the first pixel to white

    # np.write() 
    # time.sleep(0.1)

# def controlFace0():
#     np[0] = (120, 0, 0) # set the first pixel to white
#     np[1] = (120, 0, 0) # set the first pixel to white
#     np[2] = (120, 0, 0) # set the first pixel to white
#     np[3] = (120, 0, 0) # set the first pixel to white
#     np[4] = (120, 0, 0) # set the first pixel to white
#     np[5] = (120, 0, 0) # set the first pixel to white

# def controlFace1():
#     np[6] = (120, 0, 0) # set the first pixel to white
#     np[7] = (120, 0, 0) # set the first pixel to white
#     np[8] = (120, 0, 0) # set the first pixel to white
#     np[9] = (120, 0, 0) # set the first pixel to white
#     np[10] = (120, 0, 0) # set the first pixel to white
#     np[11]] = (120, 0, 0) # set the first pixel to white

# 
#     time.sleep(5.0)
#     i2c.init(I2C.CONTROLLER)
#     print(i2c.scan())
#     #print(get_values())
#     print("---")
#     # print(CONTEXT)


