#include <math.h>
/*
const String NomsAccions[5] = ["Obs", "Alarma", "Ordres", "Radar", "Mitjanes"];
const String NomsArgObs[4] = ["Temp", "Hum", "Dist", "AngRad"];
const String NomsArgAlarm[3] = ["Temp", "Hum", "Dist"];
const String NomsArgOrdres[3] = ["Stop", "Seguir"];
const String NomsArgRad[3] = ["Vel", "Lock", "Mov"];
const String IdAbsoluts[5] = ["Temp", "Hum", "Radar", "Alarmes", "All"];
*/
/*
Observacions (000)
⦁        Temperatura (000)
⦁        Humitat (001)
⦁        Distància (010)
⦁        AngleRadar (011)
Alarmes (001)
⦁        Temperatura (000)
⦁        Humitat (001)
⦁        Distància (010)
Ordres (010)
⦁        Stop (000)
⦁        Seguir (001)
⦁        Velocitat Mostreig (010)
Radar (011)
⦁        Velocitat (000)
⦁        Lock (001) 
⦁        Moure X lloc (010)
Mitjanes (100)
-       Temperatura: 000
-       Humitat: 001
-       Radar: 010
-       Alarmes:  011
-       All : 100
-       Escombreig: 101
*/
int Enter_a_Binari(int EnterEntrada){//els numeros (el return) estan escrits de dreta a esquerra
    int StrBinari[16] = {0*16};
    int i = 15 ;

    while (EnterEntrada >0){
        StrBinari[i--] = EnterEntrada %2;
        EnterEntrada = EnterEntrada/2;
    }
    
    return StrBinari; 
    //for (int i = 0; i <=16; i++)
    //  printf("%d", StrBinari[i]);   
}

int Float_a_Binari(float FraccioEntrada){
    int StrBinari[16] = {0*16};
    int i = 0;
    //int NumDecimals = 3;
    //int FraccicoEntradaint = (int)FraccioEntrada*pow(10,NumDecimals); //10^num decimals 
    

    for (i = 0 ; i<=16 ; i++){   
        FraccioEntrada = FraccioEntrada*2;
        if (FraccioEntrada-1 >=0){
            StrBinari[i]=1;
            FraccioEntrada = FraccioEntrada -1; //li treiem la part decimal
        }else{
            StrBinari[i]=0;
        }
    }
    return StrBinari;
}

int Biari_a_Decimal(int Bin[16]){ //En aquest cas ens interessa passar l'exponent a un strbinari
  int Result;
  for(int i = len(Result); i>0 ;i-- ){
    Result  = Result + pow(2,i);
  }

  return Result;
}

int Float_a_IEE745(float entrada){
  int BinFinal[16] = {0*16}; //un bit està dedicat al signe i 5 per a l'exponent
  //1r Determinem el signe
  if (entrada >0){
    BinFinal[0] = 1;
  } else{
    BinFinal[0] = -1;
  }
  //2n Convertir entrada a binari, separadament tant de la part entera com la decimal
  int PartEntera = (int)entrada;
  float PartFraccionaria = PartEntera - entrada;

  int PartEnteraBin[16] = Enter_a_Binari(PartEntera);
  int PartFraccionariaBin[16] = Float_a_Binari(PartFraccionaria);

  char trobat = 0;
  int i = 0 ;
  int EspaisEnBlanc;

  while (trobat == 0){
    if (PartEnteraBin[i] == 1){
        EspaisEnBlanc = i;
    } else{
        i++;
    }
  }
  int exponent = 15-EspaisEnBlanc;
  //Aqui calculem l'exponent en binari 
  

  //Ajuntem la part entera i flotant en un sol string binary de 15 caràcters
  i = 6;
  while (i<len(PartEnteraBin)){
    BinFinal[i]=PartEnteraBin[i+EspaisEnBlanc];
    i++;
  }
  while (i<len(BinFinal)){
    BinFinal[i] = PartFraccionariaBin[i-EspaisEnBlanc];
    i++;
  }

  }



int main (){
    Float_a_Binari(0.5);
}
 /* 
  int GenerarMissatgeObservacions(int Argument, float info) {
    char trobat = 0;
    int i=0;
    //TROBAR VALOR ACCIÓ
    while (trobat ==0){
      if (NomsArgObs[i] == Argument){
      trobat = 1;
      byte AccioMiss = i;
    }
  }
  if (trobat == 0) {
      return -1 //Acció no reconeguda


}


void setup() {
  // put your setup code here, to run once:

}

void loop() {
  // put your main code here, to run repeatedly:

}
*/
