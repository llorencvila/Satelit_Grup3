#include <SoftwareSerial.h>
SoftwareSerial mySerial(10, 11); // RX, TX (azul, naranja)
//unsigned long nextMillis = 500;


void setup() {
  Serial.begin(9600);
  Serial.println("Inici del test unitari");
  mySerial.begin(9600);
  mySerial.print("ping");
}
void loop() {

  if (mySerial.available()) {
    String data = mySerial.readString();
    Serial.print("L'altre arduino envia: ");
    Serial.println(data);
    mySerial.print("Pong!");

   }else{
    mySerial.print("Ping!");
    Serial.println("ping");
   }
}

