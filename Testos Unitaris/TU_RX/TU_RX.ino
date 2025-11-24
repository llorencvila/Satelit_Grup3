#include <SoftwareSerial.h>
SoftwareSerial mySerial(10, 11); // RX, TX (azul, naranja)

void setup() {
   Serial.begin(9600);
   mySerial.begin(9600);
}
void loop() {
  if (mySerial.available()) {
      String data = mySerial.readString();
      Serial.print(data);

  } 
}