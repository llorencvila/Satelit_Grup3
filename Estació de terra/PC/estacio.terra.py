from tkinter import *
import matplotlib.pyplot as plt
import serial
import time
import threading
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ───────────────────────────────────────────────
# CONFIGURACIÓ DEL PORT SÈRIE 
# ───────────────────────────────────────────────
device = 'COM10'
mySerial = serial.Serial(device, 9600)
print("funcionant:")
#mySerial = None  # permet provar el codi sense Arduino

# ───────────────────────────────────────────────
# VARIABLES GLOBALS
# ───────────────────────────────────────────────
estat = "Escoltant"
t0= time.time()
histH = []
histT = []
contact = []
parametres = 2
running = True  # control del fil

# ───────────────────────────────────────────────
# FUNCIONS AUXILIARS
# ───────────────────────────────────────────────
def temps():
    return time.time() - t0

def stop():
    mensaje = "STOP"
    mySerial.write(mensaje.encode('utf-8'))
    print("STOP")
    #mySerial.close

def resume():
    mensaje = "REANUDAR"
    mySerial.write(mensaje.encode('utf-8'))
    print("REANUDAR")

def error():
    print("FALLO EN LA TRANSMISSIÓ DE DADES")

# ───────────────────────────────────────────────
# FINESTRA PRINCIPAL TKINTER
# ───────────────────────────────────────────────
window = Tk()
window.geometry("1000x400")
window.title("Control de transmissió de dades")

window.rowconfigure(0, weight=1)
window.rowconfigure(1, weight=1)
window.columnconfigure(0, weight=1)
window.columnconfigure(1, weight=1)
window.columnconfigure(2, weight=10)

tituloLabel = Label(window, text="Transmissió de dades", font=("Courier", 20, "italic"))
tituloLabel.grid(row=0, column=0, columnspan=5, padx=5, pady=5, sticky=N + S + E + W)

IniciarButton = Button(window, text="Play", bg='green', fg="white", command=resume)
IniciarButton.grid(row=1, column=0, padx=5, pady=5, sticky=N + S + E + W)

PararButton = Button(window, text="Pausa", bg='red', fg="white", command=stop)
PararButton.grid(row=1, column=1, padx=5, pady=5, sticky=N + S + E + W)

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

# Inserir gràfica a Tkinter
canvas = FigureCanvasTkAgg(fig, master=window)
canvas.get_tk_widget().grid(row=1, column=2, padx=10, pady=10, sticky=N+S+E+W)
canvas.draw()

# ───────────────────────────────────────────────
# FIL DE RECEPCIÓ DE DADES
# ───────────────────────────────────────────────
def recepcion():
    while running:
        if mySerial and mySerial.in_waiting > 0:
            linea = mySerial.readline().decode('utf-8').rstrip()
            data = linea.split(':') #Type list // data[x] = Type: str

            if len(data) == parametres: #Comprovació que rebem totes les dades
                contact.append(int(temps()))
                print("Humitat:", data[0])
                print("Temp:   ", data[1]) 
                #print(temps())
                histH.append(float(data[0]))
                histT.append(float(data[1])) 
            elif data == "FALLO":
                error()
                print("Error a la recepció de dades")
        time.sleep(0.1)

# ───────────────────────────────────────────────
# ACTUALITZACIÓ DE LA GRÀFICA DINS TKINTER
# ───────────────────────────────────────────────
def actualitzar_grafica():
    if contact:
        lineT.set_data(contact, histT)
        lineH.set_data(contact, histH)

        axT.set_xlim(max(0, contact[-1]-60), contact[-1]+5)
        axH.set_xlim(max(0, contact[-1]-60), contact[-1]+5)

        axT.relim()
        axT.autoscale_view(scaley=True)
        axH.relim()
        axH.autoscale_view(scaley=True)

        canvas.draw_idle()
    # tornar a cridar aquesta funció cada 500 ms
    window.after(500, actualitzar_grafica)

# ───────────────────────────────────────────────
# LLANÇAR FIL I INICIAR GUI
# ───────────────────────────────────────────────
threadRecepcion = threading.Thread(target=recepcion, daemon=True)
threadRecepcion.start()

# iniciar actualització periòdica
window.after(500, actualitzar_grafica)

def on_close():
    global running
    running = False
    if mySerial:
        mySerial.close()
    window.destroy()

window.protocol("WM_DELETE_WINDOW", on_close)
window.mainloop()
