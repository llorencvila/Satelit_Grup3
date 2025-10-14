import serial
import matplotlib.pyplot as plt
import time

device = 'COM10'
mySerial = serial.Serial(device, 9600)
print("funcionant:")

t0= time.time()
histH = []
histT = []
contact = []
parametres = 2 #
plt.ion()

def temps():
   return time.time()-t0
   
try:
   while True:
      if mySerial.in_waiting > 0:
         linea = mySerial.readline().decode('utf-8').rstrip()
         data = linea.split(':') #Type list // data[x] = Type: str

         if len(data) == parametres: #Comprovació que rebem totes les dades
            contact.append(int(temps()))
            print("Humitat:", data[0])
            print("Temp:   ", data[1]) 
            #print(temps())
            histH.append(float(data[0]))
            histT.append(float(data[1])) 
            print(contact)
            print(float(data[1]))
            plt.plot(contact, histT)
            plt.title("Temperatura/temps")
            plt.draw()
            plt.pause(0.5)

except KeyboardInterrupt:
   print("Tancant....")
finally:
   mySerial.close
         
   
