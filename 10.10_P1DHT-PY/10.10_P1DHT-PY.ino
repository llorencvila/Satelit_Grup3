#include "DHT.h"
#include <Wire.h> 
#include <SoftwareSerial.h>
SoftwareSerial mySerial(10, 11); // RX, TX (azul, naranja)
unsigned long nextMillis = 500;

#define DHTTYPE DHT11   // DHT 11
const int DHTPin = 5;   


DHT dht(DHTPin, DHTTYPE);
void setup(){
  Serial.begin(9600);

  mySerial.begin(9600);
  dht.begin();

}

void loop() {

  delay(1000);
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
  }


}



