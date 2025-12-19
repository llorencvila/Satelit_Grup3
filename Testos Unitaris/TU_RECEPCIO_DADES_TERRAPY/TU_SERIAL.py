import serial
import matplotlib.pyplot as plt
import time

device = 'COM11'
mySerial = serial.Serial(device, 9600)
print("funcionant:")

t0= time.time()
histH = []
histT = []
histAng = []
histDist = []
contact = []
parametres = 2 #


def temps():
   return time.time()-t0
   
try:
   while True:
      if mySerial.in_waiting > 0:
         linea = mySerial.readline().decode('utf-8').rstrip()
         print(linea)


except KeyboardInterrupt:
   print("Tancant....")
finally:
   mySerial.close
         
   
