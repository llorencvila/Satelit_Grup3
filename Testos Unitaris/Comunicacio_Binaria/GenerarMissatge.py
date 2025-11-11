#DOCUMENT REDUNDANT. TOT EL CONTINGUT HA PASSAT A TU_COM_BINARIA.PY
#ELIMINAR AQUEST DOCUMENT D'AQUI A UNS QUANTS DIES SI NO ES PRODUEIXEN ERRORS
#DATA D'AVUI 11/11/25



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
        #"escb":0b011, s'ha mogut de lloc, si despres de un perïode de proves no dona errors es pot treure (11/11/25)
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
        "escb" : 0b101
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

   
    missatge = ['1','0'] #El missatge comença sempre amb un bit a 1 i el segon espai que es el bit de parietat (encara per definir)
    llargadaMissatge = 1
    try:
        missatge.append(bin((Accions[AccioMiss]))[2:].zfill(3))
        #Primers 3 bits del missatge escrits (La accció)

        missatge.append(bin(Arguments[AccioMiss][ArgMiss])[2:].zfill(3))
        #No hi ha el desplaçament de bits ja que es fa en els seguents apartats (ja que la longitud pot variar depenent del tipus)
        #Primers 6 bits del missatge escrits (Acció + Argument)
        llargadaMissatge = llargadaMissatge+3

        #BLOC BLAU
        if AccioMiss == "ordre" and ArgMiss !="freq": #Si és un d'aquests dos casos, vol dir que només ens cal l'identificador de sistemes i no pas tot un byte sencer (Consultar excel)  
            missatge.append(bin(Arguments["sysid"][InfoMiss])[2:].zfill(3))
            llargadaMissatge = llargadaMissatge+3   
            #return missatge
        
        #BLOC LILA
        elif AccioMiss == "observacio" or AccioMiss == "ordre" and ArgMiss == "freq" or AccioMiss == "radar" and ArgMiss != "lock":
            if abs(Info) <65504: #Comprovació que la informació capiga en 2 bytes IEEE 754
            #Aqui es on toca la conversió IEEE754
                #Segurament hi ha una millor forma de fer aixo però m'esitc quedant sense opcions
                missatge.append(bin(np.float16(13).view('H'))[2:].zfill(16))
                llargadaMissatge = llargadaMissatge+16
                #return missatge

            
        #BLOC VERMELL
        elif AccioMiss == "radar" and ArgMiss == "lock":
            InfoMiss = (InfoMiss/360)*258
            AddMiss = (AddMiss/360)*258
            #Aqui nescesita dos arguments 
                #1r -> Posició (int de 0 -> 258) == Info 
                #2n - >Angle De busqueda (int de 0->258) == Add
                #Amb aquesta aproximació es perd resolució(la resolució del stepper és de 1024, que pasa a ser reduit a una quarta part)
            InfoMiss = int(abs (InfoMiss)) #Ens assegurem que els paràmetres siguin si o si valors enters positius
            AddMiss = int(abs(AddMiss)) 

            if  InfoMiss <258 and AddMiss <258: #Comprovació que els valors son màxim un byte 
                missatge.append(bin(InfoMiss)[2:].zfill(8))
                missatge.append(bin(AddMiss)[2:].zfill(8))
                llargadaMissatge = llargadaMissatge+8
            else:
                return -2 #Arguments lock > 258

    except KeyError:
        return -1 #Algun nom és incorrecte o està mal escrit
    
    ##Fer el bit de parietat -> EL BIT DE PARIETAT PAR FA QUE EL MISSATGE SEMPRE SIGUI PARELL
    missatge= "".join(missatge)
    missatge=list(missatge)
    parietat = 0

    for i in range(len(missatge)):
        if missatge[i] == "1":
            parietat = parietat+1

    if (parietat+1) % 2 == 0: #el bit de paerietat par tmb es te en conte a l'hora de mirar la parietat
        missatge[1] = "1"

    #Empaquetar i conversió integral
    missatge ="".join(missatge)
    print(missatge)
    missatge = int(missatge,2)

    return missatge

print(GenerarMissatge("ORDRE","FREQ",13,0))












