#include "DHT.h"
#include <Wire.h> 
#include <SoftwareSerial.h>
#include <Stepper.h>


SoftwareSerial mySerial(10, 11); // RX, TX (azul, naranja)
int interval = 500;
int intervalRad = 500;
String data;
unsigned long NextMillis;
unsigned long NextMillisRad;


#define DHTTYPE DHT11   // DHT 11
const int DHTPin = 2;   


DHT dht(DHTPin, DHTTYPE);
//Definició Alarmes
unsigned long lastDHTMillis = 0;//Aixo ha migrat a ultima lectura     // Guarda el último momento de lectura válida
unsigned long tiempoAlarma = 5000;  
long UltimaLectura[3] = {0*3}; //TEMP HUM DIST en aquest ordre
int Alarmes[3] = {0*3}; //Temp Hum Dist (en aquest ordre, els valors van de 0 (apagada) i 1(encesa))


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

  NextMillis = millis()+interval;
  dht.begin();

  NextMillisRad = millis()+intervalRad;

  }

float GetTemp(){
  float t = dht.readTemperature();
  if (isnan(t)){
    return -1;
  }
  Alarmes[0] = 0;
  UltimaLectura[0] = millis();
  return t;
}

float GetHum(){
  float h = dht.readHumidity();
  if (isnan(h)){
    return -1;
  }
  Alarmes[1] = 0;
  UltimaLectura[1] = millis();
  return h;
}

int GetDist(){
  long duration, distCm;
  
  digitalWrite(TriggerPin, LOW);  //para generar un pulso limpio ponemos a LOW 4us
  delayMicroseconds(4); //Aqui hauriem d'implementar la funció millis ()
  digitalWrite(TriggerPin, HIGH);  //generamos Trigger (disparo) de 10us
  delayMicroseconds(10);
  digitalWrite(TriggerPin, LOW);
  
  duration = pulseIn(EchoPin, HIGH);  //medimos el tiempo entre pulsos, en microsegundos
  
  distCm = duration * 10 / 292/ 2;   //convertimos a distancia, en cm
  return distCm;
}

void MoureMotor(){
  //MOURE MOTOR RADAR
  if (pos <=0){
    Sentit = 1;
  }else if (pos >= 4779) {
    Sentit = -1;
  }
  myStepper.step(Sentit * llargadaSteps);
  pos = pos + (Sentit*llargadaSteps);
  return;
  }


void SendObservacions(){ 
    //Comunicació DEBUG
    Serial.print(GetHum());
    Serial.print(":");
    Serial.println(GetTemp());
    //TELEMETRIA
    mySerial.print(GetHum());
    mySerial.print(":");
    mySerial.print(GetTemp());
    mySerial.print(":");
    mySerial.print(pos);
    mySerial.print(":");
    mySerial.println(GetDist());

    
  return;
  }

void GetInfo (){
  if (mySerial.available()) {
    data = mySerial.readString();
    data.trim(); //elimina tots els caràcters que no siguin lletres. Essencial per poder fer els if's seguents
    Serial.print(data);
  }
  }
//
//
void loop() {
  
  MoureMotor();
  GetInfo();

  //ENVIAR INFORMACIÓ
  if (data == "REANUDAR" || data == "INICIAR"){
    if (millis() >=NextMillis){
      //Serial.println("estem dins");
      SendObservacions();
      NextMillis = millis()+interval;
      }
    } else if (data == "STOP"){
      Serial.println("Parant");
    }


    //CONTROL D'ALARMES 
    for (int i=0; i<2;i++){
      if (Alarmes[i] == 0 && millis()-UltimaLectura[i] > tiempoAlarma){
        Alarmes[i] = 1;
        Serial.println("FALLO");
        mySerial.println("FALLO");
      }
    }

}
  





