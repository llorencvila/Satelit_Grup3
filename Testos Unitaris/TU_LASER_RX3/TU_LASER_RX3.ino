int TempsRebuda;
int UmbralIdle;

int LastIsidle = 0;
int IsIdle = 0;

int CanviEstat(int Vi, int Vf){ //Valor inicial i valor final
  //El Vf mai es farà servir, tot i aixo el deixo perque crec que dona claredat a l'hoara de cridar la funció
  
  if (Vi == 0){
    if (lastInput<umbral && input>umbral){ //0->1
      TempsRebuda = millis();
      digitalWrite(LEDPin,HIGH);
      return 1;
    }
  }else if(Vi == 1) {
    if (lastInput>umbral && input<umbral){ //1->0
      TempsRebuda = millis();
      digitalWrite(LEDPin,HIGH);
      return 1;
    }
  }
}

int IsIdle(){
  CanviEstat(0,1);
  if (millis()>(millis-TempsRebuda)){
    return 1;
  }
}

int IsStartBit(){
  LastIsidle = IsIdle;
  IsIdle = IsIdle();
  if (LastIsidle==1 && input<umbral){ //1->0
    TempsRebuda = millis();
    digitalWrite(LEDPin,HIGH);
    return 1;
  }
}


void setup() {
  // put your setup code here, to run once:

}

void loop() {

}
