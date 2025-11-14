//#include <map>
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
int Float_a_IEE745(float entrada){
  //1r Determinem el signe
  int signe = 0;
  if (entrada >0){
    signe = 1;
  } else{
    signe = -1;
  }

    //2n 
  }

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
