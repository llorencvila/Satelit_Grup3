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
int EstatFuncionamentSistemes[6] = {1, 1, 1, 1, 1, 0}; 
int PeriodeEmisioDelsSistemes[4] = {500, 500, 500, 1000};

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

// ===============================================================
// LECTURES SENSORS
// ===============================================================
float GetTemp() {
  if (millis() >= NextMillis[0] && EstatFuncionamentSistemes[0] == 1) {

    float t = dht.readTemperature();
    NextMillis[0] = millis() + PeriodeEmisioDelsSistemes[0];

    if (isnan(t)) return -1;

    Alarmes[0] = 0;
    UltimaLectura[0] = millis();
    return t;
  }
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

    digitalWrite(TriggerPin, LOW);
    delayMicroseconds(4);
    digitalWrite(TriggerPin, HIGH);
    delayMicroseconds(10);
    digitalWrite(TriggerPin, LOW);

    long duration = pulseIn(EchoPin, HIGH, 20000);
    NextMillis[2] = millis() + PeriodeEmisioDelsSistemes[2];

    int distCm = duration / 58;
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

    Serial.print("Orbit | t=");
    Serial.print(time);
    Serial.print("s  X=");
    Serial.print(x);
    Serial.print("  Y=");
    Serial.print(y);
    Serial.print("  Z=");
    Serial.println(z);
  
  return time
  return x
  return y
  return z
}


// ===============================================================
// TELEMETRIA
// ===============================================================
void SendObservacions() {
  
  float hum = GetHum();
  float temp = GetTemp();
  int dist2 = GetDist();
  float time = simulate_orbit(time);
  float time = simulate_orbit(x);
  float time = simulate_orbit(y);
  float time = simulate_orbit(z);

  // --- ACTUALITZAR BUFFERS ---
  if (temp != 0 && hum != 0 && temp != -1 && hum != -1) {
      updateBuffers(temp, hum);
  }

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
  mySerial.print(":");

  //dades de la òrbita
  mySerial.print(time);
  mySerial.print(:);
  mySerial.print(x);
  mySerial.print(:);
  mySerial.print(y);
  mySerial.print(:);
  mySerial.println(z);
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

  for (int i = 0; i < 4; i++) ElementsUltimMissatge[i] = 0;

  int idx = 0;
  int start = 0;
  int sep;

  while ((sep = data.indexOf(";", start)) != -1 && idx < 4) {
    ElementsUltimMissatge[idx] = data.substring(start, sep).toInt();
    start = sep + 1;
    idx++;
  }

  if (idx < 4)
    ElementsUltimMissatge[idx] = data.substring(start).toInt();

  int accio = ElementsUltimMissatge[0];
  int argument = ElementsUltimMissatge[1];
  int valor1 = ElementsUltimMissatge[2];
  int valor2 = ElementsUltimMissatge[3];

  if (accio == 2) {
    if (argument == 0)   EstatFuncionamentSistemes[valor1] = 0;
    if (argument == 2)   EstatFuncionamentSistemes[valor1] = 1;
    if (argument == 3)   PeriodeEmisioDelsSistemes[valor1] = valor2;
  }

  if (accio == 3) {
    if (argument == 0) llargadaSteps = valor1;
    if (argument == 2) pos = valor1;
  }

  if (accio == 4) {
    if (argument == 0){
      EstatFuncionamentSistemes[5] = 1;
    } 
    else if (argument == 1){
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

  // ======= ACTUALITZAR SIMULACIÓ ORBITA =======
  if (millis() >= nextOrbitUpdate) {
    simulate_orbit(millis(), 0.1, 1);  // inclinació 0.1 rad, ECEF = true
    nextOrbitUpdate = millis() + MILLIS_BETWEEN_UPDATES;
  }


  if (millis() >= NextMillis[3]){
    SendObservacions();
    NextMillis[3] = millis() + 1000;
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

