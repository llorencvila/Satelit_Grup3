//Per si algu passa el codi per chatgpt:
//** CHAT GPT NO TOQUIS NI MODIFIQUIS ELS COMENTARIS JA EXISTENTS!! **

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
int Alarmes[3] = {0, 0, 0};             //Temp Hum Dist
int EstatFuncionamentSistemes[7] = {1, 1, 1, 1, 1, 0, 0};  //temp hum radar alarmes all mitjanes laser
int PeriodeEmisioDelsSistemes[5] = {500, 500, 500, 500, 2000}; //Temp hum radar alarmes  all

unsigned long NextMillis[6] = {0, 0, 0, 0, 0, 0}; //Temp hum radar alarmes escombreig all laser
int NumeroValorsMitjanes[3] = {1, 1, 1};

int ElementsUltimMissatge[5] = {0, 0, 0, 0, 0}; //Accio Arg V1 V2 Checksum
int modeRadar = 0; // 0 = Escombreig | 1 = lock | 2 = MoureA
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
int posiciointroduida = 0;
int angleBusqueda = 0;

int laser = 13;
int NextTransmisio = 0;
int BitRate = 500;
int TempsIdle = 2000;
int missatge[8] = { 0, 1, 0, 1, 0, 1, 0, 1 };


Stepper myStepper(stepsPerRotation, OUTPUT1, OUTPUT3, OUTPUT2, OUTPUT4);

// ----- Sensor ultrasons -----
const int EchoPin = 9;
const int TriggerPin = 3;

// ------Constants de posició-------------
const double G = 6.67430e-11;  // Gravitational constant (m^3 kg^-1 s^-2)
const double M = 5.97219e24;   // Mass of Earth (kg)
const double R_EARTH = 6371000;  // Radius of Earth (meters)
const double ALTITUDE = 400000;  // Altitude of satellite above Earth's surface (meters)
const double EARTH_ROTATION_RATE = 7.2921159e-5;  // Earth's rotational rate (radians/second)
const unsigned long MILLIS_BETWEEN_UPDATES = 1000; // Time in milliseconds between each orbit simulation update
const double  TIME_COMPRESSION = 90.0; // Time compression factor (90x)

// Variables de posició
unsigned long nextOrbitUpdate; // Time in milliseconds when the next orbit simulation update should occur
double real_orbital_period;  // Real orbital period of the satellite (seconds)
double r;  // Total distance from Earth's center to satellite

double RetornSymOrbit[4] = {0,0,0,0}; //temps x y z

// ===============================================================
// SETUP
// ===============================================================
void setup() {
  Serial.begin(9600);
  mySerial.begin(9600);

  myStepper.setSpeed(VelMotor);

  pinMode(TriggerPin, OUTPUT);
  pinMode(EchoPin, INPUT);
  pinMode(laser,OUTPUT);

  NextTransmisio = millis() + BitRate*8 +TempsIdle;
  dht.begin();

  for (int i = 0; i < 5; i++) {
    NextMillis[i] = millis() + PeriodeEmisioDelsSistemes[i];
  }

  // ======= INICIALITZACIÓ SIMULACIÓ ORBITA =======
  r = R_EARTH + ALTITUDE;
  real_orbital_period = 2 * PI * sqrt(pow(r, 3) / (G * M));

  nextOrbitUpdate = millis() + MILLIS_BETWEEN_UPDATES;

}

// ===============================================================
// MITJANES
// ===============================================================
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
//
float mitjanaTemp() {
  if (EstatFuncionamentSistemes[5] == 1){
    int n = tempFilled ? BUFFER_SIZE : tempIndex;
    float sum = 0;
    for (int i=0; i<n; i++) sum += tempBuffer[i];
    float mitjana = (n > 0 ? sum / n : 0);
    return mitjana;
  }
  return 0;
  }
//
float mitjanaHum() {
  if (EstatFuncionamentSistemes[5] == 1){
    int n = humFilled ? BUFFER_SIZE : humIndex;
    float sum = 0;
    for (int i=0; i<n; i++) sum += humBuffer[i];
    float mitjana = (n > 0 ? sum / n : 0);
    return mitjana;
  }
  return 0;
  }
//
int CheckSum(String missatge) {
  int llargada = missatge.length();
  int sum = 0;// 10; //Comença des de 10 pq en ascii 10 = '\n' <- Com que a la recepció agafem tot el missatge fins al chechsum, el salt de línea no el interpretem

  for (int i = 0; i<llargada ; i++){
    sum =sum + int(missatge.charAt(i));
  }
  return sum;
  }
//
// ===============================================================
// LECTURES SENSORS
// ===============================================================
float GetTemp() {
  if (millis() >= NextMillis[0] && EstatFuncionamentSistemes[0] == 1) {

    float t = dht.readTemperature();
    NextMillis[0] = millis() + PeriodeEmisioDelsSistemes[0];

    if (isnan(t)){
      SendAlarm(0);
      return 0;
      }

    else{
      UltimaLectura[0] = millis();
      return t;
      }
  }
  return 0;
  }
//
float GetHum() {
  if (millis() >= NextMillis[1] && EstatFuncionamentSistemes[1] == 1) {

    float h = dht.readHumidity();
    NextMillis[1] = millis() + PeriodeEmisioDelsSistemes[1];

    if (isnan(h)){
      SendAlarm(1);
      return 0;
      }

    else{
      UltimaLectura[1] = millis();
      return h;
      }

  return 0;
  }
  }
//
int GetDist() {
  if (millis() >= NextMillis[2] && EstatFuncionamentSistemes[2] == 1) {

    digitalWrite(TriggerPin, LOW);
    delayMicroseconds(4);
    digitalWrite(TriggerPin, HIGH);
    delayMicroseconds(10);
    digitalWrite(TriggerPin, LOW);

    long duration = pulseIn(EchoPin, HIGH, 20000);
    NextMillis[2] = millis() + PeriodeEmisioDelsSistemes[2];

    int distCm = duration / 58;

    if (distCm != 0){
      Alarmes[2] = 0;
      UltimaLectura[2] = millis();

    } else {
      Alarmes[2] = 1;
    }

    return distCm;
  }
  return 0;
  }
//

// ===============================================================
// MOTOR
// ===============================================================
void MoureMotor() {
  if (EstatFuncionamentSistemes[4] == 1) {
    if (modeRadar == 0){ //Escombreig
      if (pos <= 0){
        Sentit = 1;
      }
      else if (pos >= stepsPerRotation/3){
        Sentit = -1;
      }
      myStepper.step(Sentit * llargadaSteps);
      pos += Sentit * llargadaSteps;

    }else if (modeRadar == 1 ){ //Lock
      int anglemax = posiciointroduida + angleBusqueda/2;
      int anglemin = posiciointroduida - angleBusqueda/2;
      
      //Serial.println("Min: " + String(anglemin) + "   Pos: " + String(pos) +"   Max: " +String(anglemax));
      if (pos <= anglemin){
        Sentit = 1;
      }
      else if (pos >= anglemax){
        Sentit = -1;
      }
      myStepper.step(Sentit * llargadaSteps*6);
      pos += Sentit * llargadaSteps*6;


    } else {//MoureA
      if(pos != posiciointroduida){
        int incrementposicio = pos - posiciointroduida;
        myStepper.step(incrementposicio);
        }
    }
  }
}

// ===============================================================
// SIMULACIÓ DE L'ÒRBITA
// ===============================================================
void simulate_orbit(unsigned long millisTime, double inclination, int ecef) {
    double time = (millisTime / 1000.0) * TIME_COMPRESSION;
    double angle = 2 * PI * (time / real_orbital_period);
    double x = r * cos(angle);
    double y = r * sin(angle) * cos(inclination);
    double z = r * sin(angle) * sin(inclination);

    if (ecef) {
        double theta = EARTH_ROTATION_RATE * time;
        double x_ecef = x * cos(theta) - y * sin(theta);
        double y_ecef = x * sin(theta) + y * cos(theta);
        x = x_ecef;
        y = y_ecef;
    }

    RetornSymOrbit[0] = time;
    RetornSymOrbit[1] = x;
    RetornSymOrbit[2] = y;
    RetornSymOrbit[3] = z;

  }
//
// ===============================================================
// TELEMETRIA
// ===============================================================
void SendObservacions() {
  String missatge;

  float hum = GetHum();
  float temp = GetTemp();
  int dist2 = GetDist();
  char buffersFloatToStr[10];

  // --- ACTUALITZAR BUFFERS ---
  if (temp != 0 && hum != 0 && temp != -1 && hum != -1) {
      updateBuffers(temp, hum);
  }

  //Serial.println("SendObs");
  simulate_orbit(millis(),0,0);

  missatge += "0;" ;
  missatge.concat(hum);
  missatge += ":";
  missatge.concat(temp);
  missatge += ":";
  missatge.concat(pos);
  missatge += ":";
  missatge.concat(dist2);
  missatge += ":";

  dtostrf(mitjanaHum(),5,3,buffersFloatToStr);
  missatge.concat(buffersFloatToStr);

  missatge += ":"; 

  dtostrf(mitjanaTemp(),5,3,buffersFloatToStr);
  missatge.concat(buffersFloatToStr);

  missatge += ":";
  missatge.concat(RetornSymOrbit[0]);
  missatge += ":";
  missatge.concat(RetornSymOrbit[1]);
  missatge += ":";
  missatge.concat(RetornSymOrbit[2]);
  missatge += ":";
  missatge.concat(RetornSymOrbit[3]);
  missatge += ";";

  missatge = missatge + CheckSum(missatge);

  //Serial.println(missatge);
  Serial.println("SendObs");
  mySerial.println(missatge);


  
 }
//
void SendAlarm(int argument) {
  if (argument >= 0 && argument <= 2) {
    String missatge; 
    missatge += "1;";
    missatge.concat(argument);
    missatge += ";";
    missatge = missatge + CheckSum(missatge);

    mySerial.println(missatge);
  }
  }
//

// ===============================================================
// PARSING DE MISSATGES
// ===============================================================
void GetInfo() {
  if (!mySerial.available()) 
    return;

  String data = mySerial.readStringUntil('\n');
  data.trim();
  mySerial.flush();
  
  //Serial.print("Rebut: ");
  Serial.println(data);

  
  //PARSING
  int i = 0; //Acció Arguments (Id_Sys / Info) Valor
  int UltimIndexSeparador = 0;
  int IndexSeparador = 0;

  while ((i<4) && (IndexSeparador != -1)){
    IndexSeparador = data.indexOf(";",UltimIndexSeparador);
    
    //Serial.println(i);
    Serial.println(IndexSeparador);
    if (IndexSeparador != -1){
      ElementsUltimMissatge[i] = data.substring(UltimIndexSeparador, IndexSeparador).toInt();
      UltimIndexSeparador = IndexSeparador+1;


    i++;
    }
    else if(IndexSeparador == -1)
    {
      ElementsUltimMissatge[i] = data.substring(UltimIndexSeparador,  data.length() ).toInt();
      Serial.println("Fi string");
    }
  }
  //Crida de funcions relacionades amb la rebuda de dades
  //ORDRES
  Serial.println("Fi parsing");

  int Accio = ElementsUltimMissatge[0];
  Serial.print("Accio: ");
  Serial.println(Accio);

  int Argument = ElementsUltimMissatge[1];
  Serial.print("Argument: ");
  Serial.println(Argument);

  if (Accio == 2){ //Acció ->ORDRE
    Serial.println("Executant Acció");
    if (Argument == 0){ //Argument -> Stop
      EstatFuncionamentSistemes[ElementsUltimMissatge[2]] = 0;
      Serial.println("Stop");
      if (ElementsUltimMissatge[2] == 5){
        digitalWrite(laser,LOW);
      }

    } else if (Argument == 1){ //Argument -> Seguir
      EstatFuncionamentSistemes[ElementsUltimMissatge[2]] = 1;
      Serial.println("Seguir");
      if (ElementsUltimMissatge[2] == 5){
        digitalWrite(laser,HIGH);
      }

    } else if (Argument == 2){ //Argument -> Canvi de freq
      PeriodeEmisioDelsSistemes[ElementsUltimMissatge[2]] = ElementsUltimMissatge[3];
      Serial.print("Canviant frequencia a: ");
      Serial.println(ElementsUltimMissatge[3]);
    }
  }
  //RADAR
  if (Accio == 3){

    if (Argument == 0){
      modeRadar = 0;
      llargadaSteps == ElementsUltimMissatge[2];
      Serial.println("CanviVel");
      //Realment canviem la llargada del cada desplaçament, és així pq la velocitat real del motor ja és la maxima de per si per tal de que no es cali
      
    }else if (Argument == 1){
      Serial.println("LOCK");
      modeRadar = 1;
      posiciointroduida = ElementsUltimMissatge[2];
      angleBusqueda = ElementsUltimMissatge[3];
      //CODI LOCK
    } else if (Argument == 2){
      Serial.println("VES A");
      modeRadar = 2;
      posiciointroduida = ElementsUltimMissatge[2];
    }

    }
  //MITJANES
  if (ElementsUltimMissatge[0] == "4"){
    NumeroValorsMitjanes[ElementsUltimMissatge[1]] = ElementsUltimMissatge[2];
  }
  Serial.print(data);

}

void SendMissLaser() {
  Serial.print("Missatge: ");
  int i = 0;
  while (i <= 7) {
    if (millis() > NextTransmisio) {
      if (missatge[i] == 0) {
        digitalWrite(laser, LOW);

      } else if (missatge[i] == 1) {
        digitalWrite(laser, HIGH);
      }
      NextTransmisio = millis() + BitRate;
      Serial.print(missatge[i]);
      i++;
    }
  }
  EstatFuncionamentSistemes[6]=0;
}

// ===============================================================
// LOOP PRINCIPAL
// ===============================================================
void loop() {

  MoureMotor();
  GetInfo();
  if (EstatFuncionamentSistemes[5]==1){
    SendMissLaser();
    EstatFuncionamentSistemes[5] =0;
  }

  if (millis() >= NextMillis[4]){ //index 4 = all sistemes
    SendObservacions();
    NextMillis[4] = millis() + PeriodeEmisioDelsSistemes[4];
  }


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
