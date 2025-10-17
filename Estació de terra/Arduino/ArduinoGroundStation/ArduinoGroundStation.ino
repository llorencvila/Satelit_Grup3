#include <SoftwareSerial.h>
SoftwareSerial mySerial(10, 11);  // RX, TX (azul, naranja)


void setup() {
  Serial.begin(9600);
  mySerial.begin(9600);
  pinMode(13, OUTPUT);
}
void loop() {
  
  if (mySerial.available()) { //llegeix les dades del satel·lit i les fica a l'ordinador
    String dataSat = mySerial.readString();
    Serial.print(dataSat);
      if (dataSat == "FALLO"){
        digitalWrite(13, HIGH);
      }
  } 

  if (Serial.available()) { //agafa les instruccions del pc i les envia al satel·lit
    String dataPc = Serial.readString();
    if (dataPc == "STOP") {
      mySerial.println("STOP");
      digitalWrite(5,HIGH);
    } else if (dataPc == "REANUDAR") {
      mySerial.println("REANUDAR");
      digitalWrite(5,LOW);
    }
  }
  
}