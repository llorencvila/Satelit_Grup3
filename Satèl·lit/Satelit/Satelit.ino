#include "DHT.h"
#include <Wire.h> 
#include <SoftwareSerial.h>
#include <Stepper.h>

// Comunicació amb l’estació
SoftwareSerial mySerial(10, 11); // RX, TX
String data;

// ----- DHT11 -----
#define DHTTYPE DHT11
const int DHTPin = 2;
DHT dht(DHTPin, DHTTYPE);

// ----- Sistemes -----
unsigned long tiempoAlarma = 5000;

long UltimaLectura[3] = {0, 0, 0};      // Temp, Hum, Dist
int Alarmes[3] = {0, 0, 0};             //Temp Hum Dist (en aquest ordre, els valors van de 0 (apagada) i 1(encesa))
int EstatFuncionamentSistemes[6] = {1, 1, 1, 1, 1, 0}; // Temp Hum Dist Alarmes Escombreig, MitjanesAlSatèl·lit     ||Tots encesos inicialment
int PeriodeEmisioDelsSistemes[4] = {500, 500, 500, 1000}; // Temp, Hum, Dist, Enviar dades

unsigned long NextMillis[4] = {0, 0, 0, 0};
int NumeroValorsMitjanes[3] = {1, 1, 1};

int ElementsUltimMissatge[4] = {0, 0, 0, 0};

// ----- Motor pas a pas -----
#define OUTPUT1   7   
#define OUTPUT2   6   
#define OUTPUT3   5   
#define OUTPUT4   4   

const int stepsPerRotation = 4779;
int VelMotor = 5;
int pos = 0;
int Sentit = 1;
int llargadaSteps = 1;

Stepper myStepper(stepsPerRotation, OUTPUT1, OUTPUT3, OUTPUT2, OUTPUT4);

// ----- Sensor ultrasons -----
const int EchoPin = 9;
const int TriggerPin = 3;

// ===============================================================
// SETUP
// ===============================================================
void setup() {
  Serial.begin(9600);
  mySerial.begin(9600);

  myStepper.setSpeed(VelMotor);

  pinMode(TriggerPin, OUTPUT);
  pinMode(EchoPin, INPUT);

  dht.begin();

  for (int i = 0; i < 4; i++) {
    NextMillis[i] = millis() + PeriodeEmisioDelsSistemes[i];
  }
}

// ===============================================================
// SENSORS
// ===============================================================



//CÀLCUL DE MITJANA DE TEMPERATURA I HUMITAT..............................................................
#define BUFFER_SIZE 10
float tempBuffer[BUFFER_SIZE];
float humBuffer[BUFFER_SIZE];
int tempIndex = 0;
int humIndex = 0;
bool tempFilled = false;
bool humFilled = false;

void updateBuffers(float temp, float hum) {
    tempBuffer[tempIndex] = temp;
    humBuffer[humIndex] = hum;

    tempIndex = (tempIndex + 1) % BUFFER_SIZE;
    humIndex = (humIndex + 1) % BUFFER_SIZE;

    if (tempIndex == 0) tempFilled = true;
    if (humIndex == 0) humFilled = true;
}

float mitjanaTemp() {
  if (EstatFuncionamentSistemes[5] == 1){
    int n = tempFilled ? BUFFER_SIZE : tempIndex;
    float sum = 0;
    for (int i=0; i<n; i++) sum += tempBuffer[i];
    return n > 0 ? sum / n : 0;
  }else{
    return 0;
  }
}

float mitjanaHum() {
  if (EstatFuncionamentSistemes[5] == 1){
    int n = humFilled ? BUFFER_SIZE : humIndex;
    float sum = 0;
    for (int i=0; i<n; i++) sum += humBuffer[i];
    return n > 0 ? sum / n : 0;

  } else{
    return 0;
  }
}

void processCommand(String cmd) { //Funció obsoleta, la seva funcionalitat es troba a Getinfo
    cmd.trim();
    if (cmd.startsWith("4;")) {
        // Format: 4;ID;10; (ID=0 temp, 1 hum)
        int first = cmd.indexOf(';');
        int second = cmd.indexOf(';', first+1);
        int third = cmd.indexOf(';', second+1);
        int ID = cmd.substring(first+1, second).toInt();

        float valorMitjana = 0;

        if (ID == 0)
          valorMitjana = mitjanaTemp();

        if (ID == 1) 
          valorMitjana = mitjanaHum();

        // Enviem al serial
        /*
        mySerial.print("MITJANA;");
        mySerial.print(ID);
        mySerial.print(";");
        mySerial.println(valorMitjana);
        */
    }
}
//............................................................................


float GetTemp() {
  if (millis() >= NextMillis[0] && EstatFuncionamentSistemes[0] == 1) {

    float t = dht.readTemperature();
    NextMillis[0] = millis() + PeriodeEmisioDelsSistemes[0];

    if (isnan(t)) return -1;

    Alarmes[0] = 0;
    UltimaLectura[0] = millis();
    return t;
  } else
  return 0;
}

float GetHum() {
  if (millis() >= NextMillis[1] && EstatFuncionamentSistemes[1] == 1) {

    float h = dht.readHumidity();
    NextMillis[1] = millis() + PeriodeEmisioDelsSistemes[1];

    if (isnan(h)) return -1;

    Alarmes[1] = 0;
    UltimaLectura[1] = millis();
    return h;
  }
  return 0;
}

int GetDist() {
  if (millis() >= NextMillis[2] && EstatFuncionamentSistemes[2] == 1) {

    // Pols ultrasònic
    digitalWrite(TriggerPin, LOW);
    delayMicroseconds(4);
    digitalWrite(TriggerPin, HIGH);
    delayMicroseconds(10);
    digitalWrite(TriggerPin, LOW);

    long duration = pulseIn(EchoPin, HIGH, 20000); // timeout 20ms

    NextMillis[2] = millis() + PeriodeEmisioDelsSistemes[2];

    //if (duration == 0) return -1;  // No hi ha eco

    int distCm = duration / 58;    // Fórmula correcta
    Alarmes[2] = 0;
    UltimaLectura[2] = millis();
    return distCm;
  }
  return 0;
}

// ===============================================================
// MOTOR
// ===============================================================
void MoureMotor() {
  if (EstatFuncionamentSistemes[4] == 1) {

    if (pos <= 0) Sentit = 1;
    else if (pos >= stepsPerRotation) Sentit = -1;

    myStepper.step(Sentit * llargadaSteps);
    pos += Sentit * llargadaSteps;
  }
}

// ===============================================================
// TELEMETRIA
// ===============================================================
void SendObservacions() {
  
  float hum = GetHum();
  float temp= GetTemp();
  int dist2 = GetDist();
  
  Serial.println("SendObs");
  mySerial.print("0;");
  mySerial.print(hum); 
  mySerial.print(":");
  mySerial.print(temp);
  mySerial.print(":");
  mySerial.print(pos); 
  mySerial.print(":");
  mySerial.print(dist2);
  mySerial.print(":");
  mySerial.print(mitjanaHum());
  mySerial.print(":");
  mySerial.print(mitjanaTemp());
  mySerial.print("\n");

}

void SendAlarm(int argument) {
  if (argument >= 0 && argument <= 2) {
    mySerial.print("1;");
    mySerial.println(argument);
  }
}

// ===============================================================
// PARSING DE MISSATGES
// ===============================================================
void GetInfo() {
  if (!mySerial.available()) return;

  data = mySerial.readStringUntil('\n');
  data.trim();

  Serial.print("Rebut: ");
  Serial.println(data);

  // Inicialitzar contingut
  for (int i = 0; i < 4; i++) ElementsUltimMissatge[i] = 0;

  // Parsing
  int idx = 0;
  int start = 0;
  int sep;

  while ((sep = data.indexOf(";", start)) != -1 && idx < 4) {
    ElementsUltimMissatge[idx] = data.substring(start, sep).toInt();
    start = sep + 1;
    idx++;
  }

  // Últim fragment
  if (idx < 4)
    ElementsUltimMissatge[idx] = data.substring(start).toInt();

  int accio = ElementsUltimMissatge[0];
  int argument = ElementsUltimMissatge[1];
  int valor1 = ElementsUltimMissatge[2];
  int valor2 = ElementsUltimMissatge[3];

  // ----- ORDRES -----
  if (accio == 2) {
    if (argument == 0)   EstatFuncionamentSistemes[valor1] = 0;      // STOP
    if (argument == 2)   EstatFuncionamentSistemes[valor1] = 1;      // START
    if (argument == 3)   PeriodeEmisioDelsSistemes[valor1] = valor2;   // Canvi freq
  }

  // ----- RADAR -----
  if (accio == 3) {
    if (argument == 0) llargadaSteps = valor1;  // Ajust pas motor
    if (argument == 2) pos = valor1;            // Reposicionar
  }

  // ----- MITJANES -----
  if (accio == 4) {
    if (argument == 0){ //Les mitjanes es calculen al satèl·lit
      EstatFuncionamentSistemes[5] = 1;
      //NumeroValorsMitjanes[argument] = valor1;        
    } else if (argument == 1){
      EstatFuncionamentSistemes[5] = 0;
    }


  }
}

// ===============================================================
// LOOP PRINCIPAL
// ===============================================================
void loop() {

  MoureMotor();
  GetInfo();
  if (millis() >= NextMillis[3]){
    SendObservacions();
    NextMillis[3]=millis()+1000;
  }

  // CONTROL D’ALARMES
  if (EstatFuncionamentSistemes[3] == 1) {
    for (int i = 0; i < 3; i++) {
      if (Alarmes[i] == 0 && millis() - UltimaLectura[i] > tiempoAlarma) {
        Alarmes[i] = 1;
        SendAlarm(i);
        Serial.println("ALERTA SISTEMA " + String(i));
      }
    }
  }
}
