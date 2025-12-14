from tkinter import *
from tkinter import messagebox
import matplotlib.pyplot as plt
import numpy as np
import serial
import time
import threading
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random
import sys
import re
import matplotlib
import csv
import os
from datetime import datetime
from tkinter import ttk
import tkinter as tk

Debug_RecepcioSimulada = False #En cas de ser True s'inventarà les dades de recepció ignorant completament el port sèrie. 
                              #És d'utilitat per fer proves amb el codi si no es disposa del maquinari físic (els dos arduinos)

# ───────────────────────────────────────────────
# CONFIGURACIÓ DEL PORT SÈRIE 
# ───────────────────────────────────────────────
if Debug_RecepcioSimulada == False:
    device = 'COM5'
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
histmitjT = []
histmitjH = []
histTemps = []
histCoordx = []
histCoordy = []
histCoordz = []


contact = []
parametres = 4
Llista_Arguments_Ordres = ["stop", "seguir", "freq"]
llista_Arguments_Radar = ["vel", "lock", "moure", "escombreig"]
llista_Id_sys = ["temp", "hum", "radar", "alarmes", "all"]
noms_alarmes = ["Temperatura", "Humitat", "Distancia", "Perduda Conexió", "Error de sintaxi"]


R_EARTH = 6371000  # radi de la Terra en metres

#variables per l'alarma de la mitjana de temperatura i humitat

consec_Tmax = 0
consec_Hmax = 0
Tmax_val = None
Hmax_val = None
mySerialOrbit = None

stopCalc = False

# -------- Esdeveniments (log) -----------
EVENTS_FILE = "events_log.csv"   # ruta del fitxer on es guarden els events
EVENT_TYPES = ["Comanda", "Alarma", "Observació"]  # els tres tipus que demanes

events = []   # llista de dicts: {"datetime": datetime obj, "tipo": str, "desc": str}
events_lock = threading.Lock()  # per sincronitzar accés a events
# ----------------------------------------


data_lock = threading.Lock() #https://labex.io/es/tutorials/python-how-to-use-lock-in-python-s-threading-module-417460
                             #La funció lock serveix per evitar que hi hagi conflictes en la escriptura de variables entre els codis de dins i fora del thread


# ───────────────────────────────────────────────
# FUNCIONS TEMPS I ALARMES
# ───────────────────────────────────────────────
print ("Funcionant")
def temps():
    return time.time() - t0

def Notificació_Alarma(arguments):
    if arguments < len(noms_alarmes):
        alarma_text = noms_alarmes[arguments]

        print("alarma:", alarma_text)
        add_event("Alarma", f"Codi {arguments}: {alarma_text}")

        # Important: cridar el Tkinter Toplevel des del MAIN THREAD
        window.after(0, lambda: messagebox_no_modal("Alarma", alarma_text))

def validar_numero(entry_widget):
    try:
        return float(entry_widget.get())
    except ValueError:
        # Activa alarma “Error de sintaxi” (codi 4)
        Notificació_Alarma(4)
        add_event("Alarma", "Error de sintaxi: valor no numèric")
        return None

# ─────────────────────────────────────────────────────
# FUNCIÓ MESSAGEBOX QUE NO CONGELI TOT EL PROGRAMA
# ─────────────────────────────────────────────────────

def messagebox_no_modal(titol, text):
    win = tk.Toplevel()
    win.title(titol)
    win.geometry("350x150")
    win.resizable(False, False)
    win.attributes("-topmost", True)

    # Centra la finestra
    win.update_idletasks()
    x = (win.winfo_screenwidth() - win.winfo_width()) // 2
    y = (win.winfo_screenheight() - win.winfo_height()) // 3
    win.geometry(f"+{x}+{y}")

    tk.Label (win, text=text, wraplength=300, justify="left", font = ("Helvetica",12,"bold"), fg="red").pack(pady=15)
    tk.Button(
        win,
        text="OK",
        command=win.destroy,
        font=("Helvetica", 14, "bold"),  # font més gran
        fg="white",
        bg="red",
        width=10,  # amplada del botó en caràcters
        height=2   # alçada del botó en línies
    ).pack(pady=10)


# ───────────────────────────────────────────────
# FUNCIONS PER ENVIAR DADES
# ───────────────────────────────────────────────

def stopHT(): 
    Send_Ordres("stop","temp")
    Send_Ordres("stop", "hum")
    print("STOP")
    #mySerial.close

def resumeHT():
    Send_Ordres("seguir","temp")
    Send_Ordres("seguir", "hum")
    print("REANUDAR")

def canvi_periodeHT():
    Send_Canvi_Frequencia("temp", fraseHTEntry.get())
    Send_Canvi_Frequencia("hum", fraseHTEntry.get())
    add_event("Comanda", f"Canvi període HT a {fraseHTEntry.get()}")     #registre d'events
    validar_numero(fraseHTEntry)       #alarma sino s'ha entroduint un valor correcte

def Tmax():
    global Tmax_val
    try:
        Tmax_val = float(fraseHTEntry_Tmax.get())
        print('La temperatura màxima és:' + fraseHTEntry_Tmax.get())
    except ValueError:
        print("Error: no has introduït un número.")
    add_event("Comanda", f"Tmax configurat a {fraseHTEntry_Tmax.get()}")     #registre d'events
    validar_numero(fraseHTEntry_Tmax)       #alarma sino s'ha entroduint un valor correcte

def Hmax():
    global Hmax_val
    try:
        Hmax_val = float(fraseHTEntry_Hmax.get())
        print('La humitat màxima és:' + fraseHTEntry_Hmax.get())
    except ValueError:
        print("Error: no has introduït un número.")
    add_event("Comanda", f"Hmax configurat a {fraseHTEntry_Hmax.get()}")     #registre d'events
    validar_numero(fraseHTEntry_Hmax)       #alarma sino s'ha entroduint un valor correcte


def activar_mitjanes_EstTerra():
    global stopCalc
    stopCalc = False
    mitjanes_EstTerra()
    add_event("Comanda", "Mitjanes Estació de terra")     #registre d'events


def mitjanes_EstTerra(): #NOMÉS ES CALCULEN LES MITJANES QUAN ES CTRIDA LA FUNCIÓ A TRAVÉS DE LA FUNCIÓ ANTERIOR, SÓN LES MITJANES CALCULADES PER L'ESTACIÓ DE TERRA 
    global thread_mitjanaT, thread_mitjanaH

    if stopCalc == False:
        try:
            thread_mitjanaT, mitjana_labelT = start_mitjanaT_label(
                histT,
                data_lock,
                parent_widget=button_HT_frame,
                interval=0.5,
                row=4,
                column=0
                )
            thread_mitjanaH, mitjana_labelH = start_mitjanaH_label(
                histH,
                data_lock,
                parent_widget=button_HT_frame,
                interval=0.5,
                row=5,
                column=0
            )
        except Exception as e:
            print("Error iniciant els fils de mitjana:", e)
    
    else:    
        return

    
    
#Realment, les funcions seguents es podrien ajuntar en una de sola, de moment s'ha optat per deixar-ho aixi perque pot resultar més entenedor. En un futur es poden ajuntar.

def Send_Ordres(Argument, info):
    #Estrucutra del missatge 
    #  2;    Codi de Argument        ;  Codi_Informacio
    #Acció   Odrdre (Start/stop)     Id_sys (temp, hum...)
    if Debug_RecepcioSimulada == False:
        trobat = 0
        i = 0
        while i < len(Llista_Arguments_Ordres) and trobat == 0:  #Aquest pas no es extremadament nescesari, només està aqui pq sigui més facil de fer servir la funció per la persona que programa
            if Llista_Arguments_Ordres[i] == Argument:
                trobat = 1
                Codi_Argument = i
            else:
                i = i+1

        if trobat == 0:
            Notificació_Alarma(4)
            return
        
        if Codi_Argument == 0 or Codi_Argument == 1: # Si el argument == a Stop o Seguir
            trobat = 0
            i = 0
            while i < len(llista_Id_sys) and trobat == 0:
                if llista_Id_sys[i] == info:
                    trobat = 1
                    Info_Missatge = i
                else:
                    i=i+1
        
        missatgefinal = ("2;"+str(Codi_Argument)+";"+str(Info_Missatge)+";")

        print(missatgefinal)

        missatgefinal = (missatgefinal + str(Generar_Checksum(missatgefinal)))
        mySerial.write(missatgefinal.encode('utf-8'))
        mySerial.write("\n".encode('utf-8'))
            # Després d'enviar pel serial (o en mode debug), afegim l'event:
    try:
        add_event("Comanda", f"Enviada ordre: {Argument} -> {info}")
    except Exception:
        pass


def Send_Canvi_Frequencia(Id_Sys, ValorFreq):
    #Estrucutra del missatge 
    #  2;      2;    Id_sys;              Valor freq
    #Acció   Freq    Id_sys (temp, hum...)
    if Debug_RecepcioSimulada == False:
        print("Send_Canvi_frequencia")
        trobat = 0
        i = 0
        while i < len(llista_Id_sys) and trobat == 0:
            if llista_Id_sys[i] == Id_Sys:
                trobat = 1  
                Missatge_Id_Sys = i
            else:
                i=i+1
        
        missatgefinal = ("2;2;"+str(Missatge_Id_Sys)+";"+str(abs(ValorFreq))+";")   
        missatgefinal = (missatgefinal + str(Generar_Checksum(missatgefinal)))

        mySerial.write(missatgefinal.encode('utf-8'))

def Send_Radar(Argument, Valor1, Valor2):
    #                            Estrucutras del missatge 
    #  3;    Codi d'argument                           ;       Valor1        ;    Valor2  
    #Acció   Argument (vel/lock/Moure/escombreig)     Valor de velocitat        Angle
    #                                                    o de posició      (Només s'usa en el cas de lock)
    #                                                (depen de la acció)
    if Debug_RecepcioSimulada == False:
        print("sendRadar")
        trobat = 0
        i = 0
        while trobat == 0 and i < len(llista_Arguments_Radar):
            if llista_Arguments_Radar[i] == Argument:
                Codi_Argument = Argument
            else:
                i = i+1

        
        if Codi_Argument == 0 or Codi_Argument == 2: #Canvi velocitat o bé moure a x lloc
            Valor1_Missatge = Valor1
            missatgefinal = ("3;"+str(Codi_Argument)+";"+str(Valor1_Missatge)+";")

        if Codi_Argument == 1: # El cas de lock que nescesita dos valors 
            Valor2_Missatge = Valor2

            missatgefinal = ("3;"+str(Codi_Argument)+";"+str(Valor1_Missatge)+";"+str(Valor2_Missatge)+";")

        if Codi_Argument == 3: #En cas que sigui escombreig
            missatgefinal = ("3;"+str(Codi_Argument)+";")

        missatgefinal = (missatgefinal + str(Generar_Checksum(missatgefinal)))
        
        mySerial.write(missatgefinal.encode('utf-8'))
        mySerial.write("\n".encode('utf-8'))


def Send_Mitjanes_Arduino(Argument, Valor1): #Aquesta funció serveix nomès pq les mitjanes les faci l'arduino. No serveix perque les mitjanes siguin fetes a la Ground Station
    #                            Estrucutra del missatge 
    #  4;    Codi d'argument        ;       Valor1         
    #Acció   Id_sys                Nº de valors que ha 
    #                              de tenir la mitjana  
  
    if Debug_RecepcioSimulada == False: 
        trobat = 0
        i = 0
        
        while trobat == 0 and i < len(llista_Id_sys):
            if llista_Id_sys[i] == Argument:
                Codi_Argument = i
                trobat=1
            else:
                i = i+1

        if Codi_Argument != 3 or Codi_Argument != 4: #Sempre que l'argument no sigui ni alarmes ni radar
            Valor_Missatge = abs(Valor1)
        else:
            return -1 #Error, els elements Alarmes i Escombreig no accepten mitjana
        
        missatgefinal = ("4;"+"0;"+str(Codi_Argument)+";"+str(Valor_Missatge)+";")
        missatgefinal = (missatgefinal + str(Generar_Checksum(missatgefinal)))
        print("ENVIEM DADES_________________________________")
        mySerial.write(missatgefinal.encode('utf-8'))
        mySerial.write("\n".encode('utf-8'))

def Generar_Checksum(missatge):
    checksum = 59 #Començem amb 59 pq és el codi ascii del ";", el qual s'elimina per la funció rsplit
    for i in range(len(missatge)):
        checksum = checksum + ord(missatge[i]) #La funció ord() retorna el valor ASCII de l'element

    return checksum

def MitjanesArduinoTkinterFriendly():
    print("mitjana arduino")
    Send_Mitjanes_Arduino("temp",0)
    Send_Mitjanes_Arduino("hum",0)
    add_event("Comanda", "Mitjanes Satèl·lit")     #registre d'events


# ───────────────────────────────────────────────
# FUNCIONS AUXILIARS DISTANCIA
# ───────────────────────────────────────────────

def radar_play():
    Send_Ordres("seguir", "radar")
    #add_event("Comanda", "Radar PLAY")

def radar_stop():
    Send_Ordres("stop", "radar")
    #add_event("Comanda", "Radar STOP")

def canvi_periodedist():
    Send_Canvi_Frequencia("dist", frase_distEntry.get())
    add_event("Comanda", f"Canvi període distància a {frase_distEntry.get()}")     #registre d'events
    validar_numero(frase_distEntry)       #alarma sino s'ha entroduint un valor correcte

'''''''''
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
'''''''''

# ───────────────────────────────────────────────
# FUNCIONS REGISTRE D'EVENTS
# ───────────────────────────────────────────────
def _format_dt(dt):
    # Format llegible per a l'usuari i per a guardar
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def _parse_dt(s):
    try:
        return datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
    except Exception:
        return None

def load_events_from_file():
    #Carrega events des del CSV a la llista events.
    global events
    if not os.path.exists(EVENTS_FILE):
        return
    with events_lock:
        with open(EVENTS_FILE, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            events = []
            for row in reader:
                dt = _parse_dt(row.get("datetime", ""))
                tipo = row.get("type", "")
                desc = row.get("description", "")
                if dt:
                    events.append({"datetime": dt, "type": tipo, "description": desc})

def save_event_to_file(event):
    """Afegeix un event (dict) al fitxer CSV (append)."""
    header_needed = not os.path.exists(EVENTS_FILE)
    with open(EVENTS_FILE, "a", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if header_needed:
            writer.writerow(["datetime", "type", "description"])
        writer.writerow([_format_dt(event["datetime"]), event["type"], event["description"]])

def save_all_events_to_file():
    """Escriu tots els events a l'arxiu (sobreescriu)."""
    with events_lock:
        with open(EVENTS_FILE, "w", newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["datetime", "type", "description"])
            for e in events:
                writer.writerow([_format_dt(e["datetime"]), e["type"], e["description"]])

def add_event(tipo, description, dt=None, persist=True):
    """
    Afegeix un event a la memòria (i opcionalment a fitxer).
    - tipo: una de EVENT_TYPES
    - description: text
    - dt: datetime object (si None, s'usa ara)
    - persist: si True, escriu al fitxer immediatament
    """

    # --- Filtre: ignora els dos primers esdeveniments ---
    #if len(events) < 2:
        #return
    # ----------------------------------------------------

    if tipo not in EVENT_TYPES:
        tipo = "Observació"  # fallback
    if dt is None:
        dt = datetime.now()

    ev = {"datetime": dt, "type": tipo, "description": description}

    with events_lock:
        events.append(ev)

    if persist:
        try:
            save_event_to_file(ev)
        except Exception as e:
            print("Error desant event:", e)

    # Actualitza la vista si existeix
    try:
        if 'events_treeview' in globals():
            refresh_events_treeview()
    except Exception:
        pass

    #Scroll automàtic al afegir un event
    try:
        if 'events_treeview' in globals():
            refresh_events_treeview()

            # --- Desplaçar scroll a l'última fila ---
            children = events_treeview.get_children()
            if children:
                events_treeview.see(children[-1])
    except Exception:
        pass



    
# ───────────────────────────────────────────────
# FINESTRA PRINCIPAL TKINTER
# ───────────────────────────────────────────────
window = Tk()
window.geometry("1100x710")
window.title("Control de transmissió de dades")

window.columnconfigure(0, weight=1, uniform="col")
window.columnconfigure(1, weight=1, uniform="col")
window.columnconfigure(2, weight=1, uniform="col")
window.rowconfigure(0, weight=3, uniform="row")
window.rowconfigure(1, weight=1, uniform="row")
window.rowconfigure(2, weight=1, uniform="row")
window.rowconfigure(3, weight=1, uniform="row")
window.rowconfigure(4, weight=1)


#tituloLabel = Label(window, text="Transmissió de dades", font=("Courier", 20, "italic"))
#tituloLabel.grid(row=0, column=0, columnspan=5, padx=5, pady=5, sticky=N + S + E + W)

#─────────────────FRAME CONTROLADOR TEMPERATURA I HUMITAT:─────────────────
button_HT_frame = LabelFrame(window, text = 'Humitat i Temperatura', font=("Arial", 15))
button_HT_frame.grid(row=0, column=0, padx=5, pady=5, sticky=N + S + E + W)

button_HT_frame.rowconfigure(0, weight=1)
button_HT_frame.rowconfigure(1, weight=1)
button_HT_frame.rowconfigure(2, weight=1)
button_HT_frame.rowconfigure(3, weight=1)
button_HT_frame.rowconfigure(4, weight=1)
button_HT_frame.rowconfigure(5, weight=1)
button_HT_frame.rowconfigure(6, weight=1)

button_HT_frame.columnconfigure(0, weight=1)
button_HT_frame.columnconfigure(1, weight=1)

IniciarHTButton = Button(button_HT_frame, text="Play", bg='#6BD66B', fg="white", font=("Arial", 15), command=resumeHT)
IniciarHTButton.grid(row=0, column=0, padx=5, pady=5, sticky=N + S + E + W)

PararHTButton = Button(button_HT_frame, text="Pausa", bg='#FFB74D', fg="white", font=("Arial", 15), command=stopHT)
PararHTButton.grid(row=0, column=1, padx=5, pady=5, sticky=N + S + E + W)

#grafiquesButton = Button(button_HT_frame, text="grafiques", bg='#6BD66B', fg="white", font=("Arial", 15), command=switch_orbit)
#grafiquesButton.grid(row=0, column=3, padx=5, pady=5, sticky=N + S + E + W)

CalculArduinoButton = Button(button_HT_frame, text="Calcula la mitjana al satèl·lit", bg="#FF4D6B", fg="white", font=("Arial", 15), command=MitjanesArduinoTkinterFriendly)
CalculArduinoButton.grid(row=6, column=0, padx=10, pady=5, sticky=N + S + E + W)

CalculEstTerraButton = Button(button_HT_frame, text="Calcula la mitjana a l'estació de terra", bg='#FF4D6B', fg="white", font=("Arial", 15), command=activar_mitjanes_EstTerra)
CalculEstTerraButton.grid(row=6, column=1, padx=10, pady=5, sticky=N + S + E + W)

label_mitjanaT_arduino = Label(button_HT_frame, text="Mitjana T Arduino: --", font=("Arial", 14))
label_mitjanaT_arduino.grid(row=4, column=1, padx=5, pady=5, sticky=W)

label_mitjanaH_arduino = Label(button_HT_frame, text="Mitjana H Arduino: --", font=("Arial", 14))
label_mitjanaH_arduino.grid(row=5, column=1, padx=5, pady=5, sticky=W)

label_mitjanaT_ET = Label(button_HT_frame, text="Mitjana T ET: --", font=("Arial", 14))
label_mitjanaT_ET.grid(row=4, column=0, padx=5, pady=5, sticky=W)

label_mitjanaH_ET = Label(button_HT_frame, text="Mitjana H ET: --", font=("Arial", 14))
label_mitjanaH_ET.grid(row=5, column=0, padx=5, pady=5, sticky=W)

periode_HT_frame = LabelFrame(button_HT_frame, text = 'Modificar el periode de transmissió', font=("Arial", 10))
periode_HT_frame.grid(row=1, column=0, columnspan = 2, padx=5, pady=5, sticky=N + S + E + W)

periode_HT_frame.rowconfigure(0, weight=1)
periode_HT_frame.columnconfigure(0, weight=1)
periode_HT_frame.columnconfigure(1, weight=1)

AplicarHTButton = Button(periode_HT_frame, text="Aplicar", bg='#4DA3FF', fg="white", font=("Arial", 15), command=canvi_periodeHT)
AplicarHTButton.grid(row=0, column=1, padx=5, pady=5, sticky=N + S + E + W)

fraseHTEntry = Entry(periode_HT_frame, font=("Arial", 15))
fraseHTEntry.grid(row=0, column=0, columnspan = 1, padx=5, pady=5, sticky=N + S + E + W)

#----------------FRAME TEMPERATURA MÀXIMA----------------
Tmax_HT_frame = LabelFrame(button_HT_frame, text = 'Temperatura màxima', font=("Arial", 10))
Tmax_HT_frame.grid(row=2, column=0, columnspan = 2, padx=5, pady=5, sticky=N + S + E + W)

Tmax_HT_frame.rowconfigure(0, weight=1)
Tmax_HT_frame.columnconfigure(0, weight=1)
Tmax_HT_frame.columnconfigure(1, weight=1)

AplicarHTButton_Tmax = Button(Tmax_HT_frame, text="Aplicar", bg='#4DA3FF', fg="white", font=("Arial", 15), command=Tmax)
AplicarHTButton_Tmax.grid(row=0, column=1, padx=5, pady=5, sticky=N + S + E + W)

fraseHTEntry_Tmax = Entry(Tmax_HT_frame, font=("Arial", 15))
fraseHTEntry_Tmax.grid(row=0, column=0, columnspan = 1, padx=5, pady=5, sticky=N + S + E + W)

#----------------FRAME HUMITAT MÀXIMA----------------
Hmax_HT_frame = LabelFrame(button_HT_frame, text = 'Humitat màxima', font=("Arial", 10))
Hmax_HT_frame.grid(row=3, column=0, columnspan = 2, padx=5, pady=5, sticky=N + S + E + W)

Hmax_HT_frame.rowconfigure(0, weight=1)
Hmax_HT_frame.columnconfigure(0, weight=1)
Hmax_HT_frame.columnconfigure(1, weight=1)

AplicarHTButton_Hmax = Button(Hmax_HT_frame, text="Aplicar", bg='#4DA3FF', fg="white", font=("Arial", 15), command=Hmax)
AplicarHTButton_Hmax.grid(row=0, column=1, padx=5, pady=5, sticky=N + S + E + W)

fraseHTEntry_Hmax = Entry(Hmax_HT_frame, font=("Arial", 15))
fraseHTEntry_Hmax.grid(row=0, column=0, columnspan = 1, padx=5, pady=5, sticky=N + S + E + W)


#─────────────────FRAME CONTROLADOR DADES DE DISTÀNCIA─────────────────
button_dist_frame = LabelFrame(window, text = 'Sensor de distància', font=("Arial", 15))
button_dist_frame.grid(row=1, column=0, padx=5, pady=5, sticky=N + S + E + W)

button_dist_frame.rowconfigure(0, weight=1)
button_dist_frame.rowconfigure(1, weight=1)
button_dist_frame.columnconfigure(0, weight=1)
button_dist_frame.columnconfigure(1, weight=1)

Iniciar_distButton = Button(button_dist_frame, text="Play", bg='#6BD66B', fg="white", font=("Arial", 15), command=radar_play)
Iniciar_distButton.grid(row=0, column=0, padx=5, pady=5, sticky=N + S + E + W)

Parar_distButton = Button(button_dist_frame, text="Pausa", bg='#FFB74D', fg="white", font=("Arial", 15), command=radar_stop)
Parar_distButton.grid(row=0, column=1, padx=5, pady=5, sticky=N + S + E + W)

#----------------FRAME CONTROLADOR DE PERIODE DISTÀNCIA----------------
periode_dist_frame = LabelFrame(button_dist_frame, text = 'Modificar el periode de transmissió', font=("Arial", 10))
periode_dist_frame.grid(row=1, column=0, columnspan = 2, padx=5, pady=5, sticky=N + S + E + W)

periode_dist_frame.rowconfigure(0, weight=1)
periode_dist_frame.columnconfigure(0, weight=1)
periode_dist_frame.columnconfigure(1, weight=1)

Aplicar_distButton = Button(periode_dist_frame, text="Aplicar", bg='#4DA3FF', fg="white", font=("Arial", 15), command=canvi_periodedist)
Aplicar_distButton.grid(row=0, column=1, padx=5, pady=5, sticky=N + S + E + W)

frase_distEntry = Entry(periode_dist_frame, font=("Arial", 15))
frase_distEntry.grid(row=0, column=0, columnspan = 1, padx=5, pady=5, sticky=N + S + E + W)

#─────────────────FRAME GRÀFICA HT─────────────────
grafHT_frame = LabelFrame(window, text = 'Gràfica temperatura i humitat', font=("Arial", 15))
grafHT_frame.grid(row=0, column=1, rowspan = 4, padx=5, pady=5, sticky=N + S + E + W)

grafHT_frame.rowconfigure(0, weight=1)
grafHT_frame.columnconfigure(0, weight=1)

#─────────────────FRAME GRÀFICA DISTÀNCIA─────────────────
graf_dist_frame = LabelFrame(window, text = 'Gràfica sensor de distància', font=("Arial", 15))
graf_dist_frame.grid(row=0, column=2, rowspan = 2, padx=5, pady=5, sticky=N + S + E + W)

graf_dist_frame.rowconfigure(0, weight=1)
graf_dist_frame.columnconfigure(0, weight=1)

#─────────────────FRAME SIMULADOR D'ÒRBITA─────────────────
graf_orbita_frame = LabelFrame(window, text='Òrbita satèl·lit', font=("Arial", 15))
graf_orbita_frame.grid(row=2, column=2, rowspan = 2, padx=5, pady=5, sticky=N + S + E + W)

graf_orbita_frame.rowconfigure(0, weight=1)
graf_orbita_frame.columnconfigure(0, weight=1)

# Figura òrbita
fig_orbita, ax_orbita = plt.subplots(figsize=(5, 4))

orbit_plot, = ax_orbita.plot([], [], 'bo-', markersize=2, label='Òrbita')
last_point_plot = ax_orbita.scatter([], [], color='red', s=50, label='Últim punt')

# Cercle Terra (vista pol nord)
earth_circle = plt.Circle((0, 0), R_EARTH, color='orange', fill=False, label='Terra')
ax_orbita.add_artist(earth_circle)

ax_orbita.set_xlim(-7e6, 7e6)
ax_orbita.set_ylim(-7e6, 7e6)

ax_orbita.set_aspect('equal', 'box')
ax_orbita.set_xlabel('X (m)')
ax_orbita.set_ylabel('Y (m)')
ax_orbita.set_title('Òrbita equatorial (vista pol nord)')
ax_orbita.grid(True)
ax_orbita.legend()

canvas_orbita = FigureCanvasTkAgg(fig_orbita, master=graf_orbita_frame)
canvas_orbita.get_tk_widget().grid(row=0, column=0, padx=5, pady=5, sticky=N+S+E+W)
canvas_orbita.draw()

#─────────────────FRAME D'ESDEVENIMENTS / LOG─────────────────
events_frame = LabelFrame(window, text='Registre d\'esdeveniments', font=("Arial", 15))
events_frame.grid(row=2, rowspan=2, column=0, padx=5, pady=5, sticky=N+S+E+W)

events_frame.rowconfigure(0, weight=0)
events_frame.rowconfigure(1, weight=0)
events_frame.rowconfigure(2, weight=1)
events_frame.columnconfigure(0, weight=1)
events_frame.columnconfigure(1, weight=1)
events_frame.columnconfigure(2, weight=1)

# 1) Entrada observacions usuari
obs_label = Label(events_frame, text="Nova observació:", font=("Arial", 12))
obs_label.grid(row=0, column=0, padx=5, pady=3, sticky="w")

obs_entry = Entry(events_frame, font=("Arial", 12))
obs_entry.grid(row=0, column=1, padx=5, pady=3, sticky="we")

def on_add_observation():
    text = obs_entry.get().strip()
    if not text:
        messagebox.showinfo("Info", "Introdueix una observació abans d'afegir.")
        return
    add_event("Observació", text)
    obs_entry.delete(0, END)
    #messagebox.showinfo("OK", "Observació afegida i guardada.")

add_obs_btn = Button(events_frame, text="Afegeix observació", command=on_add_observation, bg="#4DA3FF", fg="white", font=("Arial", 12))
add_obs_btn.grid(row=0, column=2, padx=5, pady=3, sticky="e")

# 2) Filtres: tipus i rang de dates
filter_type_label = Label(events_frame, text="Filtrar per tipus:", font=("Arial", 10))
filter_type_label.grid(row=1, column=0, padx=5, pady=3, sticky="w")
filter_type_cb = ttk.Combobox(events_frame, values=["Tots"] + EVENT_TYPES, state="readonly")
filter_type_cb.set("Tots")
filter_type_cb.grid(row=1, column=1, padx=5, pady=3, sticky="we")

#filter_from_label = Label(events_frame, text="Des (YYYY-MM-DD HH:MM:SS):", font=("Arial", 10))
#filter_from_label.grid(row=1, column=2, padx=5, pady=3, sticky="w")
#filter_from_entry = Entry(events_frame, font=("Arial", 10))
#filter_from_entry.grid(row=1, column=2, padx=5, pady=3, sticky="e")  # ajusta si cal

#filter_to_label = Label(events_frame, text="Fins (YYYY-MM-DD HH:MM:SS):", font=("Arial", 10))
#filter_to_label.grid(row=1, column=2, padx=5, pady=3, sticky="w")

# Per simplificar la disposició, fem dues entrades petites a sota:
filter_from_entry = Entry(events_frame, font=("Arial", 10))
#filter_from_entry.grid(row=1, column=1, padx=5, pady=3, sticky="w")
filter_to_entry = Entry(events_frame, font=("Arial", 10))
#filter_to_entry.grid(row=1, column=2, padx=5, pady=3, sticky="w")

# 3) Treeview per mostrar events
cols = ("datetime", "type", "description")
events_treeview = ttk.Treeview(events_frame, columns=cols, show="headings", height=8)
events_treeview.heading("datetime", text="Data i hora")
events_treeview.heading("type", text="Tipus")
events_treeview.heading("description", text="Descripció")
events_treeview.column("datetime", width=150)
events_treeview.column("type", width=80)
events_treeview.column("description", width=500)
events_treeview.grid(row=2, column=0, columnspan=3, sticky=N+S+E+W, padx=5, pady=5)

# scrollbar
sv = ttk.Scrollbar(events_frame, orient="vertical", command=events_treeview.yview)
events_treeview.configure(yscrollcommand=sv.set)
sv.grid(row=2, column=3, sticky='ns', padx=0, pady=5)

def refresh_events_treeview():
    """Omple el treeview amb els events filtrats segons els controls."""
    # Llegim filtres
    ftype = filter_type_cb.get()
    ffrom = filter_from_entry.get().strip()
    fto = filter_to_entry.get().strip()

    dt_from = _parse_dt(ffrom) if ffrom else None
    dt_to = _parse_dt(fto) if fto else None

    # netejar treeview
    for i in events_treeview.get_children():
        events_treeview.delete(i)

    with events_lock:
        for e in events:
            if ftype != "Tots" and ftype and e["type"] != ftype:
                continue
            if dt_from and e["datetime"] < dt_from:
                continue
            if dt_to and e["datetime"] > dt_to:
                continue
            events_treeview.insert("", "end",
                                   values=(_format_dt(e["datetime"]), e["type"], e["description"]))

# Botons d'actualitzar i esborrar filtres
def on_apply_filter():
    try:
        refresh_events_treeview()
    except Exception as ex:
        print("Error filtrant events:", ex)

def on_clear_filters():
    filter_type_cb.set("Tots")
    filter_from_entry.delete(0, END)
    filter_to_entry.delete(0, END)
    refresh_events_treeview()

apply_filter_btn = Button(events_frame, text="Aplica filtre", command=on_apply_filter)
apply_filter_btn.grid(row=3, column=1, sticky="e", padx=5, pady=3)
clear_filter_btn = Button(events_frame, text="Neteja filtres", command=on_clear_filters)
clear_filter_btn.grid(row=3, column=2, sticky="w", padx=5, pady=3)

# Carregar events guardats i pintar-los
load_events_from_file()
refresh_events_treeview()

'''''''''''
#Detectar qualsevol click
def log_ui_click(event):
    widget = event.widget
    name = str(widget)
    add_event("Comanda", f"Click a {name}")

window.bind_all("<Button-1>", log_ui_click)
'''''''''

# ────────────────── FRAME MANUAL D’ORDRES ──────────────────
manual_cmd_frame = LabelFrame(window, text='Enviar comanda manual', font=("Arial", 15))
manual_cmd_frame.grid(row=6, column=0, columnspan = 3, padx=5, pady=5, sticky=N+S+E+W)

manual_cmd_frame.columnconfigure(0, weight=1, uniform="col")
manual_cmd_frame.columnconfigure(1, weight=1, uniform="col")
manual_cmd_frame.columnconfigure(2, weight=1, uniform="col")
manual_cmd_frame.columnconfigure(3, weight=1, uniform="col")
manual_cmd_frame.columnconfigure(4, weight=1, uniform="col")

# --- DESPLEGABLE ACCIONS (5 opcions) ---
opcions_accions = ["Ordres", "Radar", "Mitjanes"]
combo_accions = ttk.Combobox(manual_cmd_frame, values=opcions_accions, state="readonly", font=("Arial", 12))
combo_accions.set("Selecciona acció")
combo_accions.grid(row=0, column=0, padx=5, pady=5, sticky=E+W)

# --- DESPLEGABLE ARGUMENTS (10 opcions) ---
opcions_arguments = ["Stop","Start","Freqüència","Velocitat","Lock","Moure"]
combo_arguments = ttk.Combobox(manual_cmd_frame, values=opcions_arguments, state="readonly", font=("Arial", 12))
combo_arguments.set("Selecciona argument")
combo_arguments.grid(row=0, column=1, padx=5, pady=5, sticky=E+W)

# --- ENTRY VALOR 1 ---
entry_valor1 = Entry(manual_cmd_frame, font=("Arial", 12))
entry_valor1.grid(row=0, column=2, padx=5, pady=5, sticky=E+W)

# --- ENTRY VALOR 2 ---
entry_valor2 = Entry(manual_cmd_frame, font=("Arial", 12))
entry_valor2.grid(row=0, column=3, padx=5, pady=5, sticky=E+W)


# --- BOTÓ D’ENVIAR ---
def enviar_comanda_manual():
    accio = combo_accions.get()
    argument = combo_arguments.get()
    v1 = entry_valor1.get()
    v2 = entry_valor2.get()
    
    try:
        if accio == "Ordres":
            if argument == "Freqüència":
                Send_Canvi_Frequencia(v1, int(v2))
            else: #Start i stop
                print("checkbox: ")
                print(argument.lower())
                print(v1.lower())
                Send_Ordres(argument.lower(),v1.lower())
                

        elif accio == "Radar":
            if argument == "Lock":
                Send_Radar(argument, int(v1), int(v2))
            else:
                Send_Radar(argument, abs(int(v1)))

        elif accio == "Mitjanes":
            Send_Mitjanes_Arduino(argument, 0)

            print("Comanda manual:", accio, argument, v1, v2)
            messagebox.showinfo("Comanda enviada", f"{accio}, {argument}, {v1}, {v2}")

    except ValueError or UnboundLocalError: # Tant ValueError com UnboundLocalError són codis d'error que surten quant es crida una variable introduïnt uns paràmetres per els quals la variable no està preparada. És a dir, mostra els errors a l'hora de cirdar funcions
        Notificació_Alarma(4) #Error de sintaxi



send_cmd_btn = Button(manual_cmd_frame, text="Enviar", bg='#4DA3FF', fg="white",
                      font=("Arial", 14), command=enviar_comanda_manual)
send_cmd_btn.grid(row=0, column=4, padx=5, pady=5, sticky=E+W)



# ───────────────────────────────────────────────
# CONFIGURACIÓ DE LA FIGURA MATPLOTLIB
# ───────────────────────────────────────────────

#-------------Grafica HT-------------
fig, (axT, axH) = plt.subplots(2, 1, figsize=(5, 3), sharex=True)
fig.subplots_adjust(hspace=0.4)
axT.set_title("Temperatura (°C)")
axH.set_title("Humitat (%)")

lineT, = axT.plot([], [], color='red')
lineH, = axH.plot([], [], color='blue')

lineMitjanaT, = axT.plot([], [], color='green', linestyle=':', linewidth=2)
lineMitjanaH, = axH.plot([], [], color='purple', linestyle=':', linewidth=2)

axT.set_xlim(0, 60)
axT.set_ylim(0, 50)
axH.set_ylim(0, 100)


# Inserir gràfica HT a Tkinter 
canvas = FigureCanvasTkAgg(fig, master=grafHT_frame)
canvas.get_tk_widget().grid(row=0, column=0, padx=5, pady=5, sticky=N+S+E+W)
canvas.draw()


#-------------Grafica Radar-------------
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

#-------------Grafica Simulació de l'òrbita 2D-------------
def draw_earth_slice(z):
    if abs(z) <= R_EARTH:
        slice_radius = (R_EARTH**2 - z**2)**0.5
    else:
        slice_radius = 0
    earth_slice = plt.Circle((0, 0), slice_radius, color='orange',
                             fill=False, linestyle='--', label='Tall Terra a Z')
    return earth_slice

earth_slice = draw_earth_slice(0)
ax_orbita.add_artist(earth_slice)


#-------------Grafica Simulació de l'òrbita 3D-------------

# ───────────────────────────────────────────────
# FIL DE RECEPCIÓ DE DADES
# ───────────────────────────────────────────────
def recepcion():
    while True:
        if Debug_RecepcioSimulada == False :
            if mySerial and mySerial.in_waiting > 0:
                try:
                    #Rebem la informació
                    linea = mySerial.readline().decode('utf-8').rstrip()
                    print("linea : "+str(linea))
                    data_chunks = linea.split(';') #Type list // data[x] = Type: str
    
                except UnicodeDecodeError:
                    print("Error en la rebuda de dades")
                    Notificació_Alarma(3)

                #Comprovem el checksum
                if (len(data_chunks)>=3):
                    try:
                        Checksum_Missatge = linea.rsplit(";",1)[1] #Adruirim el ultim element de la llista, en aquest cas, el checksum
                        MissatgeMenysChecksum = linea.rsplit(";",1)[0]
                        print("Checksum Reconstruit: "+str(Generar_Checksum(MissatgeMenysChecksum)))
                        print("Checksum rebut : " + str(Checksum_Missatge))
                        

                        if Generar_Checksum(MissatgeMenysChecksum) != int(Checksum_Missatge):
                            #Error en el checksum
                            #Implementar addevent
                            Notificació_Alarma(3)
                            print("-----ERROR_CHECKSUM-----")
                        else:
                            #iMPORTANT : DE MOMENT ESTÀ AIXI MENTRESTANT QUE EL CHECKSUM NO ESTÀ IMPLEMENTAT DEL TOT, UN COP SIUGI FUNCIONAL S'HA DE TREURE I DEIXAR NOMES EL ELSE
                            data_chunks = linea.split(';') #Type list // data[x] = Type: str
                            accio = data_chunks[0]
                            print("Acció : "+str(accio))
                            data = data_chunks[1].split(":")
                            #print(data)
                            #OBSERVACIONS
                            if accio == "0": 
                                #if len(data) == parametres: #Comprovació que rebem totes les dades
                                contact.append(int(temps()))
                                """
                                print("Humitat:", data[0])
                                print("Temp:   ", data[1]) 
                                print("Pos:", (int (data[2])/4779)*360)
                                print("Dist:   ", data[3])
                                print("Mitjana Hum:   ", data[4]) 
                                print("Mitjana Temp:   ", data[5])
                                print("Temps òrbita:  ",data[6])
                                print("Coord x:  ",data[7])
                                print("Coord y:  ",data[8])
                                print("Coord z:  ",data[9])
                                """
                                #print(temps())
                                histH.append(float(data[0]))
                                histT.append(float(data[1]))
                                histAng.append(float(data[2]))
                                histDist.append(float(data[3]))
                                histmitjH.append(float(data[4]))
                                histmitjT.append(float(data[5]))
                                histTemps.append(float(data[6]))
                                histCoordx.append(float(data[7]))
                                histCoordy.append(float(data[8]))
                                histCoordz.append(float(data[9]))
                                label_mitjanaT_arduino.config(text=f"Mitjana T Arduino: {float(data[5]):.2f} °C")
                                label_mitjanaH_arduino.config(text=f"Mitjana H Arduino: {float(data[4]):.2f} %")

                            #ALARMES
                            elif accio == "1":
                                threadNotificacio = threading.Thread(target=Notificació_Alarma(int(data[0])))
                                threadNotificacio.start()
                    except IndexError or ValueError:
                        print("Error intern recepció INDEX OUT OF RANGE")
                        Notificació_Alarma(3);    
                else:
                    print("ERROR: Falten arguments en el missatge")
                    Notificació_Alarma(3)   
                    
        else: 
            with data_lock: #No acabo d'entendre perque fem servir el thread.lock() si la variable que accedim no es compartida ni s'edita enlloc més
                histH.append(float("%.2f" % random.uniform(0,100)))
                histT.append(float("%.2f" % random.uniform(10,25)))
                histAng.append(float("%.2f" % random.uniform(0,180)))
                histDist.append(float("%.2f" % random.uniform(0,100)))
                histmitjH.append(float("%.2f" % random.uniform(0,100)))
                histmitjT.append(float("%.2f" % random.uniform(0,100)))
                #histTemps.append(float(temps_sim))
                histCoordx.append(float("%.2f" % random.uniform(0,6500000)))
                histCoordy.append(float("%.2f" % random.uniform(0,6500000)))
                histCoordz.append(float("%.2f" % random.uniform(0,6500000)))
                #temps_sim += 1
                #threading.Event().wait(1.0)
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
        if contact:
            # Actualitzar temperatura i humitat
            lineT.set_data(contact, histT)
            lineH.set_data(contact, histH)

            # ------ MITJANA TEMPERATURA (10 mostres) ------
            if len(histT) >= 10:
                mitjanesT = []
                for i in range(len(histT)):
                    if i < 9:
                        mitjanesT.append(None)
                    else:
                        finestra = histT[i-9:i+1]
                        mitjanesT.append(sum(finestra) / 10)
                lineMitjanaT.set_data(contact, mitjanesT)

            # ------ MITJANA HUMITAT (10 mostres) ------
            if len(histH) >= 10:
                mitjanesH = []
                for i in range(len(histH)):
                    if i < 9:
                        mitjanesH.append(None)
                    else:
                        finestra = histH[i-9:i+1]
                        mitjanesH.append(sum(finestra) / 10)
                lineMitjanaH.set_data(contact, mitjanesH)

            # Ajustos d'eixos
            axT.set_xlim(max(0, contact[-1] - 60), contact[-1] + 5)
            axH.set_xlim(max(0, contact[-1] - 60), contact[-1] + 5)

            axT.relim()
            axT.autoscale_view(scaley=True)
            axH.relim()
            axH.autoscale_view(scaley=True)

            canvas.draw_idle()

        window.after(50, actualitzar_graficaHT)



    except Exception as e:
        print("ERROR a actualitzar_graficaHT:", e)


# ───────────────────────────────────────────────
# CÀLCUL DE MITJANA DE TEMPERATURES 
# ───────────────────────────────────────────────

def start_mitjanaT_label(histT, data_lock, parent_widget, interval=0.5, row=None, column=None):

    #    Crea un Label a parent_widget i l'actualitza amb la mitjana de les últimes 10 temperatures.


    mitjana_label = Label(parent_widget, text="Mitjana: --", font=("Arial", 14))
    if row is None:
        mitjana_label.pack()
    else:
        mitjana_label.grid(row=row, column=column, padx=5, pady=5, sticky="w")

    def worker():
        last_len = 0
        while not stopCalc:
            with data_lock:
                cur_len = len(histT)
                if cur_len != last_len:
                    last_len = cur_len
                    if cur_len >= 10:
                        ultims = histT[-10:]
                        mitjana = sum(ultims) / 10.0

                        # ---- CONTROL DE 3 MITJANES CONSECUTIVES (TEMPERATURA) ----
                        global consec_Tmax, Tmax_val
                        if Tmax_val is not None:
                            if mitjana > Tmax_val:
                                consec_Tmax += 1
                                if consec_Tmax == 3:
                                    print("ALERTA: 3 mitjanes consecutives de temperatura superen el límit (detectat per l'estació de terra)")
                            else:       
                                consec_Tmax = 0
                                
                        text = f"Mitj 10 temp (ET): {mitjana:.3f} °C"
                    else:
                        text = f"Només {cur_len} valors; esperant 10..."

                    #evitem errors al tkinter
                    if mitjana_label.winfo_exists():
                        mitjana_label.after(0, lambda: mitjana_label.config(text=text))
                    else:
                        return  # El widget ja no existeix → parem el fil

            time.sleep(interval)

    th = threading.Thread(target=worker, daemon=True)
    th.start()
    return th, mitjana_label

# ───────────────────────────────────────────────
# CÀLCUL DE MITJANA DE HUMITATS 
# ───────────────────────────────────────────────

def start_mitjanaH_label(histH, data_lock, parent_widget, interval=0.5, row=None, column=None):
    """
    Crea un Label a parent_widget i l'actualitza amb la mitjana de les últimes 10 humitats.
    """

    mitjana_label = Label(parent_widget, text="Mitjana: --", font=("Arial", 14))
    if row is None:
        mitjana_label.pack()
    else:
        mitjana_label.grid(row=row, column=column, padx=5, pady=5, sticky="w")

    def worker():
        last_len = 0
        while not stopCalc:
            with data_lock:
                cur_len = len(histH)
                if cur_len != last_len:
                    last_len = cur_len
                    if cur_len >= 10:
                        ultims = histH[-10:]
                        mitjana = sum(ultims) / 10.0

                        # ---- CONTROL DE 3 MITJANES CONSECUTIVES (HUMITAT) ----
                        global consec_Hmax, Hmax_val
                        if Hmax_val is not None:
                            if mitjana > Hmax_val:
                                consec_Hmax += 1
                                if consec_Hmax == 3:
                                    print("ALERTA: 3 mitjanes consecutives d'humitat superen el límit (detectat per l'estació de terra)")
                            else:
                                consec_Hmax = 0

                        text = f"Mitj  10 hum(ET): {mitjana:.3f} %"
                        
                    else:
                        text = f"Només {cur_len} valors; esperant 10..."

                    #evitem errors al tkinter
                    if mitjana_label.winfo_exists():
                        mitjana_label.after(0, lambda: mitjana_label.config(text=text))
                    else:
                        return  # El widget ja no existeix → parem el fil            time.sleep(interval)

    th = threading.Thread(target=worker, daemon=True)
    th.start()
    return th, mitjana_label


# ───────────────────────────────────────────────
# FUNCIÓ PER ACTUALITZAR LA GRÀFICA DEL RADAR 
# ───────────────────────────────────────────────

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



# ───────────────────────────────────────────────────────────────
# FUNCIÓ PER ACTUALITZAR LA GRÀFICA DE SIMULACIÓ DE L'ÒRBITA 2D
# ───────────────────────────────────────────────────────────────

def actualitzar_grafica_orbita():
    try:
        if histCoordx and histCoordy:
            # Actualitzar línia d’òrbita
            orbit_plot.set_data(histCoordx, histCoordy)
            last_point_plot.set_offsets([[histCoordx[-1], histCoordy[-1]]])

            # Actualitzar tall de la Terra segons últim Z
            global earth_slice
            if histCoordz:
                z = histCoordz[-1]
            else:
                z = 0

            earth_slice.remove()
            earth_slice = draw_earth_slice(z)
            ax_orbita.add_artist(earth_slice)

            # Ajust de límits si cal
            '''''
            x = histCoordx[-1]
            y = histCoordy[-1]
            xlim = ax_orbita.get_xlim()
            ylim = ax_orbita.get_ylim()
            max_x = max(abs(xlim[0]), abs(xlim[1]), abs(x))
            max_y = max(abs(ylim[0]), abs(ylim[1]), abs(y))
            new_lim = max(max_x, max_y) * 1.1
            ax_orbita.set_xlim(-new_lim, new_lim)
            ax_orbita.set_ylim(-new_lim, new_lim)
            '''


            canvas_orbita.draw_idle()

        window.after(200, actualitzar_grafica_orbita)

    except Exception as e:
        print("ERROR a actualitzar_grafica_orbita:", e)


# ───────────────────────────────────────────────────────────────
# FUNCIÓ PER ACTUALITZAR LA GRÀFICA DE SIMULACIÓ DE L'ÒRBITA 3D
# ───────────────────────────────────────────────────────────────


# ───────────────────────────────────────────────
# LLANÇAR FIL I INICIAR GUI
# ───────────────────────────────────────────────
 
threadRecepcion = threading.Thread(target=recepcion, daemon=True)
threadRecepcion.start()


# iniciar actualització periòdica
window.after(50, actualitzar_graficaHT)
window.after(200, actualitzar_grafica_radar)
window.after(200, actualitzar_grafica_orbita)



def on_close():
    global running
    running = False
    # Guardar events abans de tancar
    try:
        save_all_events_to_file()
    except Exception as e:
        print("Error guardant events al tancar:", e)
    if Debug_RecepcioSimulada == False:
        if mySerial:
            mySerial.close()
        if mySerialOrbit:
            mySerialOrbit.close()
    window.destroy()



window.protocol("WM_DELETE_WINDOW", on_close)
window.mainloop()
