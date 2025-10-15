from tkinter import *
import matplotlib.pyplot as plt
import serial
import time
import threading


device = 'COM7'
mySerial = serial.Serial(device, 9600)
print("funcionant:")

estat = "Escoltant"
t0= time.time()
histH = []
histT = []
contact = []
parametres = 2 #
plt.ion()

def temps():
   return time.time()-t0
#def start():

def stop():
    mensaje = "STOP"
    mySerial.write(mensaje.encode('utf-8'))
    print("STOP")
    #mySerial.close

def resume():
    mensaje = "REANUDAR"
    mySerial.write(mensaje.encode('utf-8'))
    print("REANUDAR")

def recepcion():
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

#threadRecepcion = threading.Thread (target = recepcion)
#threadRecepcion.start()

#def inicar():
    

window = Tk()
window.geometry("400x400")
window.rowconfigure(0, weight=1)
window.rowconfigure(1, weight=1)
window.rowconfigure(2, weight=1)
window.rowconfigure(3, weight=1)
window.columnconfigure(0, weight=1)
window.columnconfigure(1, weight=1)
window.columnconfigure(2, weight=1)
window.columnconfigure(3, weight=1)


Binici = Button(window, text="Inici", bg='green', fg="black",command=resume)
Binici.grid(row=3, column=0, padx=5, pady=4, sticky=N + S + E + W)

BStop = Button(window, text="Stop", bg='red', fg="white",command=stop)
BStop.grid(row=3, column=1, padx=5, pady=4, sticky=N + S + E + W)

"""
EstatBar = Frame(window,)
tituloLabel.grid(row=3, column=2, columnspan=1, padx=1, pady=1, sticky=N + S + E + W)
"""

window.mainloop()