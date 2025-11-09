import numpy as np

Accions = {
    "observacio":0b000,
    "alarma":0b001,
    "ordre":0b010,
    "radar":0b011,
}

Arguments = {
    "observacio" : {
        "temp":0b000,
        "hum":0b001,
        "dist":0b010,
        "angRad":0b011,    
    },
    "alarma" : {
        "temp":0b000,
        "hum":0b001,
        "dist":0b010
    },
    "ordre" : {
        "stop":0b000,
        "seguir":0b001,
        "freq":0b010,
        "escb":0b011,
    },
    "radar" : {
        "vel":0b000,
        "lock":0b001,
        "mov":0b010,
    },
    "sysid" : {
        "temp" : 0b000,
        "hum" : 0b001,
        "radar" : 0b010,
        "alarma": 0b011,
        "all" : 0b100,
    }
}

def GenerarMissatge(Accio,Arg,Info,Add): 
    AccioMiss = Accio.lower()  
    ArgMiss = Arg.lower()

    if isinstance(Info, str):
        InfoMiss = Info.lower()
    else:
        InfoMiss = Info

    if isinstance(Add, str):
        AddMiss = Add.lower()
    else:
        AddMiss = Add

    missatge = 0b0  
    try:
        missatge = missatge + Accions[AccioMiss]
        missatge = missatge <<3
        #Primers 3 bits del missatge escrits (La accció)

        missatge = missatge + Arguments[AccioMiss][ArgMiss]
        #No hi ha el desplaçament de bits ja que es fa en els seguents apartats (ja que la longitud pot variar depenent del tipus)
        #Primers 6 bits del missatge escrits (Acció + Argument)

        #BLOC BLAU
        if AccioMiss == "ordre" and AccioMiss !="freq": #Si és un d'aquests dos casos, vol dir que només ens cal l'identificador de sistemes i no pas tot un byte sencer (Consultar excel)  
            missatge = missatge <<3
            missatge = missatge + Arguments["sysid"][InfoMiss]
            return missatge
        
        #BLOC LILA
        elif AccioMiss == "observacio" or AccioMiss == "ordre" and ArgMiss == "vel" or AccioMiss == "radar" and ArgMiss != "lock":
            if abs(Info) <65504: #Comprovació que la informació capiga en 2 bytes IEEE 754
            #Aqui es on toca la conversió IEEE754
                missatge = missatge<<16
                FloatBin = bin(np.float16(Info).view('H'))[2:].zfill(16)
                missatge =missatge + FloatBin
                return missatge
            
        #BLOC VERMELL
        elif AccioMiss == "radar" and ArgMiss == "lock":
            #Aqui nescesita dos arguments 
                #1r -> Posició (int de 0 -> 258) == Info 
                #2n - >Angle De busqueda (int de 0->258) == Add
                #Amb aquesta aproximació es perd resolució(la resolució del stepper és de 1024, que pasa a ser reduit a una quarta part)

            InfoMiss = int(abs (InfoMiss)) #Ens assegurem que els paràmetres siguin si o si valors enters positius
            AddMiss = int(abs(AddMiss)) 

            if  InfoMiss <258 and AddMiss <258: #Comprovació que els valors son màxim un byte 
                missatge = missatge <<8
                missatge = missatge+bin(InfoMiss)
                missatge = missatge <<8
                missatge = missatge+bin(AddMiss)
            else:
                return -2 #Arguments lock > 258

    except KeyError:
        return -1 #Algun nom és incorrecte o està mal escrit
    
print(bin(GenerarMissatge("ORDRE","SEGUIR","TEMP",0)))












