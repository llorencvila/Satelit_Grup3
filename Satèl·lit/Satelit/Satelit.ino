#include "DHT.h"
#include <Wire.h> 
#include <SoftwareSerial.h>
#include <Stepper.h>


SoftwareSerial mySerial(10, 11); // RX, TX (azul, naranja)
String data;
String periode;


#define DHTTYPE DHT11   // DHT 11
const int DHTPin = 2;   


DHT dht(DHTPin, DHTTYPE);
//Definició Alarmes
unsigned long lastDHTMillis = 0;//Aixo ha migrat a ultima lectura     // Guarda el último momento de lectura válida
unsigned long tiempoAlarma = 5000;  

long UltimaLectura[3] = {0*3}; //TEMP HUM DIST en aquest ordre
int Alarmes[3] = {0*3}; //Temp Hum Dist (en aquest ordre, els valors van de 0 (apagada) i 1(encesa))

int EstatFuncionamentSistemes[5] = {1*5}; // Temp Hum Dist Alarmes Escombreig || LLista que ens perrmet controlar quins sistemes estàn encesos o no (per default estan engegats fins que rebin el comando contrari) 1 = ENGEGAT
int PeriodeEmisioDelsSistemes[3] = {500*3}; //Temp Hum Dist, En aquest ordre
unsigned long NextMillis[3]; //Temp Hum Dist, En aquest ordre
int NumeroValorsMitjanes[3]; //Temp Hum Dist, En aquest ordre

//Nota: Seria bo plantejar-se fer una estrucutura per administrar millor tota aquesta quantitat de llistes

int ElementsUlitmMissatge[4]; //Acció Arguments (Id_Sys / Info) Valor || Llista d'elements que pot tenir l'ulitm missatge, CONSULTAR EXCEL PROTOCOL BITS en cas de dubte

//Definició Motor pas a pas
#define OUTPUT1   7                // Connected to the Blue coloured wire
#define OUTPUT2   6                // Connected to the Pink coloured wire
#define OUTPUT3   5                // Connected to the Yellow coloured wire
#define OUTPUT4   4                // Connected to the Orange coloured wire

const int stepsPerRotation = 4779;  //com que la transmissió es produeix per engranatges hi ha una relació de de 2.3333 (al ser decimal es perd presisció)´
int VelMotor = 5; // velocitat màxima (amb la alimentacio del 5v d'arduino), si és més gran el motor es cala
int pos = 0;
int Sentit = 1;
int llargadaSteps = 1;
Stepper myStepper(stepsPerRotation, OUTPUT1, OUTPUT3, OUTPUT2, OUTPUT4);

//Definició Sensor Ultrasons
const int EchoPin = 3;
const int TriggerPin = 9;

void setup(){
  Serial.begin(9600);

  mySerial.begin(9600);
  //CONFIGURACIÓ STEPPER
  myStepper.setSpeed(VelMotor);
  //CONFIGURACIÓ SENSOR ULTRASONS
  pinMode(TriggerPin, OUTPUT);
  pinMode(EchoPin, INPUT);

  dht.begin();

  for (int i ; i<3; i++){ //recorre tots els elements de l'array nextmillis
    NextMillis[i] = millis()+PeriodeEmisioDelsSistemes[i];
  }

  }
/*
void GetPeriode (){ 
  if (mySerial.available()) {
    periode = linmySerial.readStringea.split(',');
      if (data[0] == 22)
        int interval = perdiode [1];
      if (data[0] == 23)
        int intervalRad = periode [1];
*/

float GetTemp(){
  if (millis() >=NextMillis[0] && EstatFuncionamentSistemes[0] == 1){
    float t = dht.readTemperature();

    if (isnan(t)){
      return -1;

    } else {
      Alarmes[0] = 0;
      UltimaLectura[0] = millis();
      return t;
      }

  }else{
    return 0;
    }
  }

float GetHum(){
  if (millis() >=NextMillis[1] && EstatFuncionamentSistemes[1] == 1){
    float h = dht.readHumidity();

    if (isnan(h)){
      return -1;

    }else{
      Alarmes[1] = 0;
      UltimaLectura[1] = millis();
      return h;
      }

    }else{
      return 0;
    }
  }

int GetDist(){
  if (millis() >=NextMillis[2]  && EstatFuncionamentSistemes[2] == 1){
    long duration, distCm;
    
    digitalWrite(TriggerPin, LOW);  //para generar un pulso limpio ponemos a LOW 4us
    delayMicroseconds(4); //Aqui hauriem d'implementar la funció millis ()
    digitalWrite(TriggerPin, HIGH);  //generamos Trigger (disparo) de 10us
    delayMicroseconds(10);
    digitalWrite(TriggerPin, LOW);
    
    duration = pulseIn(EchoPin, HIGH);  //medimos el tiempo entre pulsos, en microsegundos
    
    distCm = duration * 10 / 292/ 2;   //convertimos a distancia, en cm
    return distCm;

    }else{
      return 0;
    }
  }

void MoureMotor(){
  //MOURE MOTOR RADAR
  if (EstatFuncionamentSistemes[4] == 1){
    if (pos <=0){
      Sentit = 1;
    }else if (pos >= 4779) {
      Sentit = -1;
    }
    myStepper.step(Sentit * llargadaSteps);
    pos = pos + (Sentit*llargadaSteps);
    return;
    }
  }


void SendObservacions(){ 
    float h = GetHum();
    float t = GetTemp();
    int dist = GetDist();
    //Comunicació DEBUG
    /*
    Serial.print(GetHum());
    Serial.print(":");
    Serial.println(GetTemp());
    */
    //TELEMETRIA
    mySerial.print(0);
    mySerial.print(";");
    mySerial.print(GetHum());
    mySerial.print(":");
    mySerial.print(GetTemp());
    mySerial.print(":");
    mySerial.print(pos);
    mySerial.print(":");
    mySerial.println(GetDist());
    //CHECHSUM
    //nt chechsum = (int(";")+GetHum)

    
  return;
  }

void SendAlarm (int argument){
  //llista d'arguments
  //0 = TEMP    |    1 = HUMITAT    |    2 = DISTÀNCIA    | 
    if (argument == 0 ||argument == 1 || argument == 2){ //comprovem que l'argument estigui dins del rang 
      mySerial.print(1); //Codi identificatiu Alarmes
      mySerial.print(";");//Separador de arguments
      mySerial.println(argument);
      }
  }

void GetInfo (){
  if (mySerial.available()) {
    data = mySerial.readString();
    data.trim(); //elimina tots els caràcters que no siguin lletres. Essencial per poder fer els if's seguents
    Serial.println("hemRebut");
    Serial.println(data);
    //PARSING
    int i = 0; //Acció Arguments (Id_Sys / Info) Valor
    int UltimIndexSeparador = 0;
    int IndexSeparador;

    while (i<4 || IndexSeparador != -1){
      IndexSeparador = data.indexOf(";");

      if (IndexSeparador != -1){
        ElementsUlitmMissatge[i] = data.substring(UltimIndexSeparador, IndexSeparador).toInt();
        UltimIndexSeparador = IndexSeparador+1;
      i++;
      }
    }
    //Crida de funcions relacionades amb la rebuda de dades
    //ORDRES
    if (ElementsUlitmMissatge[0] == "2"){ //Acció ->ORDRE
      Serial.println("Ordre");
      if (ElementsUlitmMissatge[1] == 0){ //Argument -> Stop
        EstatFuncionamentSistemes[ElementsUlitmMissatge[2]] = 0;

      } else if (ElementsUlitmMissatge[1] == "2"){ //Argument -> Seguir
        EstatFuncionamentSistemes[ElementsUlitmMissatge[2]] = 1;

      } else if (ElementsUlitmMissatge[1] == "3"){ //Argument -> Canvi de freq
        PeriodeEmisioDelsSistemes[ElementsUlitmMissatge[2]] = ElementsUlitmMissatge[3]; //
      }
    }
    //RADAR
    if (ElementsUlitmMissatge[0] == "3"){

      if (ElementsUlitmMissatge[1] == "0"){
        llargadaSteps == ElementsUlitmMissatge[2];
        //Realment canviem la llargada del cada desplaçament, és així pq la velocitat real del motor ja és la maxima de per si per tal de que no es cali
        
      }else if (ElementsUlitmMissatge[1] == "1"){
        //CODI LOCK
      } else if (ElementsUlitmMissatge[1] == "2"){
        pos = ElementsUlitmMissatge[2];

      }

      }
    }
    //MITJANES
    if (ElementsUlitmMissatge[0] == "4"){
      NumeroValorsMitjanes[ElementsUlitmMissatge[1]] = ElementsUlitmMissatge[2];
    }
    Serial.print(data);

  }
//
//
void loop() {
  
  MoureMotor();
  GetInfo();
  SendObservacions();


    //CONTROL D'ALARMES
    if (EstatFuncionamentSistemes[3]==1){ 
      for (int i=0; i<2;i++){
        if (Alarmes[i] == 0 && millis()-UltimaLectura[i] > tiempoAlarma){
          Alarmes[i] = 1;
          SendAlarm(i);
          Serial.println("FALLO");
        }
      }
    }

}
  
