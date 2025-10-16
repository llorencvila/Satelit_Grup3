import serial
import matplotlib.pyplot as plt
import time

device = 'COM7'
mySerial = serial.Serial(device, 9600)
print("funcionant:")

t0= time.time()
histH = [] #Llista on es guarden totes les deades de humitat a mode de historial
histT = [] #Llista on es guarden totes les temperatures a mode de historial
contact = [] #Llista on es guarden tots els temps (des de l'inici del programa) en que s'han rebut dades des de la estació de terra. (Serveix com a historial i es pot utilitzar per trobar errors de comunicació)
parametres = 2 #Numero de paràmetres separats per ":" que el programa espera rebre. Si rep menys que dita quanitat donarà com a invàlida la recepció de dades per tal d'evitar problemes més endevant
plt.ion()

def temps(): #retorna el temps transcorregut des de l'inici del programa 
   return time.time()-t0 
   
def GrafiquesSeparades(): #Funció per crear una sol element amb dues gràfiques (Temperatura i humitat)
   plt.subplot(2,1,1)
   plt.title("Temp (º) / t (s)")
   plt.plot(contact, histT)
   plt.subplot(2,1,2)
   plt.title("Hum (%) / t (s)")
   plt.plot(contact, histH)

   plt.show()
   return
def GTemp(): #Funció per crear una sola gràfica de temperatura
   return
def GHum(): #Funció per crear una sola gràfica d'hunmitat
   return
def GDobleEix():#Work in progress
   return
   
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

            GrafiquesSeparades()
            plt.pause(0.5)
except KeyboardInterrupt:
   print("Tancant....")
finally:
   mySerial.close
         
   
