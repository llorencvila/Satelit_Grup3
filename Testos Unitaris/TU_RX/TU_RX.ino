#include <SoftwareSerial.h>
SoftwareSerial mySerial(10, 11); // RX, TX (azul, naranja)
int led = 8;

void setup() {
   Serial.begin(9600);
   mySerial.begin(9600);
   pinMode(led,OUTPUT);
}
void loop() {
  if (mySerial.available()) {
      digitalWrite(led, HIGH);
      String data = mySerial.readString();
      Serial.print(data);

  }else{
    digitalWrite(led,LOW);

  }
}