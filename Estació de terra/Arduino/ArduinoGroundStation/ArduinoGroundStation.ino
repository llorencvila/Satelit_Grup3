#include <SoftwareSerial.h>
SoftwareSerial mySerial(10, 11);  // RX, TX (azul, naranja)


void setup() {
  Serial.begin(9600);
  mySerial.begin(9600);
  pinMode(5, OUTPUT);
}
void loop() {

  if (mySerial.available()) {  //llegeix les dades del satel·lit i les fica a l'ordinador
    String dataSat = mySerial.readString();
    dataSat.trim();
    Serial.println(dataSat);
    if (dataSat == "FALLO") {
      digitalWrite(5, HIGH);
    } else{
      digitalWrite(5, LOW);  
    }
  }

  if (Serial.available()) {  //agafa les instruccions del pc i les envia al satel·lit
    String dataPc = Serial.readString();
    if (dataPc == "STOP") {
      mySerial.println("STOP");
    } else if (dataPc == "REANUDAR") {
      mySerial.println("REANUDAR");
    }
  }
}