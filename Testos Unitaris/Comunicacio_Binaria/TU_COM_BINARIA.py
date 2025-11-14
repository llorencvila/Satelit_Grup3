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
        "angrad":0b011,    
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
    "mitjanes":{
        "temp" : 0b000,
        "hum" : 0b001,
        "radar" : 0b010,
        "alarma": 0b011,
        "all" : 0b100,
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
    #print(missatge)
    missatge = int(missatge,2)

    return missatge

def IEEE754aFloat(InfoGen): #0 10010 1010000000
    bias = 15
    #En el format IEEE745, el primer bit és el signe, els 5 seguents són el exponent i els 10 restants la fracció/mantissa

    if InfoGen[0] == "0":
        signe = 1
    else:
        signe = -1

    exponent = int(InfoGen[1:6],2)
    
    e = exponent-bias 
    
    PartFraccionaria = InfoGen[6:16]
    mantissa = 0
    for i in range(len(PartFraccionaria)):
        mantissa = mantissa + int(PartFraccionaria[i])*(2**(-(i+1)))

    decimal = signe*(1+mantissa)*2**e
    return decimal

def DesxifrarMissatge (missatge):
    AccioRes = 0
    ArgumentRes = 0
    InfoRes = 0
    AddRes = 0
    # 1.1r Comprovar que la longitud del missatge és correcte
    # 1.2r Comprovar que el bit de pareitat sigui correcte
    # 2n Separar les accions i arguments
    # 3r A partir de les accions i arguments, interpretar el missatge rebut
    #Com que l'arduino només donarà senyals d'observació i alarmes, ens podem petar la meitat de codi

    missatge = bin(missatge)[2:] #Aixó és un string
    missatgellista = list(missatge)
    #──────────────────────────────────────────────────────────────────────────────
    #1.1 comprovem quel missatge rebut en binari  tingui una llargada multiple de 8
    if len(missatgellista) % 8 !=0:
        return -1 #error de rebuda del m    issatge, Llargada insuficient
    
    #1.2 comprovem el bit de parietat par
    parietat = 0
    for i in range(len(missatge)):
        if missatge[i] == "1":
            parietat = parietat+1
    
    if parietat % 2 !=0:
        return -2 #Parity check insuficient

    #2  Eliminem els dos pirimers caràcters i comparem els tres primers caràcters i despres els tres seguents
    missatge = missatge[2:] #Eliminem el bit inicial i el bit de parietat

    accio = int(missatge[0:3],2)
    for x in Accions: #NOTA MENTAL ->> Aqui hi toca una busqueda No una iteració !!!
        if Accions[x] == accio:
            AccioRes = x
        #else:
        #   return -3 #Acció no reconeguda

    argument = int(missatge[3:6],2)
    for x in Arguments[AccioRes]:
        if Arguments[AccioRes][x] == argument:
            ArgumentRes = x
        #else: 
        #    return -4 #Argument no reconegut
        
    #------------- APARTAT INFO --------------- 
    #BLOC LILA
    #Aqui totes les informacions que es estan codificades en IEEE745
    Info = missatge[6:]
    if AccioRes == "observacio" or AccioRes == "ordre" and ArgumentRes == "freq" or AccioRes == "radar" and  AccioRes != "lock":
        InfoRes  = IEEE754aFloat(Info)
    
    #BLOC VERD
    #Aqui totes les informacions de amb només 1 byte
    if AccioRes == "alarma":
        for x in Arguments["alarma"]:
            if Arguments["alarma"][x] == argument:
                InfoRes = x
            #else:
            #    return -5 #Alarma no reconeguda
            
    #BLOC BLAU      
    #aqui les informacions amb 2bytes (identificador absolut de sistemes)
    if AccioRes == "ordre" and ArgumentRes == "stop" or ArgumentRes =="seguir":
        Info = int (Info [0:3],2)
        for x in Arguments["sysid"]:
            if Arguments["sysid"][x] == Info:
                InfoRes = x
            #else:
            #    return -6 #Ordre no reconeguda
            
    #BLOC VERMELL
    #Aqui les informacions que tenen dos arguments difernets
    if ArgumentRes == "lock":
        Add = int (Info[3:6],2)  #la veriable es diu add per coherencia amb la funció GenerarMissatge(), però en aquest cas es simplement la posició que ha de prendre el servo
        Info = int (Info[0:3],2)
        
        InfoRes = (((Info)/256)*360) #Factor de conversió per passar un valor de 0 a255 a 360º
        AddRes = (((Add)/256)*360)
    
    
    #-------------- RETURN FINAL --------------
    #El missatge ha de retornar una llista amb la acció, Argument i informació
    MissatgeRebut = [AccioRes, ArgumentRes, InfoRes, AddRes]
    return MissatgeRebut


mensaje = GenerarMissatge("ORDRE","FREQ",13,0)
print(mensaje)
print (DesxifrarMissatge(mensaje))

#print (type(DesxifrarMissatge(13781632)))

#print(IEEE754aFloat("0100101010000000"))
#010 010 0100101010000000s