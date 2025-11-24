#include <SoftwareSerial.h>
int i;
SoftwareSerial mySerial(10, 11); // RX, TX 
void setup() {
   Serial.begin(9600);
   mySerial.begin(9600);
   mySerial.println("Empezamos");
   i=1;
}
void loop() {
   delay (5000);
   mySerial.print("Envio: ");
   mySerial.println(i);
   Serial.print("Envio: ");
   Serial.println(i);
   i=i+1;
}