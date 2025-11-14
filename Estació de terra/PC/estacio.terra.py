from tkinter import *
import matplotlib.pyplot as plt
import numpy as np
import serial
import time
import threading
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random


Debug_RecepcioSimulada = False #En cas de ser True s'inventarà les dades de recepció ignorant completament el port sèrie. 
                              #És d'utilitat per fer proves amb el codi si no es disposa del maquinari físic (els dos arduinos)

# ───────────────────────────────────────────────
# CONFIGURACIÓ DEL PORT SÈRIE 
# ───────────────────────────────────────────────
if Debug_RecepcioSimulada == False:
    device = 'COM7'
    mySerial = serial.Serial(device, 9600)
    print("funcionant:")

# ───────────────────────────────────────────────
# VARIABLES GLOBALS
# ───────────────────────────────────────────────
estat = "Escoltant"
t0= time.time()
histH = []
histT = []
histAng = []
histDist = []
contact = []
parametres = 2

# ───────────────────────────────────────────────
# FUNCIONS AUXILIARS HUMITAT I TEMPERATURA
# ───────────────────────────────────────────────
print ("Funcionant")
def temps():
    return time.time() - t0

def stopHT():
    if Debug_RecepcioSimulada == False:
        mensaje = "STOPHT"
        mySerial.write(mensaje.encode('utf-8'))
    print("STOP")
    #mySerial.close

def resumeHT():
    if Debug_RecepcioSimulada == False:
        mensaje = "REANUDARHT"
        mySerial.write(mensaje.encode('utf-8'))
    print("REANUDAR")

def error():
    print("FALLO EN LA TRANSMISSIÓ DE DADES")

def canvi_periodeHT():
    periode_transmisio = "periodeHT" +fraseHTEntry.get()
    mySerial.write(periode_transmisio)
    print ('Has canviat el periode de transimsio a --- ' + fraseHTEntry.get())

# ───────────────────────────────────────────────
# FUNCIONS AUXILIARS distancia
# ───────────────────────────────────────────────

def stop_dist():
    if Debug_RecepcioSimulada == False:
        mensaje = "STOP"
        mySerial.write(mensaje.encode('utf-8'))
    print("STOP")
    #mySerial.close

def resume_dist():
    if Debug_RecepcioSimulada == False:
        mensaje = "REANUDAR"
        mySerial.write(mensaje.encode('utf-8'))
    print("REANUDAR")

def error():
    print("FALLO EN LA TRANSMISSIÓ DE DADES")

def canvi_periode_dist():
    periode_transmisio = "periode" +frase_distEntry.get()
    mySerial.write(periode_transmisio)
    print ('Has canviat el periode de transimsio a --- ' + frase_distEntry.get())
    


# ───────────────────────────────────────────────
# FINESTRA PRINCIPAL TKINTER
# ───────────────────────────────────────────────
window = Tk()
window.geometry("1000x400")
window.title("Control de transmissió de dades")

window.columnconfigure(0, weight=1)
window.columnconfigure(1, weight=1)
window.columnconfigure(2, weight=1)
window.rowconfigure(0, weight=1)
window.rowconfigure(1, weight=1)
window.rowconfigure(2, weight=1)


#tituloLabel = Label(window, text="Transmissió de dades", font=("Courier", 20, "italic"))
#tituloLabel.grid(row=0, column=0, columnspan=5, padx=5, pady=5, sticky=N + S + E + W)

# FRAME CONTROLADOR TEMPERATURA I HUMITAT:
button_HT_frame = LabelFrame(window, text = 'Humitat i Temperatura')
button_HT_frame.grid(row=0, column=0, padx=5, pady=5, sticky=N + S + E + W)

button_HT_frame.rowconfigure(0, weight=1)
button_HT_frame.rowconfigure(1, weight=1)
button_HT_frame.columnconfigure(0, weight=1)
button_HT_frame.columnconfigure(1, weight=1)

IniciarHTButton = Button(button_HT_frame, text="Play", bg='green', fg="white", command=resumeHT)
IniciarHTButton.grid(row=0, column=0, padx=5, pady=5, sticky=N + S + E + W)

PararHTButton = Button(button_HT_frame, text="Pausa", bg='red', fg="white", command=stopHT)
PararHTButton.grid(row=0, column=1, padx=5, pady=5, sticky=N + S + E + W)

AplicarHTButton = Button(button_HT_frame, text="Aplicar", bg='yellow', fg="white", command=canvi_periodeHT)
AplicarHTButton.grid(row=1, column=1, padx=5, pady=5, sticky=N + S + E + W)

fraseHTEntry = Entry(button_HT_frame)
fraseHTEntry.grid(row=1, column=0, columnspan = 1, padx=5, pady=5, sticky=N + S + E + W)

# FRAME CONTROLADOR DADES DE DISTÀNCIA

button_dist_frame = LabelFrame(window, text = 'Sensor de distància')
button_dist_frame.grid(row=1, column=0, padx=5, pady=5, sticky=N + S + E + W)

button_dist_frame.rowconfigure(0, weight=1)
button_dist_frame.rowconfigure(1, weight=1)
button_dist_frame.columnconfigure(0, weight=1)
button_dist_frame.columnconfigure(1, weight=1)

Iniciar_distButton = Button(button_dist_frame, text="Play", bg='green', fg="white", command=resume_dist)
Iniciar_distButton.grid(row=0, column=0, padx=5, pady=5, sticky=N + S + E + W)

Parar_distButton = Button(button_dist_frame, text="Pausa", bg='red', fg="white", command=stop_dist)
Parar_distButton.grid(row=0, column=1, padx=5, pady=5, sticky=N + S + E + W)

Aplicar_distButton = Button(button_dist_frame, text="Aplicar", bg='yellow', fg="white", command=canvi_periode_dist)
Aplicar_distButton.grid(row=1, column=1, padx=5, pady=5, sticky=N + S + E + W)

frase_distEntry = Entry(button_dist_frame)
frase_distEntry.grid(row=1, column=0, columnspan = 1, padx=5, pady=5, sticky=N + S + E + W)

# FRAME GRÀFICA HT
grafHT_frame = LabelFrame(window, text = 'Gràfica temperatura i humitat')
grafHT_frame.grid(row=0, column=1, rowspan = 3, padx=5, pady=5, sticky=N + S + E + W)

grafHT_frame.rowconfigure(0, weight=1)
grafHT_frame.columnconfigure(0, weight=1)

# FRAME GRÀFICA DISTÀNCIA
graf_dist_frame = LabelFrame(window, text = 'Gràfica sensor de distància')
graf_dist_frame.grid(row=0, column=2, rowspan = 3, padx=5, pady=5, sticky=N + S + E + W)

graf_dist_frame.rowconfigure(0, weight=1)
graf_dist_frame.columnconfigure(0, weight=1)


# ───────────────────────────────────────────────
# CONFIGURACIÓ DE LA FIGURA MATPLOTLIB
# ───────────────────────────────────────────────
fig, (axT, axH) = plt.subplots(2, 1, figsize=(5, 3), sharex=True)
fig.subplots_adjust(hspace=0.4)
axT.set_title("Temperatura (°C)")
axH.set_title("Humitat (%)")

lineT, = axT.plot([], [], color='red')
lineH, = axH.plot([], [], color='blue')

axT.set_xlim(0, 60)
axT.set_ylim(0, 50)
axH.set_ylim(0, 100)


#Grafica Radar
figRad = plt.figure()
axRad = figRad.add_subplot(projection='polar')
#cRad = axRad.scatter(AngleRad, DistRad)

# Inserir gràfica a Tkinter
canvas = FigureCanvasTkAgg(fig, master=grafHT_frame)
canvas.get_tk_widget().grid(row=0, column=0, padx=5, pady=5, sticky=N+S+E+W)
canvas.draw()

# ───────────────────────────────────────────────
# FIL DE RECEPCIÓ DE DADES
# ───────────────────────────────────────────────
def recepcion():
    while True:
        if Debug_RecepcioSimulada == False :
            if mySerial and mySerial.in_waiting > 0:
                linea = mySerial.readline().decode('utf-8').rstrip()
                data = linea.split(':') #Type list // data[x] = Type: str

                if len(data) == parametres: #Comprovació que rebem totes les dades
                    contact.append(int(temps()))
                    print("Humitat:", data[0])
                    print("Temp:   ", data[1]) 
                    print("Pos:", (data[2]/4779)*360)
                    print("Dist:   ", data[3]) 
                    #print(temps())
                    histH.append(float(data[0]))
                    histT.append(float(data[1]))
                    histAng.append(float(data[2]))
                    histDist.append(float(data[3]))
                elif data == "FALLO":
                    error()
                    print("Error a la recepció de dades")
        else: 
                histH.append(float("%.2f" % random.uniform(0,100)))
                histT.append(float("%.2f" % random.uniform(10,25)))
                histAng.append(float("%.2f" % random.uniform(0,180)))
                histDist.append(float("%.2f" % random.uniform(0,100)))
                contact.append(int(temps()))
                print(histH)
                print(contact)
                time.sleep(0.5)
        
        #actualitzar_grafica()
        #plt.pause(0.5)

# ───────────────────────────────────────────────
# ACTUALITZACIÓ DE LA GRÀFICA DINS TKINTER
# ───────────────────────────────────────────────
def actualitzar_grafica():
    if contact: #No acabo d'entendre pq es fa servir if contact
        lineT.set_data(contact, histT)
        lineH.set_data(contact, histH)
        print("Grafica actuaitzant-se")
        axT.set_xlim(max(0, contact[-1]-60), contact[-1]+5)
        axH.set_xlim(max(0, contact[-1]-60), contact[-1]+5)

        axT.relim()
        axT.autoscale_view(scaley=True)
        axH.relim()
        axH.autoscale_view(scaley=True)

        canvas.draw_idle()

        #Grafica Radar
        cRad = axRad.scatter(data[2], data[3])

    # tornar a cridar aquesta funció cada 500 ms

    window.after(500, actualitzar_grafica)

# ───────────────────────────────────────────────
# LLANÇAR FIL I INICIAR GUI
# ───────────────────────────────────────────────
 
threadRecepcion = threading.Thread(target=recepcion)
threadRecepcion.start()

# iniciar actualització periòdica
window.after(50, actualitzar_grafica)

def on_close():
    global running
    running = False
    if Debug_RecepcioSimulada == False:
        if mySerial:
            mySerial.close()
    window.destroy()

window.protocol("WM_DELETE_WINDOW", on_close)
window.mainloop()
