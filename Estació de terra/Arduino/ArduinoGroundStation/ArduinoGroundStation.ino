#include <SoftwareSerial.h>
SoftwareSerial mySerial(10, 11);  // RX, TX (azul, naranja)
String data;

int ElementsUlitmMissatge[4];  //Acció Arguments (Id_Sys / Info) Valor || Llista d'elements que pot tenir l'ulitm missatge, CONSULTAR EXCEL PROTOCOL BITS en cas de dubte


void setup() {
  Serial.begin(9600);
  mySerial.begin(9600);
  pinMode(5, OUTPUT);
  pinMode(8, OUTPUT);
}
void loop() {

  if (mySerial.available()) {
    data = mySerial.readString();
    data.trim();  //elimina tots els caràcters que no siguin lletres. Essencial per poder fer els if's seguents
    Serial.println(data);
   
  }
  if (Serial.available()) {  //agafa les i
    String dataPc = Serial.readString();
    digitalWrite(8, HIGH);

    mySerial.println(dataPc);

  } else {
    digitalWrite(8, LOW);
  }
}
