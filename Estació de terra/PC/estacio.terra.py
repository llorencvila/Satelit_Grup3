from tkinter import *
from tkinter import messagebox
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
    device = 'COM11'
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
parametres = 4
Llista_Arguments_Ordres = ["stop", "seguir", "freq"]
llista_Arguments_Radar = ["vel", "lock", "moure", "escombreig"]
llista_Id_sys = ["temp", "hum", "radar", "alarmes", "escombreig", "all"]
noms_alarmes = ["Temperatura", "Humitat", "Distancia", "Perduda Conexió"]




data_lock = threading.Lock() #https://labex.io/es/tutorials/python-how-to-use-lock-in-python-s-threading-module-417460
                             #La funció lock serveix per evitar que hi hagi conflictes en la escriptura de variables entre els codis de dins i fora del thread


# ───────────────────────────────────────────────
# FUNCIONS AUXILIARS HUMITAT I TEMPERATURA
# ───────────────────────────────────────────────
print ("Funcionant")
def temps():
    return time.time() - t0

def stopHT(): #Aquesta funció ha migrat a Send_Ordres
    if Debug_RecepcioSimulada == False:
        mensaje = "STOP"
        mySerial.write(mensaje.encode('utf-8'))
    print("STOP")
    #mySerial.close

def resumeHT(): #Aquesta funció ha migrat a Send_Ordres
    if Debug_RecepcioSimulada == False:
        mensaje = "REANUDAR"
        mySerial.write(mensaje.encode('utf-8'))
    print("REANUDAR")

def Notificació_Alarma(arguments):
    messagebox.showwarning("Alarma", noms_alarmes(arguments)) 

def canvi_periodeHT(): ##Aquesta funció ha migrat a Send_Canvi_Frequencia
    periode_transmisio = "periode" +fraseHTEntry.get()
    mySerial.write(periode_transmisio)
    print ('Has canviat el periode de transimsio a --- ' + fraseHTEntry.get())

def Send_Ordres(Argument, info): 
    #Estrucutra del missatge 
    #  2;    Codi de Argument        ;  Codi_Informacio
    #Acció   Odrdre (Start/stop)     Id_sys (temp, hum...)
    if Debug_RecepcioSimulada == False:
        for i in len(Llista_Arguments_Ordres):  #Aquest pas no es extremadament nescesari, només està aqui pq sigui més facil de fer servir la funció per la persona que programa
            if Llista_Arguments_Ordres[i] == Argument:
                Codi_Argument = i

        if Codi_Argument == 0 or Codi_Argument == 1: # Si el argument == a Stop o Seguir
            for i in len(llista_Id_sys):
                if llista_Id_sys[i] == info:
                    Info_Missatge = i
        
        missatgefinal = ("2;"+str(Codi_Argument)+";"+str(Info_Missatge))
        mySerial.write(missatgefinal.encode('utf-8'))

def Send_Canvi_Frequencia(Id_Sys, ValorFreq):
    #Estrucutra del missatge 
    #  2;      2;    Id_sys;              Valor freq
    #Acció   Freq    Id_sys (temp, hum...)
    if Debug_RecepcioSimulada:
        for i in len(llista_Id_sys):
            if llista_Id_sys[i] == Id_Sys:
                Missatge_Id_Sys = i
        
        missatgefinal = ("2;2;"+str(Missatge_Id_Sys)+";"+str(abs(ValorFreq)))
        mySerial.write(missatgefinal.encode('utf-8'))

def Send_Radar(Argument, Valor1, Valor2):
    #                            Estrucutras del missatge 
    #  3;    Codi d'argument                           ;       Valor1        ;    Valor2  
    #Acció   Argument (vel/lock/Moure/escombreig)     Valor de velocitat        Angle
    #                                                    o de posició      (Només s'usa en el cas de lock)
    #                                                (depen de la acció)
    if Debug_RecepcioSimulada == False:
        trobat = 0
        i = 0
        while trobat == 0 and i < len(llista_Arguments_Radar):
            if llista_Arguments_Radar[i] == Argument:
                Codi_Argument = Argument
        
        if Codi_Argument == 0 or Codi_Argument == 2: #Canvi velocitat o bé moure a x lloc
            Valor1_Missatge = Valor1
            missatgefinal = ("3;"+str(Codi_Argument)+";"+str(Valor1_Missatge))

        if Codi_Argument == 1: # El cas de lock que nescesita dos valors 
            Valor2_Missatge = Valor2

            missatgefinal = ("3;"+str(Codi_Argument)+";"+str(Valor1_Missatge)+";"+str(Valor2_Missatge))

        if Codi_Argument == 3: #En cas que sigui escombreig
            missatgefinal = ("3;"+str(Codi_Argument))

        mySerial.write(missatgefinal.encode('utf-8'))
        
def Send_Mitjanes_Arduino(Argument, Valor1): #Aquesta funció serveix nomès pq les mitjanes les faci l'arduino. No serveix perque les mitjanes siguin fetes a la Ground Station
    #                            Estrucutra del missatge 
    #  4;    Codi d'argument                           ;       Valor1         
    #Acció   Id_sys     Valor de velocitat                Nº de valors que ha 
    #                                                     de tenir la mitjana     
    if Debug_RecepcioSimulada == False: 
        trobat = 0
        i = 0
        
        while trobat == 0 and i < len(llista_Id_sys):
            if llista_Id_sys[i] == Argument:
                Codi_Argument = Argument

        if Codi_Argument != 3 or Codi_Argument != 4: #Sempre que l'argument no sigui ni alarmes ni radar
            Valor_Missatge = abs(Valor1)
        else:
            return -1 #Error, els elements Alarmes i Escombreig no accepten mitjana
        
        missatgefinal = ("4;"+str(Codi_Argument)+";"+str(Valor_Missatge))
        mySerial.write(missatgefinal.encode('utf-8'))



# ───────────────────────────────────────────────
# FUNCIONS AUXILIARS DISTANCIA
# ───────────────────────────────────────────────

def stop_dist(): #Aquesta funció ha migrat a Send_Ordres
    if Debug_RecepcioSimulada == False:
        mensaje = "STOP"
        mySerial.write(mensaje.encode('utf-8'))
    print("STOP")
    #mySerial.close

def resume_dist(): #Aquesta funció ha migrat a Send_Ordres
    if Debug_RecepcioSimulada == False:
        mensaje = "REANUDAR"
        mySerial.write(mensaje.encode('utf-8'))
    print("REANUDAR")

def error_dist(): #Aquesta funció ha migrat a Notificacio_Alarma
    print("FALLO EN LA TRANSMISSIÓ DE DADES")

def canvi_periode_dist(): ##Aquesta funció ha migrat a Send_Canvi_Frequencia
    periode_transmisio = "periode" +frase_distEntry.get()
    mySerial.write(periode_transmisio)
    print ('Has canviat el periode de transimsio a --- ' + frase_distEntry.get())


    
# ───────────────────────────────────────────────
# FINESTRA PRINCIPAL TKINTER
# ───────────────────────────────────────────────
window = Tk()
window.geometry("10000x800")
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

IniciarHTButton = Button(button_HT_frame, text="Play", bg='#6BD66B', fg="white", command=resumeHT)
IniciarHTButton.grid(row=0, column=0, padx=5, pady=5, sticky=N + S + E + W)

PararHTButton = Button(button_HT_frame, text="Pausa", bg='#FFB74D', fg="white", command=stopHT)
PararHTButton.grid(row=0, column=1, padx=5, pady=5, sticky=N + S + E + W)

AplicarHTButton = Button(button_HT_frame, text="Aplicar", bg='#4DA3FF', fg="white", command=canvi_periodeHT)
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

Iniciar_distButton = Button(button_dist_frame, text="Play", bg='#A8E6A3', fg="white", command=resume_dist)
Iniciar_distButton.grid(row=0, column=0, padx=5, pady=5, sticky=N + S + E + W)

Parar_distButton = Button(button_dist_frame, text="Pausa", bg='#FFD59E', fg="white", command=stop_dist)
Parar_distButton.grid(row=0, column=1, padx=5, pady=5, sticky=N + S + E + W)

Aplicar_distButton = Button(button_dist_frame, text="Aplicar", bg='#A9D6F9', fg="white", command=canvi_periode_dist)
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

#Grafica HT
fig, (axT, axH) = plt.subplots(2, 1, figsize=(5, 3), sharex=True)
fig.subplots_adjust(hspace=0.4)
axT.set_title("Temperatura (°C)")
axH.set_title("Humitat (%)")

lineT, = axT.plot([], [], color='red')
lineH, = axH.plot([], [], color='blue')

axT.set_xlim(0, 60)
axT.set_ylim(0, 50)
axH.set_ylim(0, 100)


# Inserir gràfica HT a Tkinter 
canvas = FigureCanvasTkAgg(fig, master=grafHT_frame)
canvas.get_tk_widget().grid(row=0, column=0, padx=5, pady=5, sticky=N+S+E+W)
canvas.draw()


#Grafica Radar
figdist = plt.figure(figsize=(5,4))
axdist = figdist.add_subplot(111, projection='polar')
axdist.set_thetamin(0)
axdist.set_thetamax(180)
axdist.set_ylim(0, 110)   # ajustar segons el rang de distàncies esperat

# Línia que connectarà els punts del radar
lineRadar, = axdist.plot([], [], linewidth=1)

# Inserir gràfica del radar a Tkinter
canvasRadar = FigureCanvasTkAgg(figdist, master=graf_dist_frame)
canvasRadar.get_tk_widget().grid(row=0, column=0, sticky="nsew")
canvasRadar.draw()


# ───────────────────────────────────────────────
# FIL DE RECEPCIÓ DE DADES
# ───────────────────────────────────────────────
def recepcion():
    while True:
        if Debug_RecepcioSimulada == False :
            if mySerial and mySerial.in_waiting > 0:
                linea = mySerial.readline().decode('utf-8').rstrip()
                data_chunks = linea.split(';') #Type list // data[x] = Type: str
                accio = data_chunks[0]
                data = data_chunks[1].split(":")
                #OBSERVACIONS
                if accio == 0: 
                    if len(data) == parametres: #Comprovació que rebem totes les dades
                        contact.append(int(temps()))
                        print("Humitat:", data[0])
                        print("Temp:   ", data[1]) 
                        print("Pos:", (int (data[2])/4779)*360)
                        print("Dist:   ", data[3]) 
                        #print(temps())
                        histH.append(float(data[0]))
                        histT.append(float(data[1]))
                        histAng.append(float(data[2]))
                        histDist.append(float(data[3]))

                        print (histH)
                #ALARMES
                elif accio == 1:
                    Notificació_Alarma(data)
                    
        else: 
            with data_lock: #No acabo d'entendre perque fem servir el thread.lock() si la variable que accedim no es compartida ni s'edita enlloc més
                histH.append(float("%.2f" % random.uniform(0,100)))
                histT.append(float("%.2f" % random.uniform(10,25)))
                histAng.append(float("%.2f" % random.uniform(0,180)))
                histDist.append(float("%.2f" % random.uniform(0,100)))
                contact.append(int(temps()))
                #print(histH)
                #print(contact)
                threading.Event().wait(0.5)
        
        #actualitzar_grafica()
        #plt.pause(0.5)

# ───────────────────────────────────────────────
# ACTUALITZACIÓ DE LA GRÀFICA DINS TKINTER 
# ───────────────────────────────────────────────
#FUNCIÓ PER ACTUALITZAR LA GRÀFICA DE TEMPERATURA I HUMITAT
def actualitzar_graficaHT():
    try: 
        if contact: #No acabo d'entendre pq es fa servir if contact
            lineT.set_data(contact, histT)
            lineH.set_data(contact, histH)
            #print("Grafica actuaitzant-se")
            axT.set_xlim(max(0, contact[-1]-60), contact[-1]+5)
            axH.set_xlim(max(0, contact[-1]-60), contact[-1]+5)

            axT.relim()
            axT.autoscale_view(scaley=True)
            axH.relim()
            axH.autoscale_view(scaley=True)

            canvas.draw_idle()

        window.after(500, actualitzar_graficaHT)
    
    except Exception as e:
        print("ERROR a actualitzar_graficaHT:", e)




#FUNCIÓ PER ACTUALITZAR LA GRÀFICA DEL RADAR
def actualitzar_grafica_radar():
    try:
        if (len(histAng)!=0 and len(histDist)!=0):
            # agafar últims N valors
            N = 10
            angs = histAng[-N:]
            r = histDist[-N:]

            # convertir a radians
            theta = np.radians(angs)

            # Actualitzar la línia que uneix punts
            lineRadar.set_data(theta, r)

            # Esborrar i tornar a dibuixar només el scatter actual
            # eliminar collections (punts antics)
            for c in list(axdist.collections):
                c.remove()

         # Eliminar totes les línies existents menys la del radar
            for line in list(axdist.lines):
                if line is not lineRadar:
                    axdist.lines.remove(line)
        
            if lineRadar not in axdist.lines:
                axdist.add_line(lineRadar)

            axdist.scatter(theta, r, s=40, color="blue")


            # Ajustar escala radial (dinàmic o fixa)
            axdist.set_ylim(0, max(1, max(r)) + 10)

            canvasRadar.draw_idle()

        window.after(200, actualitzar_grafica_radar)

    except Exception as e:
        print("ERROR a actualitzar_grafica_radar:", e)




# ───────────────────────────────────────────────
# LLANÇAR FIL I INICIAR GUI
# ───────────────────────────────────────────────
 
threadRecepcion = threading.Thread(target=recepcion, daemon=True)
threadRecepcion.start()


# iniciar actualització periòdica
window.after(50, actualitzar_graficaHT)

window.after(200, actualitzar_grafica_radar)


def on_close():
    global running
    running = False
    if Debug_RecepcioSimulada == False:
        if mySerial:
            mySerial.close()
    window.destroy()

window.protocol("WM_DELETE_WINDOW", on_close)
window.mainloop()
