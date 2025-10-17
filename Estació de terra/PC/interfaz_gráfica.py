from tkinter import *
import serial
import threading
import recepcion
import mySerial



def IniciarClick ():
    threadRecepcion = threading.Thread (target = recepcion)
    threadRecepcion.start()


def PararClick ():
    mensajeP = "PARAR"
    mySerial.write(mensajeP.encode('utf-8'))

def ReanudarClick ():
    mensajeR = "REANUDAR"
    mySerial.write(mensajeR.encode('utf-8'))


window = Tk()
window.geometry("400x400")
window.rowconfigure(0, weight=1)
window.rowconfigure(1, weight=2)



window.columnconfigure(0, weight=1)
window.columnconfigure(1, weight=1)
window.columnconfigure(2, weight=1)


tituloLabel = Label(window, text = "Mi programa", font=("Courier", 20, "italic"))
tituloLabel.grid(row=0, column=0, columnspan=5, padx=5, pady=5, sticky=N + S + E + W)


IniciarButton = Button(window, text="Iniciar", bg='green', fg="white",command=IniciarClick)
IniciarButton.grid(row=1, column=0, padx=5, pady=5, sticky=N + S + E + W)

PararButton = Button(window, text="Parar", bg='red', fg="white",command=PararClick)
PararButton.grid(row=1, column=1, padx=5, pady=5, sticky=N + S + E + W)

ReanudarButton = Button(window, text="Reanudar", bg='yellow', fg="black",command=ReanudarClick )
ReanudarButton.grid(row=1, column=2, padx=5, pady=5, sticky=N + S + E + W)



window.mainloop()