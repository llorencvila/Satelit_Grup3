#include "DHT.h"
#include <Wire.h> 



#define DHTTYPE DHT11   // DHT 11
const int DHTPin = 5;   

DHT dht(DHTPin, DHTTYPE);
void setup(){
  Serial.begin(9600);
  Serial.println("DHTxx test!");

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
    Serial.println("DHT 11: Nominal  ");
  }


}
