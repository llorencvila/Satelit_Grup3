def Generar_Checksum(missatge):
    checksum = 59 #Començem amb 59 pq és el codi ascii del ";", el qual s'elimina per la funció rsplit
    for i in range(len(missatge)):
        checksum = checksum + ord(missatge[i]) #La funció ord() retorna el valor ASCII de l'element

    return checksum



linea = "0;-1.00:-1.00:1186:0:0.000:0.000:22138.74:6763821.00:-311709.47:-0.00;3554"

#print(linea.rsplit(";",1))
Checksum_Missatge = linea.rsplit(";",1)[1] #Adruirim el ultim element de la llista, en aquest cas, el checksum
MissatgeMenysChecksum = linea.rsplit(";",1)[0]
#print(Checksum_Missatge)

#print(Generar_Checksum(linea[0]))
#print(linea)
#print(linea[1])
print(type(Generar_Checksum(MissatgeMenysChecksum)))
print("a")
print(Checksum_Missatge)
if Generar_Checksum(MissatgeMenysChecksum) != int(Checksum_Missatge):
    #Error en el checksum
    print("-----ERROR_CHECKSUM-----")
else:
    #iMPORTANT : DE MOMENT ESTÀ AIXI MENTRESTANT QUE EL CHECKSUM NO ESTÀ IMPLEMENTAT DEL TOT, UN COP SIUGI FUNCIONAL S'HA DE TREURE I DEIXAR NOMES EL ELSE
    data_chunks = linea.split(';') #Type list // data[x] = Type: str
    accio = data_chunks[0]
    print("Acció : "+str(accio))
    data = data_chunks[1].split(":")
    print(data)
    #OBSERVACIONS






#print(Generar_Checksum("0;-1.00:-1.00:1186:0:0.000:0.000:22138.74:6763821.00:-311709.47:-0.00;")) #3554