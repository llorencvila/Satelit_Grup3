#include "DHT.h"
#include <Wire.h> 
#include <SoftwareSerial.h>

SoftwareSerial mySerial(10, 11); // RX, TX (azul, naranja)
int interval = 1000;
String data;
unsigned long NextMillis;

#define DHTTYPE DHT11   // DHT 11
const int DHTPin = 5;   


DHT dht(DHTPin, DHTTYPE);

unsigned long lastDHTMillis = 0;     // Guarda el último momento de lectura válida
unsigned long tiempoAlarma = 5000;  
bool alarmaActiva = false;           

void setup(){
  Serial.begin(9600);

  mySerial.begin(9600);
  dht.begin();

  NextMillis = millis()+interval;

  }
void DHTSendData(){
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

void loop() {
  if (mySerial.available()) {
    data = mySerial.readString();
    data.trim(); //elimina tots els caràcters que no siguin lletres. Essencial per poder fer els if's seguents
    Serial.print(data);
    }

  if (data == "REANUDAR" || data == "INICIAR"){
    if (millis() >=NextMillis){
      DHTSendData();
      NextMillis = millis()+interval;
      }
    } else if (data == "STOP"){
      Serial.println("Parant");
    } else{
      Serial.println("Sense_Dades");
    }

    if ((millis() - lastDHTMillis) > tiempoAlarma && !alarmaActiva) {
      Serial.println("FALLO");
      mySerial.println("FALLO");
      alarmaActiva = true;  
    }
  }





