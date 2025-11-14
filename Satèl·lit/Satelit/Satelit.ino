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
const int DHTPin = 5;   


DHT dht(DHTPin, DHTTYPE);
//Definició Alarmes
unsigned long lastDHTMillis = 0;     // Guarda el último momento de lectura válida
unsigned long tiempoAlarma = 5000;  
bool alarmaActiva = false;

//Definició Motor pas a pas
#define OUTPUT1   7                // Connected to the Blue coloured wire
#define OUTPUT2   6                // Connected to the Pink coloured wire
#define OUTPUT3   5                // Connected to the Yellow coloured wire
#define OUTPUT4   4                // Connected to the Orange coloured wire

const int stepsPerRotation = 4779;  //com que la transmissió es produeix per engranatges hi ha una relació de de 2.3333 (al ser decimal es perd presisció)´
int VelMotor = ; // velocitat màxima (amb la alimentacio del 5v d'arduino), si és més gran el motor es cala
int pos = 0;
int Sentit = 1;
int llargadaSteps = 500;
Stepper myStepper(stepsPerRotation, OUTPUT1, OUTPUT3, OUTPUT2, OUTPUT4);

//Definició Sensor Ultrasons
const int EchoPin = 6;
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

void DHTSendData(){ //funció obsoleta, la seva funcionalitat ha migrat a SendData. A data de (14/11/25)
  float h = dht.readHumidity();
  float t = dht.readTemperature();

  if (isnan(h) || isnan(t)) {
    Serial.println("DHT 11: ERROR (lectura=NaN)");
    return;
  } else{
    Serial.print(h);
    Serial.print(":");
    Serial.println(t);
    mySerial.print(h);
    mySerial.print(":");
    mySerial.println(t);
    lastDHTMillis = millis();   // actualiza el tiempo de la última lectura
    alarmaActiva = false;       // desactiva la alarma si había saltado
      }
  return;
  }

int ping(int TriggerPin, int EchoPin) {
  long duration, distCm;
  
  digitalWrite(TriggerPin, LOW);  //para generar un pulso limpio ponemos a LOW 4us
  delayMicroseconds(4);
  digitalWrite(TriggerPin, HIGH);  //generamos Trigger (disparo) de 10us
  delayMicroseconds(10);
  digitalWrite(TriggerPin, LOW);
  
  duration = pulseIn(EchoPin, HIGH);  //medimos el tiempo entre pulsos, en microsegundos
  
  distCm = duration * 10 / 292/ 2;   //convertimos a distancia, en cm
  return distCm;
}


void SendData(int pos){
  float h = dht.readHumidity();
  float t = dht.readTemperature();

  if (isnan(h) || isnan(t)) {
    Serial.println("DHT 11: ERROR (lectura=NaN)");
    return;
  } else{
    //Comunicació DEBUG
    Serial.print(h);
    Serial.print(":");
    Serial.println(t);
    //TELEMETRIA
    mySerial.print(h);
    mySerial.print(":");
    mySerial.print(t);
    mySerial.print(":");
    mySerial.print(pos);
    mySerial.print(":");
    mySerial.println(ping(TriggerPin,EchoPin));

    lastDHTMillis = millis();   // actualiza el tiempo de la última lectura
    alarmaActiva = false;       // desactiva la alarma si había saltado
      }
  return;
  }



void loop() {
  //MOURE MOTOR RADAR
  if (pos <=0){
    Sentit = 1;
  }else if (pos >= 4779) {
    Sentit = -1;
  }
  myStepper.step(Sentit * llargadaSteps);
  pos = pos + (Sentit*llargadaSteps);

  if (millis() >=NextMillis){
    int dist = ping(TriggerPin,EchoPin);
  NextMillis = millis()+interval;

  //REBUDA INFORMACIÓ
  if (mySerial.available()) {
    data = mySerial.readString();
    data.trim(); //elimina tots els caràcters que no siguin lletres. Essencial per poder fer els if's seguents
    Serial.print(data);
    }

  //ENVIAR INFORMACIÓ
  if (data == "REANUDAR" || data == "INICIAR"){
    if (millis() >=NextMillis){
      SendData(pos);
      NextMillis = millis()+interval;
      }
    } else if (data == "STOP"){
      Serial.println("Parant");
    } //else{
    //  Serial.println("Sense_Dades");
    //}

    //CONTROL D'ALARMES
    if ((millis() - lastDHTMillis) > tiempoAlarma && !alarmaActiva) {
      Serial.println("FALLO");
      mySerial.println("FALLO");
      alarmaActiva = true;  
    }
  }
}
  





