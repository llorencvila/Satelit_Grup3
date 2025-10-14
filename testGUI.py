from tkinter import *
import serial

device = 'COM10'
mySerial = serial.Serial(device, 9600)
print("funcionant:")

estat = "Escoltant"

#def start():

def stop():
    mensaje = "STOP"
    mySerial.write(mensaje.encode('utf-8'))

def resume():
    mensaje = "REANUDAR"
    mySerial.write(mensaje.encode('utf-8'))

def dades():
    threadRecepcion = threading.Thread (target = recepcion)
    threadRecepcion.start()

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


Binici = Button(window, text="Inici", bg='green', fg="black",command=resume())
Binici.grid(row=3, column=0, padx=5, pady=4, sticky=N + S + E + W)

BStop = Button(window, text="Stop", bg='red', fg="white",command=stop())
BStop.grid(row=3, column=1, padx=5, pady=4, sticky=N + S + E + W)

"""
EstatBar = Frame(window,)
tituloLabel.grid(row=3, column=2, columnspan=1, padx=1, pady=1, sticky=N + S + E + W)
"""

window.mainloop()