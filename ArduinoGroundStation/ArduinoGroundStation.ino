#include <SoftwareSerial.h>
SoftwareSerial mySerial(10, 11);  // RX, TX (azul, naranja)
unsigned long nextMillis = 500;

void setup() {
  Serial.begin(9600);
  mySerial.begin(9600);
}
void loop() {
  if (mySerial.available()) {
    String data = mySerial.readString();
    Serial.print(data);
  }

  if (Serial.available()) {
    String dataPc = Serial.readString();
    if (dataPc == "STOP") {
      mySerial.println("STOP");

    } else if (dataPc == "REANUDAR") {
      mySerial.println("REANUDAR");
    }
  }
}
