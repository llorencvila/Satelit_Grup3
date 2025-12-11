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
    /*
    //PARSING
    int i = 0; //Acció Arguments (Id_Sys / Info) Valor
    int UltimIndexSeparador = 0;
    int IndexSeparador;
    
    while (i<4 || IndexSeparador != -1){
      IndexSeparador = data.indexOf(";");

      if (IndexSeparador != -1){
        ElementsUlitmMissatge[i] = data.substring(UltimIndexSeparador, IndexSeparador).toInt();
        UltimIndexSeparador = IndexSeparador+1;
      i++;
      }
    }

    if (ElementsUlitmMissatge[1] == "1") { //Si es rep una alarma, independentment de quina
      digitalWrite(5, HIGH);
    } else{
      digitalWrite(5, LOW);  
    }

  */
  }
  if (Serial.available()) {  //agafa les i
    String dataPc = Serial.readString();
    digitalWrite(8, HIGH);

    mySerial.println(dataPc);
    //Serial.println(dataPc);
    /*
    if (dataPc == "STOP") {
      mySerial.println("STOP");
    } else if (dataPc == "REANUDAR") {
      mySerial.println("REANUDAR");
    }
    */
  } else {
    digitalWrite(8, LOW);
  }
}
