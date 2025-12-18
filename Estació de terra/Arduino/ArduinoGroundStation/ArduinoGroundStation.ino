#include <SoftwareSerial.h>
SoftwareSerial mySerial(10, 11);  // RX, TX (azul, naranja)
String data;

const int LedIdle = 12;
const int LedMirall = 5;
const int LedMissatge = 10;

const int LDRPin = A0;
const float umbralDetecio = 1.25;  //Es considerarà com a detecció quan els valors sobrepassin aquest tan percert del valor base

int NumRep = 0;
int TempsRebudaMissHigh = 0;
int TempsRebudaMissLow = 0;

int BaudRate = 1000;
int EstatMissatge = 0;  //0=Idle | 1=Startbit | 2=LlegintMissatge

int UmbralIdle = 1500;
int UmbralLDR = -1;
int LastIsidle = 0;
int IsIdleNow = 0;

long TIniciCrono;
long TempsRebuda;
long TempsRebudaStartbit = 0;
long nextMillis = 0;
long TDetecioIdle;
int timeout;

int laserOn =0;

int missatge[8];
int LlargadaMissatge = 0;

int lastInput;
int input;


int ElementsUlitmMissatge[4];  //Acció Arguments (Id_Sys / Info) Valor || Llista d'elements que pot tenir l'ulitm missatge, CONSULTAR EXCEL PROTOCOL BITS en cas de dubte

void calibracio() {
  Serial.println("Entrem a calibració");
  int primer = 1;
  int intents = 0;

  while ((UmbralLDR < 0 || UmbralLDR > 1000) && intents < 3) {  //Si el umbral és superior al valor màxim que pot agafar el sensor
    int sum = 0;
    int i = 0;
    intents++;
    //Serial.println(intents);
    //Serial.println("Prenent mitjana");
    nextMillis = millis() + 1000;

    while (millis() < nextMillis) {  //S'està 1 seg prenent valors
      sum = sum + analogRead(LDRPin);
      //Serial.println(analogRead(LDRPin));
      i++;
      delay(75);
    }

    int background = sum / i;  //Agafem com a background la mitjana dels valors de llum que es prenen durant

    if (intents < 3) {
      UmbralLDR = background * umbralDetecio;

      primer = 0;
    } else {
      UmbralLDR = 800;
    }
    //Serial.println("Umbral: " + String(UmbralLDR));
  }
}

int CanviEstat(int Vi, int Vf) {  //Valor inicial i valor final
  //El Vf mai es farà servir, tot i aixo el deixo perque crec que dona claredat a l'hoara de cridar la funció

  if (Vi == 0) {
    if (lastInput <= UmbralLDR && input >= UmbralLDR) {  //0->1
      TempsRebuda = millis();
      digitalWrite(LedMirall, HIGH);
      //Serial.print("1");
      return 1;
    } else {
      return 0;
    }
  }
  if (Vi == 1) {
    if (lastInput >= UmbralLDR && input <= UmbralLDR) {  //1->0
      TempsRebuda = millis();
      digitalWrite(LedMirall, LOW);
      //Serial.print("0");
      return 1;
    } else {
      return 0;
    }
  }
}


void setup() {
  Serial.begin(9600);
  mySerial.begin(9600);
  pinMode(5, OUTPUT);
  pinMode(6, OUTPUT);
  calibracio();
}
void loop() {
  lastInput = input;
  input = analogRead(LDRPin);

  if (mySerial.available()) {
    data = mySerial.readString();
    data.trim();  //elimina tots els caràcters que no siguin lletres. Essencial per poder fer els if's seguents
    Serial.println(data);
  }
  if (Serial.available()) {  //agafa les i
    String dataPc = Serial.readString();
    digitalWrite(8, HIGH);

    mySerial.println(dataPc);

  } else {
    digitalWrite(8, LOW);
  }
  if (CanviEstat(1,0)){
    timeout = millis() + 5000;
    laserOn = 1;
  }
  if ((millis()>timeout)&& laserOn ==1){
    Serial.println("1;8;223");
    timeout = millis()+5000;
  }
}
